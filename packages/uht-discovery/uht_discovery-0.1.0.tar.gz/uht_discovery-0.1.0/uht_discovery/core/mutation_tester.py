#!/usr/bin/env python3

import sys, os, logging, yaml, subprocess, random, re
from pathlib import Path

import torch, esm
from tqdm import tqdm
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

import numpy as np
import pandas as pd
import csv
import math

def load_config(config_path="config.yaml"):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    for key in (
        "mutation_tester_project_directory",
        "max_sequences_to_denoise_mutation_tester",
        "selected_sequence_mutation_tester",
        "max_hamming_mutation_tester",
    ):
        if key not in cfg:
            raise KeyError(f"Missing required config key: {key}")
    return cfg

def setup_logging(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = output_dir / "pipeline.log"
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(str(log_file)); fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout); ch.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(fmt); ch.setFormatter(fmt)
    logger.addHandler(fh); logger.addHandler(ch)
    logging.info("Logging to %s", log_file)

def get_fasta_sequences(input_dir: Path, max_length=3000):
    seqs = []
    for fasta in input_dir.glob("*.fasta"):
        for rec in SeqIO.parse(str(fasta), "fasta"):
            if len(rec.seq) <= max_length:
                seqs.append(rec)
            else:
                logging.debug("Skipping %s (len %d > %d)", rec.id, len(rec.seq), max_length)
    if not seqs:
        logging.error("No sequences ≤ %d aa found in %s", max_length, input_dir)
        sys.exit(1)
    logging.info("Loaded %d sequences (≤ %d aa)", len(seqs), max_length)
    return seqs

def compute_nll_scores(records, model, batch_converter, device, batch_size=16, pbar=None):
    model.eval()
    pad_idx = batch_converter.alphabet.padding_idx
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        labels, seqs, toks = batch_converter([(r.id, str(r.seq)) for r in batch])
        toks = toks.to(device)
        with torch.no_grad():
            out = model(toks, repr_layers=[], return_contacts=False)
        lps = torch.log_softmax(out["logits"], dim=-1)
        tp = lps.gather(2, toks.unsqueeze(-1)).squeeze(-1)
        mask = (toks != pad_idx)
        raw = -(tp * mask).sum(dim=1).cpu().numpy()
        lengths = mask.sum(dim=1).cpu().numpy()
        norm = raw / lengths
        for (hdr, seq), score in zip([(r.id, str(r.seq)) for r in batch], norm):
            compute_nll_scores.nlls[hdr] = (seq, float(score))
        if pbar:
            pbar.update(1)
    return compute_nll_scores.nlls

compute_nll_scores.nlls = {}

def write_nll_csv(nll_scores, out_path: Path):
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Header", "Sequence", "Normalized_NLL"])
        for hdr, (seq, nll) in nll_scores.items():
            w.writerow([hdr, seq, nll])
    logging.info("Wrote NLL scores to %s", out_path)

def select_reference(nll_scores, selected_substr=None):
    hdrs = list(nll_scores)
    if selected_substr:
        for h in hdrs:
            if selected_substr in h:
                logging.info("Using specified reference '%s'", h)
                return h
        logging.warning("'%s' not found; picking lowest NLL", selected_substr)
    ref = min(nll_scores.items(), key=lambda x: x[1][1])[0]
    logging.info("Picked reference by lowest NLL: '%s'", ref)
    return ref

def apply_event(seq: str, ev: tuple):
    typ, pos = ev[0], ev[1] - 1
    if typ == "sub":
        return seq[:pos] + ev[3] + seq[pos+1:]
    if typ == "ins":
        return seq[:pos] + ev[2] + seq[pos:]
    if typ == "del":
        L = len(ev[2])
        return seq[:pos] + seq[pos+L:]
    raise ValueError("Unknown event")

def parse_variant_string(variant: str):
    variant = variant.encode("ascii", "ignore").decode().strip()
    if variant.upper() == "WT":
        return []
    events = []
    for part in variant.split("+"):
        p = part.strip()
        m = re.match(r"^(\d+)ins([A-Za-z]+)$", p)
        if m:
            events.append(("ins", int(m.group(1)), m.group(2))); continue
        m = re.match(r"^([A-Za-z]*)(\d+)del$", p)
        if m:
            seq, pos = m.group(1), int(m.group(2))
            events.append(("del", pos, seq)); continue
        m = re.match(r"^([A-Za-z])(\d+)([A-Za-z])$", p)
        if m:
            events.append(("sub", int(m.group(2)), m.group(1), m.group(3))); continue
        raise ValueError(f"Unrecognized mutation '{part}'")
    return events

def score_variants_from_csv(variants_csv: Path,
                            reference_id: str,
                            ref_seq: str,
                            records,
                            wt_nll: dict,
                            model, batch_converter,
                            device,
                            max_seqs: int,
                            pbar,
                            output_csv: Path,
                            bg_batch_size: int,
                            max_hamming: int):
    df = pd.read_csv(variants_csv, encoding="utf-8-sig")
    if "variant" not in df.columns:
        raise KeyError("CSV must have a 'variant' column")
    df["variant"] = df["variant"].astype(str)\
                        .apply(lambda v: v.encode("ascii","ignore").decode().strip())

    hdr2seq = {r.id: str(r.seq).replace("-", "") for r in records}
    n_backgrounds = min(max_seqs, len(hdr2seq))
    n_bg_batches = math.ceil(n_backgrounds / bg_batch_size)

    df["DeltaNLL_Reference"]         = np.nan
    df["Avg_DeltaNLL_Backgrounds"]   = np.nan
    df["StdDev_DeltaNLL_Backgrounds"]= np.nan

    for idx, row in df.iterrows():
        var = row["variant"]

        # — skip any '*'-notation before parsing —
        if "*" in var:
            logging.info("Skipping variant %s: contains '*' stop codon notation", var)
            continue

        evs = parse_variant_string(var)

        # — skip if too many mutations —
        if len(evs) > max_hamming:
            logging.info("Skipping variant %s: %d events > max_hamming %d",
                         var, len(evs), max_hamming)
            continue

        # — (optional) double-check that mutated seq doesn’t produce a '*' —
        seq_test = ref_seq
        for ev in evs:
            seq_test = apply_event(seq_test, ev)
        if "*" in seq_test:
            logging.info("Skipping variant %s: mutation produces '*' in sequence", var)
            continue

        # reference ΔNLL (1 batch of size 1)
        seq_ref = ref_seq
        for ev in evs:
            seq_ref = apply_event(seq_ref, ev)
        compute_nll_scores.nlls = {}
        compute_nll_scores([SeqRecord(seq_ref, id=f"{reference_id}|mut")],
                            model, batch_converter, device,
                            batch_size=1, pbar=pbar)
        ref_nll = compute_nll_scores.nlls[f"{reference_id}|mut"][1]
        df.at[idx, "DeltaNLL_Reference"] = float(ref_nll - wt_nll[reference_id])

        # backgrounds ΔNLLs
        picks = random.sample(list(hdr2seq), n_backgrounds)
        recs = []
        for h in picks:
            s = hdr2seq[h]
            for ev in evs:
                s = apply_event(s, ev)
            recs.append(SeqRecord(s, id=f"{h}|mut"))

        compute_nll_scores.nlls = {}
        compute_nll_scores(recs, model, batch_converter, device,
                            batch_size=bg_batch_size, pbar=pbar)
        deltas = [(nll - wt_nll[rid.split("|mut")[0]])
                  for rid, (_, nll) in compute_nll_scores.nlls.items()]
        df.at[idx, "Avg_DeltaNLL_Backgrounds"]   = float(np.mean(deltas))
        df.at[idx, "StdDev_DeltaNLL_Backgrounds"]= float(np.std(deltas))

    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    logging.info("Wrote scored variants to %s", output_csv)
    return df

def run(cfg):
    """
    Entry‐point for the mutation tester when called from run.py.
    Expects cfg to be the dict loaded from config.yaml.
    """
    from pathlib import Path
    import sys
    import logging
    import math
    import random
    from tqdm import tqdm
    import torch
    import esm
    import pandas as pd

    # 1. Unpack config
    project       = cfg["mutation_tester_project_directory"]
    max_seqs      = cfg["max_sequences_to_denoise_mutation_tester"]
    selected      = cfg["selected_sequence_mutation_tester"]
    max_hamming   = cfg["max_hamming_mutation_tester"]

    # 2. Prepare paths & logging
    input_dir  = Path("inputs/mutation_tester")  / project
    output_dir = Path("results/mutation_tester") / project
    setup_logging(output_dir)

    # 3. Load reference sequences
    records = get_fasta_sequences(input_dir)

    # 4. Choose device
    device = torch.device(
        "mps" if torch.backends.mps.is_available()
         else "cuda" if torch.cuda.is_available()
         else "cpu"
    )
    logging.info("Using device: %s", device)

    # 5. Load model
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()

    # 6. Find the variants CSV
    csvs = list(input_dir.glob("*.csv"))
    if not csvs:
        logging.error("No .csv files in %s", input_dir)
        sys.exit(1)
    variants_csv = csvs[0]

    # 7. 1st pass: compute raw NLLs
    batch_size_init = 8
    n_init_batches  = math.ceil(len(records) / batch_size_init)
    with tqdm(total=n_init_batches, desc="Raw NLL") as pbar1:
        compute_nll_scores.nlls = {}
        nll_scores = compute_nll_scores(
            records, model, batch_converter, device,
            batch_size=batch_size_init, pbar=pbar1
        )
        write_nll_csv(nll_scores, output_dir / "nll_scores.csv")

    # 8. Select reference
    reference = select_reference(nll_scores, selected)
    wt_nll_map = {hdr: score for hdr, (_, score) in nll_scores.items()}
    ref_seq    = nll_scores[reference][0]

    # 9. Determine total steps
    raw_df      = pd.read_csv(variants_csv, encoding="utf-8-sig")
    def passes(v):
        v = str(v).strip()
        if "*" in v: return False
        evs = parse_variant_string(v)
        if len(evs) > max_hamming: return False
        # double-check no stop
        s = ref_seq
        for ev in evs: s = apply_event(s, ev)
        return "*" not in s

    filtered    = [v for v in raw_df["variant"] if passes(v)]
    n_filtered  = len(filtered)
    n_bg_batches = math.ceil(min(max_seqs, len(records)) / 8)
    total_steps = n_filtered * (1 + n_bg_batches)

    # 10. Final scoring
    out_csv = output_dir / f"{variants_csv.stem}_scored.csv"
    with tqdm(total=total_steps, desc="Scoring variants") as pbar2:
        score_variants_from_csv(
            variants_csv,
            reference,
            ref_seq,
            records,
            wt_nll_map,
            model,
            batch_converter,
            device,
            max_seqs,
            pbar2,
            out_csv,
            bg_batch_size=8,
            max_hamming=max_hamming
        )

    logging.info("Wrote scored variants to %s", out_csv)
