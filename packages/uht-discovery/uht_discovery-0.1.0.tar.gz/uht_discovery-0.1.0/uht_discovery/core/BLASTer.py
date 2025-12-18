#!/usr/bin/env python3

import os
import glob
import datetime
from Bio.Blast import NCBIWWW, NCBIXML
from Bio import Entrez, SeqIO
from Bio.SeqRecord import SeqRecord
from .common import project_dir

def load_query_sequences(project_dir):
    """
    Load all FASTA sequences found in inputs/blaster/PROJECT/*.fasta.
    Returns a list of SeqRecord objects and the list of input file paths.
    """
    fasta_pattern = os.path.join('inputs', 'blaster', project_dir, '*.fasta')
    print(f"Looking for FASTA files with pattern: {fasta_pattern}")
    fasta_paths = sorted(glob.glob(fasta_pattern))
    print(f"Found {len(fasta_paths)} FASTA files: {fasta_paths}")
    
    if not fasta_paths:
        print(f"No FASTA files found in {fasta_pattern}")
        # List the directory contents to debug
        input_dir = os.path.join('inputs', 'blaster', project_dir)
        if os.path.exists(input_dir):
            print(f"Input directory exists. Contents: {os.listdir(input_dir)}")
        else:
            print(f"Input directory does not exist: {input_dir}")
        raise FileNotFoundError(f"No FASTA files found in {fasta_pattern}")

    query_records = []
    for path in fasta_paths:
        print(f"Loading sequences from: {path}")
        for record in SeqIO.parse(path, 'fasta'):
            query_records.append(record)
        print(f"Loaded {len(query_records)} sequences from {path}")
    return query_records, fasta_paths


def run_blastp(sequence, blast_db, evalue, hitlist_size):
    """
    Run BLASTP against NCBI using the provided sequence string.
    Returns the BLAST XML handle.
    """
    try:
        print(f"  Submitting BLAST query to NCBI (db={blast_db}, evalue={evalue})")
        result = NCBIWWW.qblast(
        program='blastp',
        database=blast_db,
        sequence=sequence,
        expect=evalue,
        hitlist_size=hitlist_size
    )
        print(f"  BLAST query submitted successfully")
        return result
    except Exception as e:
        print(f"  ERROR: BLAST query failed: {e}")
        raise


def parse_blast_xml(xml_handle, max_hits):
    """
    Parse BLAST XML handle to extract top hit accessions and HSP details.
    Returns a list of dicts.
    """
    blast_records = NCBIXML.parse(xml_handle)
    hits = []
    for blast_record in blast_records:
        for alignment in blast_record.alignments:
            for hsp in alignment.hsps:
                hits.append({
                    'accession': alignment.accession,
                    'defline':   alignment.hit_def,
                    'evalue':    hsp.expect,
                    'bit_score': hsp.bits
                })
                break  # one HSP per alignment
            if len(hits) >= max_hits:
                break
        break  # one query per XML
    return hits


def fetch_sequences_from_accessions(accessions, email, api_key=None):
    """
    Retrieve FASTA sequences for a list of accessions via Entrez.
    """
    try:
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key

        seq_records = []
        batch_size = 10
        for i in range(0, len(accessions), batch_size):
            batch = accessions[i:i+batch_size]
            print(f"  Fetching batch {i//batch_size + 1}: {len(batch)} sequences")
            try:
                handle = Entrez.efetch(
                    db="protein",
                    id=",".join(batch),
                    rettype="fasta",
                    retmode="text"
                )
                batch_records = list(SeqIO.parse(handle, "fasta"))
                seq_records.extend(batch_records)
                handle.close()
                print(f"  Successfully fetched {len(batch_records)} sequences")
            except Exception as e:
                print(f"  ERROR: Failed to fetch batch {i//batch_size + 1}: {e}")
        return seq_records
    except Exception as e:
        print(f"ERROR: Failed to initialize Entrez: {e}")
        raise


def write_combined_fasta(query_records, hit_records, output_path):
    """
    Write a FASTA file: queries first (tagged), then unique hits.
    """
    with open(output_path, 'w') as out_f:
        for record in query_records:
            record.id = f"{record.id}|Query"
            SeqIO.write(record, out_f, 'fasta')
        SeqIO.write(hit_records, out_f, 'fasta')


def write_blast_report(
    report_path,
    start_time,
    end_time,
    cfg,
    input_files,
    num_queries,
    unique_hits,
    hits_by_query
):
    """
    Write a text report including run metadata and hit details.
    """
    duration = end_time - start_time
    with open(report_path, 'w') as rpt:
        rpt.write("SMART-BLAST Run Report\n")
        rpt.write("======================\n\n")
        rpt.write(f"Start: {start_time:%Y-%m-%d %H:%M:%S}\n")
        rpt.write(f"End:   {end_time:%Y-%m-%d %H:%M:%S}\n")
        rpt.write(f"Duration: {duration}\n\n")

        rpt.write("Configuration:\n")
        rpt.write(f"  Project Directory: {cfg['blaster_project_directory']}\n")
        rpt.write(f"  Hits per Query:    {cfg.get('blaster_num_hits')}\n")
        rpt.write(f"  BLAST DB:          {cfg.get('blaster_blast_db')}\n")
        rpt.write(f"  E-value cutoff:    {cfg.get('blaster_evalue')}\n")
        rpt.write(f"  Email:             {cfg.get('blaster_email')}\n\n")

        rpt.write("Input FASTA files:\n")
        for f in input_files:
            rpt.write(f"  - {f}\n")
        rpt.write(f"\n# Queries: {num_queries}\n")
        rpt.write(f"# Unique accessions: {len(unique_hits)}\n\n")

        rpt.write("Hits by Query:\n")
        for query_id, hits in hits_by_query.items():
            rpt.write(f"\nQuery: {query_id}\n")
            rpt.write("Rank\tAccession\tE-value\tBit Score\tDefinition\n")
            for idx, hit in enumerate(hits, start=1):
                rpt.write(
                    f"{idx}\t{hit['accession']}\t{hit['evalue']:.2e}"
                    f"\t{hit['bit_score']:.1f}\t{hit['defline']}\n"
                )


def run(cfg):
    """
    Entry point for the BLASTer task.
    """
    try:
        # 1. Start timer
        start_time = datetime.datetime.now()
        print(f"Starting BLASTer at {start_time}")

        # 2. Unpack config
        project = os.getenv("BLASTER_PROJECT_ID") or cfg.get("blaster_project_directory")
        if not project:
            raise ValueError("Missing BLASTER_PROJECT_ID env-var or 'blaster_project_directory' in config")

        num_hits = int(cfg.get('blaster_num_hits', 10))
        blast_db = cfg.get('blaster_blast_db', 'nr')
        evalue   = float(cfg.get('blaster_evalue', 1e-5))
        email    = cfg.get('blaster_email')
        api_key  = cfg.get('blaster_api_key')

        print(f"Config: project={project}, hits={num_hits}, db={blast_db}, evalue={evalue}, email={email}")

        # 3. Load queries
        print("Loading query sequences...")
        query_records, fasta_paths = load_query_sequences(project)
        num_queries = len(query_records)
        print(f"Loaded {num_queries} query sequences from {len(fasta_paths)} files")

        # 4. Run BLAST & collect
        print("Starting BLAST searches...")
        hits_by_query     = {}
        seen              = set()
        ordered_accessions = []

        for i, rec in enumerate(query_records):
            print(f"BLASTing query {i+1}/{num_queries}: {rec.id}")
            try:
                xml_handle = run_blastp(str(rec.seq), blast_db, evalue, num_hits)
                hits = parse_blast_xml(xml_handle, num_hits)
                hits_by_query[rec.id] = hits
                print(f"  Found {len(hits)} hits for {rec.id}")
                for h in hits:
                    if h['accession'] not in seen:
                        seen.add(h['accession'])
                        ordered_accessions.append(h['accession'])
            except Exception as e:
                print(f"ERROR: Failed to BLAST query {rec.id}: {e}")
                hits_by_query[rec.id] = []

        # 5. Fetch sequences
        print(f"Fetching {len(ordered_accessions)} unique sequences from NCBI...")
        try:
            hit_records = fetch_sequences_from_accessions(ordered_accessions, email, api_key)
            print(f"Successfully fetched {len(hit_records)} sequences")
        except Exception as e:
            print(f"ERROR: Failed to fetch sequences: {e}")
            hit_records = []

        # 6. Write outputs
        print("Writing output files...")
        results_dir = os.path.join('results', 'blaster', project)
        os.makedirs(results_dir, exist_ok=True)

        fasta_out = os.path.join(results_dir, f"combined_hits_{project}.fasta")
        write_combined_fasta(query_records, hit_records, fasta_out)

        end_time   = datetime.datetime.now()
        report_out = os.path.join(results_dir, f"blast_report_{project}.txt")
        write_blast_report(
            report_out, start_time, end_time,
            cfg, fasta_paths, num_queries,
            ordered_accessions, hits_by_query
        )

        print(f"FASTA saved to: {fasta_out}")
        print(f"Report saved to: {report_out}")
        print(f"BLASTer completed successfully at {end_time}")
        
    except Exception as e:
        print(f"FATAL ERROR in BLASTer: {e}")
        import traceback
        traceback.print_exc()
        raise
