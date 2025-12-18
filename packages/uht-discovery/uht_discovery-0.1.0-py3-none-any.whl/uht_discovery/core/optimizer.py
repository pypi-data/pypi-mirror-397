#!/usr/bin/env python3
import os
import sys
import logging
import yaml
import subprocess
import random
import itertools
from pathlib import Path

import torch
import esm
from tqdm import tqdm
from Bio import SeqIO, AlignIO
from Bio.SeqRecord import SeqRecord

import numpy as np
import csv
from .common import project_dir

def load_config(config_path="config.yaml"):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    for key in ("optimizer_project_directory", "max_sequences_to_de_denoise", "max_order"):
        if key not in cfg:
            raise KeyError(f"Missing required config key: {key}")
    return cfg

def setup_logging(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = output_dir / "pipeline.log"
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(str(log_file))
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logging.info("Logging to %s", log_file)

def get_fasta_sequences(input_dir: Path, max_length=3000):
    seqs = []
    for fasta in input_dir.glob("*.fasta"):
        for rec in SeqIO.parse(str(fasta), "fasta"):
            if len(rec.seq) > max_length:
                logging.debug("Excluding %s (length %d > %d)", rec.id, len(rec.seq), max_length)
            else:
                seqs.append(rec)
    if not seqs:
        logging.error("No sequences ≤ %d aa found in %s", max_length, input_dir)
        sys.exit(1)
    logging.info("Loaded %d sequences (≤ %d aa)", len(seqs), max_length)
    return seqs

def compute_nll_scores(records, model, batch_converter, device, batch_size=16):
    model.eval()
    nlls = {}
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
        raw_nll = -(tp * mask).sum(dim=1).cpu().numpy()
        lengths = mask.sum(dim=1).cpu().numpy()
        norm_nll = raw_nll / lengths
        for (hdr, seq), score in zip([(r.id, str(r.seq)) for r in batch], norm_nll):
            nlls[hdr] = (seq, float(score))
        logging.debug("Processed batch %d/%d", i//batch_size+1, (len(records)-1)//batch_size+1)
    return nlls

def write_nll_csv(nll_scores, out_path: Path):
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Header", "Sequence", "Normalized_NLL"])
        for hdr, (seq, nll) in nll_scores.items():
            w.writerow([hdr, seq, nll])
    logging.info("Wrote NLL scores to %s", out_path)

def select_reference(nll_scores, selected_substr=None):
    headers = list(nll_scores)
    if selected_substr:
        for h in headers:
            if selected_substr in h:
                logging.info("Using specified reference '%s'", h)
                return h
        logging.warning("No header matching '%s'; falling back to lowest NLL", selected_substr)
    ref = min(nll_scores.items(), key=lambda x: x[1][1])[0]
    logging.info("Selected reference by lowest NLL: '%s'", ref)
    return ref

def write_reordered_fasta(records, reference, out_path: Path):
    ref_rec = next(r for r in records if r.id == reference)
    others = [r for r in records if r.id != reference]
    with open(out_path, "w") as f:
        SeqIO.write([ref_rec] + others, f, "fasta")
    logging.info("Wrote reordered FASTA to %s", out_path)

def run_clustalo(in_fasta: Path, out_aln: Path):
    logging.info("Running Clustal Omega...")
    subprocess.run(["clustalo", "-i", str(in_fasta), "-o", str(out_aln), "--force"], check=True)
    logging.info("Alignment written to %s", out_aln)

def parse_msa_mutations(aln_path: Path):
    aln = AlignIO.read(str(aln_path), "fasta")
    ref = aln[0].seq
    msa2ref, idx = [], 0
    for aa in ref:
        if aa == "-":
            msa2ref.append(None)
        else:
            msa2ref.append(idx)
            idx += 1

    events = set()
    for rec in aln[1:]:
        i = 0
        while i < len(ref):
            r, s = ref[i], rec.seq[i]
            pos = msa2ref[i]
            if r != "-" and s != "-" and r != s:
                events.add(("sub", pos+1, r, s))
                i += 1
            elif r == "-" and s != "-":
                anchor = (msa2ref[i-1]+1) if i>0 and msa2ref[i-1] is not None else 0
                ins, start = [], i
                while i < len(ref) and ref[i] == "-" and rec.seq[i] != "-":
                    ins.append(rec.seq[i]); i += 1
                events.add(("ins", anchor, "".join(ins)))
            elif r != "-" and s == "-":
                start = pos+1
                dels = []
                while i < len(ref) and ref[i] != "-" and rec.seq[i] == "-":
                    dels.append(ref[i]); i += 1
                events.add(("del", start, "".join(dels)))
            else:
                i += 1

    logging.info("Identified %d unique mutation events", len(events))
    return list(events), aln

def format_mutation(ev):
    typ, pos = ev[0], ev[1]
    if typ == "sub":
        return f"{ev[2]}{pos}{ev[3]}"
    if typ == "ins":
        return f"{pos}ins{ev[2]}"
    if typ == "del":
        return f"{ev[2]}{pos}del"
    return str(ev)

def apply_event(seq, ev):
    typ, pos = ev[0], ev[1]-1
    if typ == "sub":
        return seq[:pos] + ev[3] + seq[pos+1:]
    if typ == "ins":
        return seq[:pos] + ev[2] + seq[pos:]
    if typ == "del":
        L = len(ev[2])
        return seq[:pos] + seq[pos+L:]
    raise ValueError("Unknown event")

def sample_and_score_mutations(events, aln, wt_nll, model, batch_converter,
                               device, max_seqs, output_csv: Path):
    headers = [r.id for r in aln[1:]]
    hdr2seq = {r.id: str(r.seq).replace("-", "") for r in aln[1:]}
    results = []
    for ev in tqdm(events, desc="Scoring singles"):
        picks = random.sample(headers, min(max_seqs, len(headers)))
        deltas = []
        for h in picks:
            mut = apply_event(hdr2seq[h], ev)
            rec = SeqRecord(mut, id=f"{h}|mut")
            nll = compute_nll_scores([rec], model, batch_converter, device, batch_size=1)[rec.id][1]
            deltas.append(nll - wt_nll[h])
        ref_id = aln[0].id
        ref_seq = str(aln[0].seq).replace("-", "")
        ref_mut = apply_event(ref_seq, ev)
        ref_rec = SeqRecord(ref_mut, id=f"{ref_id}|mut")
        ref_delta = compute_nll_scores([ref_rec], model, batch_converter, device, batch_size=1)[ref_rec.id][1] - wt_nll[ref_id]

        results.append({
            "event": ev,
            "mutation": format_mutation(ev),
            "avg_delta_bg": float(np.mean(deltas)) if deltas else None,
            "std_delta_bg": float(np.std(deltas)) if deltas else None,
            "delta_ref": float(ref_delta),
        })

    with open(output_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "Mutation",
            "Avg_DeltaNLL_Backgrounds",
            "StdDev_DeltaNLL_Backgrounds",
            "DeltaNLL_Reference"
        ])
        for r in results:
            w.writerow([
                r["mutation"],
                r["avg_delta_bg"],
                r["std_delta_bg"],
                r["delta_ref"]
            ])
    logging.info("Wrote single-mutant scores to %s", output_csv)
    return results

def iterate_combinations(
    reference: str,
    ref_seq: str,
    events: list,
    single_results: list,
    wt_nll: dict,
    model,
    batch_converter,
    device,
    max_seqs: int,
    max_order: int,
    aln,
    output_dir: Path
):
    """
    Build higher‐order mutation combos from single‐mutant results,
    sampling backgrounds and scoring each combo, up to max_order.
    """
    # map each event to its metrics dict
    single_map = {r["event"]: r for r in single_results}

    # prepare sequence lookup for background sampling
    headers = [r.id for r in aln[1:]]
    hdr2seq = {r.id: str(r.seq).replace("-", "") for r in aln[1:]}

    # 1st‐order: only include events where avg_delta_bg or delta_ref is defined and negative
    first_order = []
    for ev in events:
        bg = single_map[ev]["avg_delta_bg"]
        dr = single_map[ev]["delta_ref"]
        if (bg is not None and bg < 0) or (dr is not None and dr < 0):
            first_order.append((ev,))
    combos_by_order = {1: first_order}

    # Now iteratively build up to max_order
    for order in range(2, max_order + 1):
        prev_combos = combos_by_order[order - 1]
        candidates  = set()

        # generate new candidate combos by adding one event at a time
        for combo in prev_combos:
            for ev in events:
                if ev in combo:
                    continue
                new_combo = tuple(sorted(combo + (ev,), key=lambda e: (e[1], e[0])))

                # skip if any two events overlap in sequence position
                used_positions = set()
                ok = True
                for e in new_combo:
                    if e[0] == "del":
                        positions = set(range(e[1], e[1] + len(e[2])))
                    else:
                        positions = {e[1]}
                    if used_positions & positions:
                        ok = False
                        break
                    used_positions |= positions
                if ok:
                    candidates.add(new_combo)

        # score each candidate combo
        scored = []
        for combo in tqdm(candidates, desc=f"Scoring order-{order} combos"):
            # background delta sampling
            bg_deltas = []
            picks = random.sample(headers, min(max_seqs, len(headers)))
            for h in picks:
                seq = hdr2seq[h]
                for ev in combo:
                    seq = apply_event(seq, ev)
                rec = SeqRecord(seq, id=f"{h}|combo")
                nll = compute_nll_scores([rec], model, batch_converter, device, batch_size=1)[rec.id][1]
                bg_deltas.append(nll - wt_nll[h])

            obs_bg_avg = float(np.mean(bg_deltas)) if bg_deltas else None
            obs_bg_std = float(np.std(bg_deltas)) if bg_deltas else None

            # reference delta
            seq_ref = ref_seq
            for ev in combo:
                seq_ref = apply_event(seq_ref, ev)
            rec_ref = SeqRecord(seq_ref, id=f"{reference}|combo")
            nll_ref = compute_nll_scores([rec_ref], model, batch_converter, device, batch_size=1)[rec_ref.id][1]
            obs_ref = float(nll_ref - wt_nll[reference])

            # expected additive effects
            exp_bg = sum(single_map[ev]["avg_delta_bg"] or 0 for ev in combo)
            exp_ref = sum(single_map[ev]["delta_ref"]    or 0 for ev in combo)

            scored.append((combo, obs_bg_avg, obs_bg_std, exp_bg, obs_ref, exp_ref))

        # write this order’s CSV
        out_csv = output_dir / f"combo_order_{order}.csv"
        with open(out_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                "Combination",
                "Obs_Avg_DeltaNLL_Backgrounds",
                "Obs_StdDev_DeltaNLL_Backgrounds",
                "Exp_Sum_DeltaNLL_Backgrounds",
                "Obs_DeltaNLL_Reference",
                "Exp_Sum_DeltaNLL_Reference"
            ])
            for combo, bg_avg, bg_std, exp_bg, ref_obs, exp_ref in scored:
                combo_str = ";".join(format_mutation(e) for e in combo)
                w.writerow([combo_str, bg_avg, bg_std, exp_bg, ref_obs, exp_ref])
        logging.info("Wrote order-%d combos to %s", order, out_csv)

        # filter for next order: keep combos where at least one observed effect is negative
        next_list = []
        for combo, bg_avg, bg_std, exp_bg, ref_obs, exp_ref in scored:
            if (bg_avg is not None and bg_avg < 0) or (ref_obs is not None and ref_obs < 0):
                next_list.append(combo)
        combos_by_order[order] = next_list

    return combos_by_order


def run(cfg):
    """
    Entry point for the optimizer task.
    Expects cfg to be the dict loaded from config.yaml.
    """
    # 1. Unpack config
    project = project_dir("optimizer", cfg)      # unified helper
    if not project:
        raise ValueError(
            "Need OPTIMIZER_PROJECT_ID env-var or 'optimizer_project_directory' in config"
        )

    max_seqs  = cfg["max_sequences_to_de_denoise"]
    max_order = cfg["max_order"]
    selected  = cfg.get("selected_sequence")

    # 2. Prepare paths & logging
    input_dir  = Path("inputs/optimizer") / project
    output_dir = Path("results/optimizer") / project
    setup_logging(output_dir)

    # 3. Load & filter FASTA
    records = get_fasta_sequences(input_dir)

    # 4. Select device
    device = torch.device(
        "mps"  if torch.backends.mps.is_available()  else
        "cuda" if torch.cuda.is_available() else
        "cpu"
    )
    logging.info("Using device: %s", device)

    # 5. Load model
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()

    # 6. Compute NLL scores & write CSV
    nll_scores = compute_nll_scores(records, model, batch_converter, device, batch_size=8)
    write_nll_csv(nll_scores, output_dir / "nll_scores.csv")

    # 7. Choose reference & align
    reference = select_reference(nll_scores, selected)
    write_reordered_fasta(records, reference, output_dir / "for_alignment.fasta")
    aln_path = output_dir / "alignment.aln"
    run_clustalo(output_dir / "for_alignment.fasta", aln_path)

    # 8. Identify mutations & score singles
    events, aln = parse_msa_mutations(aln_path)
    wt_nll = {hdr: score for hdr, (_, score) in nll_scores.items()}
    single_results = sample_and_score_mutations(
        events, aln, wt_nll,
        model, batch_converter, device,
        max_seqs, output_dir / "mutation_scores.csv"
    )

    # 9. Build and score combinations
    ref_seq = nll_scores[reference][0]
    iterate_combinations(
        reference, ref_seq,
        events, single_results,
        wt_nll, model, batch_converter, device,
        max_seqs, max_order,
        aln, output_dir
    )
    
    logging.info("Optimization pipeline for project '%s' complete.", project)

# bottom of the file
if __name__ == "__main__":
    cfg = load_config("config.yaml")
    run(cfg)
