#!/usr/bin/env python3

import os
import glob
import datetime
import argparse
import sys
from pathlib import Path
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
from Bio import SeqIO

# Handle imports for both standalone and module execution
try:
    from core.common import project_dir
except ImportError:
    # For standalone execution, provide a simple fallback
    def project_dir(task, cfg):
        return cfg.get(f"{task}_project_directory")

# Directory constants
INPUT_DIR = os.path.join("inputs", "trim")
OUTPUT_DIR = os.path.join("results", "trim")

# Valid amino acids (20 standard). Sequences containing any other character will be discarded.
VALID_AA = set("ACDEFGHIKLMNPQRSTVWY")

def load_fasta_sequences(fasta_path):
    """
    Load all SeqRecord objects from a FASTA file.
    Returns a list of SeqRecord.
    """
    return list(SeqIO.parse(fasta_path, "fasta"))

def plot_length_distribution(lengths, reference_length, title, save_path=None):
    """
    Plot a histogram of sequence lengths, mark reference_length with a vertical line.
    If save_path is provided, save the plot as a PNG file there.
    """
    plt.figure(figsize=(8, 5))
    plt.hist(lengths, bins='auto', color='skyblue', edgecolor='black')
    plt.axvline(reference_length, color='red', linestyle='--', label=f"First seq length = {reference_length}")
    plt.title(f"Length Distribution: {title}")
    plt.xlabel("Sequence Length")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()

def prompt_length_thresholds(min_len, max_len):
    """
    Prompt the user to enter lower and upper length thresholds.
    Ensures they are integers and min ≤ lower ≤ upper ≤ max.
    """
    print(f"Enter length thresholds between {min_len} and {max_len}.")
    while True:
        try:
            low = int(input("  Lower threshold (inclusive): ").strip())
            high = int(input("  Upper threshold (inclusive): ").strip())
            if low < min_len or high > max_len or low > high:
                print(f"  Please choose {min_len} ≤ lower ≤ upper ≤ {max_len}.")
                continue
            return low, high
        except ValueError:
            print("  Please enter valid integers.")

def filter_by_length(records, low, high):
    """
    Return two lists:
      - kept: SeqRecords with length between [low, high]
      - removed: SeqRecords outside that range
    """
    kept = []
    removed = []
    for rec in records:
        L = len(rec.seq)
        if low <= L <= high:
            kept.append(rec)
        else:
            removed.append(rec)
    return kept, removed

def filter_invalid_aa(records):
    """
    Return two lists:
      - kept: SeqRecords containing only VALID_AA characters
      - removed: SeqRecords that contain any invalid character
    (Case‐insensitive check.)
    """
    kept = []
    removed = []
    for rec in records:
        seq_upper = str(rec.seq).upper()
        if all(aa in VALID_AA for aa in seq_upper):
            kept.append(rec)
        else:
            removed.append(rec)
    return kept, removed

def filter_duplicates(records):
    """
    Return two lists:
      - kept: SeqRecords with unique sequences (first instance kept)
      - removed: SeqRecords that are duplicates (identical sequence to an earlier record)
    """
    kept = []
    removed = []
    seen = set()
    for rec in records:
        seq_str = str(rec.seq)
        if seq_str not in seen:
            kept.append(rec)
            seen.add(seq_str)
        else:
            removed.append(rec)
    return kept, removed

def write_fasta(records, output_path):
    """
    Write a list of SeqRecord objects to a FASTA file.
    """
    with open(output_path, "w") as out_f:
        SeqIO.write(records, out_f, "fasta")

def write_qc_report(report_path, fasta_name, metrics, low_high, auto_info=None):
    """
    Write a QC report summarizing trimming steps and metrics.
    metrics is a dict with keys:
      - initial_count
      - after_length_count
      - after_aa_count
      - avg_length_initial
      - avg_length_after_length
      - avg_length_after_aa
    low_high is a tuple (low, high) thresholds chosen.
    auto_info is optional dict with keys:
      - reference_length
      - method_used
      - std_dev
    """
    low, high = low_high
    with open(report_path, "w") as rpt:
        rpt.write(f"trim QC Report\n")
        rpt.write(f"======================\n\n")
        rpt.write(f"Input FASTA file: {fasta_name}\n")
        rpt.write(f"Run date & time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        rpt.write("Length thresholds chosen:\n")
        rpt.write(f"  Lower = {low}\n")
        rpt.write(f"  Upper = {high}\n")
        if auto_info:
            rpt.write(f"  Auto-calculation method: {auto_info['method_used']}\n")
            rpt.write(f"  Reference length: {auto_info['reference_length']:.1f}\n")
            rpt.write(f"  Standard deviation: {auto_info['std_dev']:.1f}\n")
        rpt.write("\n")
        rpt.write("Sequence counts:\n")
        rpt.write(f"  Initial total: {metrics['initial_count']}\n")
        rpt.write(f"  After length filter: {metrics['after_length_count']}\n")
        rpt.write(f"  After AA + duplicate filter: {metrics['after_aa_count']}\n\n")
        rpt.write("Average lengths:\n")
        rpt.write(f"  Initial average: {metrics['avg_length_initial']:.1f}\n")
        rpt.write(f"  After length filter: {metrics['avg_length_after_length']:.1f}\n")
        rpt.write(f"  After AA + duplicate filter: {metrics['avg_length_after_aa']:.1f}\n")

def compute_average_length(records):
    """
    Return the average length of sequences in a list of SeqRecord.
    Returns 0 if list is empty.
    """
    if not records:
        return 0.0
    lengths = [len(rec.seq) for rec in records]
    return float(np.mean(lengths))

def calculate_auto_thresholds(lengths):
    """
    Automatically calculate length thresholds based on sequence lengths.
    
    Algorithm:
    1. Find the most common length
    2. If no single most common length, use the average
    3. Calculate standard deviation
    4. Set thresholds to reference_length ± 1 SD
    
    Returns (low_threshold, high_threshold, reference_length, method_used)
    """
    if not lengths:
        return 0, 0, 0, "empty"
    
    # Convert to numpy array for easier calculations
    lengths_array = np.array(lengths)
    
    # Find most common length
    length_counts = Counter(lengths)
    most_common = length_counts.most_common()
    
    # Check if there's a single most common length
    if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
        # Tie for most common, use average instead
        reference_length = np.mean(lengths_array)
        method_used = "average (no single most common)"
    else:
        # Use most common length
        reference_length = most_common[0][0]
        method_used = "most_common"
    
    # Calculate standard deviation
    std_dev = np.std(lengths_array)
    
    # Set thresholds to reference ± 1 SD
    low_threshold = max(1, int(reference_length - std_dev))  # Don't go below 1
    high_threshold = int(reference_length + std_dev)
    
    return low_threshold, high_threshold, reference_length, method_used

def process_single_fasta(fasta_path, output_dir, auto_mode=False, manual_low=None, manual_high=None):
    """
    Process a single FASTA file with trimming.
    
    Args:
        fasta_path: Path to the input FASTA file
        output_dir: Directory for output files
        auto_mode: If True, automatically calculate thresholds
        manual_low: Manual lower threshold (if not auto_mode)
        manual_high: Manual upper threshold (if not auto_mode)
    
    Returns:
        dict with processing results
    """
    fasta_name = fasta_path.name
    base = fasta_path.stem
    
    # Load sequences
    records = load_fasta_sequences(fasta_path)
    initial_count = len(records)
    
    if initial_count == 0:
        print(f"  Warning: No sequences found in {fasta_name}")
        return None
    
    lengths = [len(rec.seq) for rec in records]
    avg_initial = compute_average_length(records)
    first_len = lengths[0] if lengths else 0
    min_len, max_len = (min(lengths), max(lengths)) if lengths else (0, 0)
    
    # Generate histogram
    hist_path = output_dir / f"{base}_length_hist.png"
    plot_length_distribution(lengths, first_len, title=fasta_name, save_path=hist_path)
    
    # Determine thresholds
    auto_info = None
    if auto_mode:
        low, high, reference_length, method_used = calculate_auto_thresholds(lengths)
        std_dev = np.std(lengths)
        auto_info = {
            'reference_length': reference_length,
            'method_used': method_used,
            'std_dev': std_dev
        }
        print(f"  Auto-calculated thresholds for {fasta_name}: {low}-{high} (method: {method_used})")
    else:
        low = manual_low if manual_low is not None else min_len
        high = manual_high if manual_high is not None else max_len
        print(f"  Using manual thresholds for {fasta_name}: {low}-{high}")
    
    # Apply filters
    kept_len, removed_len = filter_by_length(records, low, high)
    kept_aa, removed_aa = filter_invalid_aa(kept_len)
    unique_recs, removed_dup = filter_duplicates(kept_aa)
    
    # Calculate metrics
    avg_after_length = compute_average_length(kept_len)
    avg_after_aa = compute_average_length(unique_recs)
    
    # Output files
    out_fasta = output_dir / f"{base}_trimmed.fasta"
    report_txt = output_dir / f"{base}_qc_report.txt"
    
    # Write results
    write_fasta(unique_recs, out_fasta)
    
    metrics = {
        "initial_count": initial_count,
        "after_length_count": len(kept_len),
        "after_aa_count": len(unique_recs),
        "avg_length_initial": avg_initial,
        "avg_length_after_length": avg_after_length,
        "avg_length_after_aa": avg_after_aa,
    }
    
    write_qc_report(report_txt, fasta_name, metrics, (low, high), auto_info)
    
    print(f"  → Trimmed FASTA saved to: {out_fasta}")
    print(f"  → QC report saved to: {report_txt}")
    print(f"  → Histogram saved to: {hist_path}")
    print(f"  → Sequences: {initial_count} → {len(kept_len)} → {len(unique_recs)}")
    
    return {
        "fasta_name": fasta_name,
        "out_fasta": str(out_fasta),
        "report_txt": str(report_txt),
        "hist_path": str(hist_path),
        "metrics": metrics,
        "auto_info": auto_info
    }

# New function: run initial stage for web (generate histogram only)
def run_histogram_only(cfg):
    """
    Run only the initial stage of trim: load sequences, compute lengths, save histogram.
    Returns the histogram path, min_len, max_len, and other stats.
    """
    import os
    from pathlib import Path

    project = project_dir("trim", cfg)
    if not project:
        raise ValueError(
            "Need TRIM_PROJECT_ID env-var or 'trim_project_directory' in config"
        )

    input_dir  = Path("inputs")  / "trim"  / project
    output_dir = Path("results") / "trim"  / project
    output_dir.mkdir(parents=True, exist_ok=True)

    fasta_paths = sorted(input_dir.glob("*.fasta"))
    if not fasta_paths:
        print(f"No FASTA files found in '{input_dir}'. Exiting.")
        return None

    for fasta_path in fasta_paths:
        fasta_name = fasta_path.name
        records = load_fasta_sequences(fasta_path)
        lengths = [len(rec.seq) for rec in records]
        first_len = lengths[0] if lengths else 0
        min_len, max_len = (min(lengths), max(lengths)) if lengths else (0, 0)
        hist_path = output_dir / f"{fasta_path.stem}_length_hist.png"
        plot_length_distribution(lengths, first_len, title=fasta_name, save_path=hist_path)
        return {
            "hist_path": str(hist_path),
            "min_len": min_len,
            "max_len": max_len,
            "fasta_name": fasta_name,
            "num_records": len(records),
        }
    return None

def run(cfg):
    """
    Entry point for trim when called from run.py or web.
    If 'trim_low' and 'trim_high' are not provided, only generate histogram and exit.
    Now processes each FASTA file independently.
    """
    import os
    from pathlib import Path

    project = project_dir("trim", cfg)
    if not project:
        raise ValueError(
            "Need TRIM_PROJECT_ID env-var or 'trim_project_directory' in config"
        )

    mode = cfg.get("mode", "web").lower()
    auto_mode = cfg.get("auto_mode", False)
    input_dir  = Path("inputs")  / "trim"  / project
    output_dir = Path("results") / "trim"  / project
    output_dir.mkdir(parents=True, exist_ok=True)

    fasta_paths = sorted(input_dir.glob("*.fasta"))
    if not fasta_paths:
        print(f"No FASTA files found in '{input_dir}'. Exiting.")
        return

    print(f"Found {len(fasta_paths)} FASTA file(s) to process.")
    results = []
    
    # Check if only histogram generation is requested
    histogram_only = cfg.get('trim_low') is None or cfg.get('trim_high') is None
    
    for i, fasta_path in enumerate(fasta_paths, 1):
        print(f"\nProcessing file {i}/{len(fasta_paths)}: {fasta_path.name}")
        
        if histogram_only and not auto_mode:
            # Only generate histogram
            records = load_fasta_sequences(fasta_path)
            lengths = [len(rec.seq) for rec in records]
            first_len = lengths[0] if lengths else 0
            min_len, max_len = (min(lengths), max(lengths)) if lengths else (0, 0)
            hist_path = output_dir / f"{fasta_path.stem}_length_hist.png"
            plot_length_distribution(lengths, first_len, title=fasta_path.name, save_path=hist_path)
            print(f"  → Histogram saved to: {hist_path}")
            results.append({
                "hist_path": str(hist_path),
                "min_len": min_len,
                "max_len": max_len,
                "fasta_name": fasta_path.name,
                "num_records": len(records),
            })
        else:
            # Process with trimming
            manual_low = cfg.get('trim_low')
            manual_high = cfg.get('trim_high')
            
            result = process_single_fasta(
                fasta_path, 
                output_dir, 
                auto_mode=auto_mode,
                manual_low=manual_low,
                manual_high=manual_high
            )
            
            if result:
                results.append(result)
    
    print(f"\nCompleted processing {len(results)} files.")
    
    # For backward compatibility, return single result if only one file
    if len(results) == 1:
        return results[0]
    else:
        return {"results": results, "num_files": len(results)}

def main():
    """
    Command-line interface for standalone execution.
    """
    parser = argparse.ArgumentParser(
        description="Trim FASTA sequences by length with quality control.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto mode - automatically calculate thresholds
  python trim.py /path/to/input/dir /path/to/output/dir --auto
  
  # Manual mode - specify thresholds
  python trim.py /path/to/input/dir /path/to/output/dir --low 300 --high 600
  
  # Histogram only - generate histograms without trimming
  python trim.py /path/to/input/dir /path/to/output/dir --histogram-only
        """
    )
    
    parser.add_argument("input_dir", help="Directory containing input FASTA files")
    parser.add_argument("output_dir", help="Directory for output files")
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--auto", action="store_true", 
                           help="Automatically calculate length thresholds")
    mode_group.add_argument("--manual", action="store_true",
                           help="Use manual thresholds (requires --low and --high)")
    mode_group.add_argument("--histogram-only", action="store_true",
                           help="Generate histograms only, no trimming")
    
    parser.add_argument("--low", type=int, 
                       help="Lower length threshold (required with --manual)")
    parser.add_argument("--high", type=int,
                       help="Upper length threshold (required with --manual)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.manual and (args.low is None or args.high is None):
        parser.error("--manual mode requires both --low and --high")
    
    if args.low is not None and args.high is not None and args.low > args.high:
        parser.error("--low must be less than or equal to --high")
    
    # Convert paths to Path objects
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    # Check input directory exists
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find FASTA files
    fasta_paths = sorted(input_dir.glob("*.fasta"))
    if not fasta_paths:
        print(f"No FASTA files found in '{input_dir}'. Exiting.")
        sys.exit(1)
    
    print(f"Found {len(fasta_paths)} FASTA file(s) to process.")
    results = []
    
    for i, fasta_path in enumerate(fasta_paths, 1):
        print(f"\nProcessing file {i}/{len(fasta_paths)}: {fasta_path.name}")
        
        if args.histogram_only:
            # Only generate histogram
            records = load_fasta_sequences(fasta_path)
            lengths = [len(rec.seq) for rec in records]
            first_len = lengths[0] if lengths else 0
            min_len, max_len = (min(lengths), max(lengths)) if lengths else (0, 0)
            hist_path = output_dir / f"{fasta_path.stem}_length_hist.png"
            plot_length_distribution(lengths, first_len, title=fasta_path.name, save_path=hist_path)
            print(f"  → Histogram saved to: {hist_path}")
            print(f"  → Length range: {min_len} - {max_len}")
            results.append({
                "hist_path": str(hist_path),
                "min_len": min_len,
                "max_len": max_len,
                "fasta_name": fasta_path.name,
                "num_records": len(records),
            })
        else:
            # Process with trimming
            result = process_single_fasta(
                fasta_path, 
                output_dir, 
                auto_mode=args.auto,
                manual_low=args.low,
                manual_high=args.high
            )
            
            if result:
                results.append(result)
    
    print(f"\nCompleted processing {len(results)} files.")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    main()
