#!/usr/bin/env python3
"""
Command-line interface tools for UHT Discovery

"""

import argparse
import sys
import os
import yaml
import glob
from pathlib import Path

# Import from uht_discovery.core subpackage
from uht_discovery.core.BLASTer import run as blaster_run
from uht_discovery.core.trim import run as trim_run
from uht_discovery.core.plmclust import run as plmclust_run
from uht_discovery.core.plmclustv2 import run as plmclustv2_run
from uht_discovery.core.optimizer import run as optimizer_run
from uht_discovery.core.mutation_tester import run as mutation_tester_run
from uht_discovery.core.comprehensive_benchmarking_pipeline import ComprehensiveBenchmarkingPipeline
from uht_discovery.core.biophysical_signals_analysis import run as biophysical_run
from uht_discovery.core.sequence_similarity_analysis import run as sequence_similarity_run
from uht_discovery.core.phylogenetic_analysis import run as phylo_run
from uht_discovery.core.tsne_visualization import run as tsne_run
from uht_discovery.core.kmeansbenchmark import run as kmeansbenchmark_run

def load_config_file(config_path="config.yaml"):
    """Load configuration from YAML file"""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

def blaster_cli():
    """CLI for BLASTER"""
    parser = argparse.ArgumentParser(
        description="BLAST sequence search against NCBI databases",
        epilog="Example: uht-blast --project my_project --email user@example.com --hits 50"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--hits", type=int, default=100, help="Number of hits to retrieve (default: 100)")
    parser.add_argument("--db", default="nr", choices=["nr", "swissprot", "refseq_protein"], 
                       help="BLAST database to search (default: nr)")
    parser.add_argument("--evalue", type=float, default=1e-5, help="E-value cutoff (default: 1e-5)")
    parser.add_argument("--email", required=True, help="Email address for NCBI (REQUIRED)")
    parser.add_argument("--api-key", help="NCBI API key (OPTIONAL, speeds up requests if provided)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    cfg.update({
        "blaster_project_directory": args.project,
        "blaster_num_hits": args.hits,
        "blaster_blast_db": args.db,
        "blaster_evalue": args.evalue,
        "blaster_email": args.email,
    })
    if args.api_key:
        cfg["blaster_api_key"] = args.api_key
    
    blaster_run(cfg)

def trim_cli():
    """CLI for TRIM"""
    parser = argparse.ArgumentParser(
        description="Sequence quality control and length-based trimming",
        epilog="Example: uht-trim --project my_project --auto\n"
               "         uht-trim --project my_project --low 50 --high 500"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--auto", action="store_true", 
                       help="Auto-calculate thresholds based on length distribution (OPTIONAL)")
    parser.add_argument("--low", type=int, 
                       help="Lower length threshold - sequences shorter than this will be removed (OPTIONAL, requires --high)")
    parser.add_argument("--high", type=int, 
                       help="Upper length threshold - sequences longer than this will be removed (OPTIONAL, requires --low)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    cfg.update({
        "trim_project_directory": args.project,
        "mode": "cli",
        "auto_mode": args.auto,
    })
    if args.low:
        cfg["trim_low"] = args.low
    if args.high:
        cfg["trim_high"] = args.high
    
    trim_run(cfg)

def plmclust_cli():
    """CLI for PLMCLUST (v1 - legacy)"""
    parser = argparse.ArgumentParser(
        description="Protein language model clustering (v1 - legacy, uses masking-based scoring)",
        epilog="Note: Consider using uht-clust (plmclustv2) for faster, more consistent results"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--clusters", default="auto", 
                       help="Number of clusters or 'auto' for automatic selection (default: auto)")
    parser.add_argument("--sil-min", type=int, default=2, 
                       help="Minimum k for silhouette search when using auto (default: 2)")
    parser.add_argument("--sil-max", type=int, default=10, 
                       help="Maximum k for silhouette search when using auto (default: 10)")
    parser.add_argument("--n-maskings", type=int, default=5, 
                       help="Number of random maskings for scoring (default: 5)")
    parser.add_argument("--keep-separate", action="store_true", 
                       help="Process each input FASTA file separately (OPTIONAL)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    cfg.update({
        "plmclust_project_directory": args.project,
        "plmclust_cluster_number": args.clusters if args.clusters != "auto" else "auto",
        "silhouette_range": [args.sil_min, args.sil_max],
        "plm_clust_replicates": args.n_maskings,
        "plmclust_keepseparate": args.keep_separate,
    })
    
    plmclust_run(cfg)

def plmclustv2_cli():
    """CLI for PLMCLUSTV2"""
    parser = argparse.ArgumentParser(
        description="Protein language model clustering using ESM2 embeddings and single-pass NLL scoring",
        epilog="Example: uht-clust --project my_project --clusters auto --sil-min 2 --sil-max 10"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--clusters", default="auto", 
                       help="Number of clusters or 'auto' for automatic selection (default: auto)")
    parser.add_argument("--sil-min", type=int, default=2, 
                       help="Minimum k for silhouette search when using auto (default: 2)")
    parser.add_argument("--sil-max", type=int, default=10, 
                       help="Maximum k for silhouette search when using auto (default: 10)")
    parser.add_argument("--keep-separate", action="store_true", 
                       help="Process each input FASTA file separately (OPTIONAL)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    cfg.update({
        "plmclustv2_project_directory": args.project,
        "plmclustv2_cluster_number": args.clusters,
        "silhouette_range": [args.sil_min, args.sil_max],
        "plmclustv2_keepseparate": args.keep_separate,
    })
    
    plmclustv2_run(cfg)

def optimizer_cli():
    """CLI for Optimizer"""
    parser = argparse.ArgumentParser(
        description="Sequence optimizer for protein design",
        epilog="Example: uht-optimizer --project my_project"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    cfg["optimizer_project_directory"] = args.project
    
    optimizer_run(cfg)

def mutation_tester_cli():
    """CLI for Mutation Tester"""
    parser = argparse.ArgumentParser(
        description="Test mutations and evaluate their effects",
        epilog="Example: uht-mutation --project my_project"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    cfg["mutation_tester_project_directory"] = args.project
    
    mutation_tester_run(cfg)

def comprehensive_cli():
    """CLI for Comprehensive Clustering Analysis"""
    parser = argparse.ArgumentParser(
        description="Comprehensive clustering analysis with multiple methods and benchmarking",
        epilog="Example: uht-comprehensive --project my_project --n-clusters 5"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--n-clusters", type=int, default=5, 
                       help="Number of clusters for analysis (default: 5)")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda", "mps"],
                       help="Device to use for computation (default: cpu)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    
    # Find FASTA files in the project directory
    input_dir = Path("inputs") / "comprehensive_clustering" / args.project
    if not input_dir.exists():
        # Try alternative location
        input_dir = Path("inputs") / "plmclustv2" / args.project
    
    fasta_paths = sorted(glob.glob(str(input_dir / "*.fasta")))
    if not fasta_paths:
        print(f"Error: No FASTA files found in {input_dir}")
        sys.exit(1)
    
    # Run pipeline
    pipeline = ComprehensiveBenchmarkingPipeline(args.config)
    try:
        pipeline.run_comprehensive_benchmarking(
            target=args.project,
            fasta_paths=fasta_paths,
            n_clusters=args.n_clusters,
            device=args.device
        )
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def biophysical_cli():
    """CLI for Biophysical Signals Analysis"""
    parser = argparse.ArgumentParser(
        description="Analyze biophysical signals in protein sequences",
        epilog="Example: uht-biophysical --project my_project"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    cfg["biophysical_signals_project_directory"] = args.project
    
    biophysical_run(cfg)

def sequence_similarity_cli():
    """CLI for Sequence Similarity Analysis"""
    parser = argparse.ArgumentParser(
        description="Analyze sequence similarity between proteins",
        epilog="Example: uht-sequence --project my_project"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    cfg["sequence_similarity_project_directory"] = args.project
    
    sequence_similarity_run(cfg)

def phylo_cli():
    """CLI for Phylogenetic Analysis"""
    parser = argparse.ArgumentParser(
        description="Phylogenetic analysis and tree construction",
        epilog="Example: uht-phylo --project my_project"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--keep-separate", action="store_true", 
                       help="Process each input FASTA file separately (OPTIONAL)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    cfg["phylo_project_directory"] = args.project
    cfg["phylo_keepseparate"] = args.keep_separate
    
    phylo_run(cfg)

def tsne_cli():
    """CLI for t-SNE Visualization"""
    parser = argparse.ArgumentParser(
        description="Generate t-SNE visualization of sequence embeddings",
        epilog="Example: uht-tsne --project my_project"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    cfg["tsnereplicate_project_directory"] = args.project
    
    tsne_run(cfg)

def kmeansbenchmark_cli():
    """CLI for K-Means Benchmark"""
    parser = argparse.ArgumentParser(
        description="Benchmark K-means clustering with various parameters",
        epilog="Example: uht-kmeans --project my_project --k-range 2 20 --n-runs 20"
    )
    parser.add_argument("--project", required=True, help="Project name (REQUIRED)")
    parser.add_argument("--k-range", nargs=2, type=int, metavar=("MIN", "MAX"), default=[2, 10], 
                       help="Range of k values to test: MIN MAX (default: 2 10)")
    parser.add_argument("--n-runs", type=int, default=10, 
                       help="Number of runs per k value (default: 10)")
    parser.add_argument("--run-controls", action="store_true", 
                       help="Run control experiments (OPTIONAL)")
    parser.add_argument("--compare-algorithms", action="store_true", 
                       help="Compare different clustering algorithms (OPTIONAL)")
    parser.add_argument("--keep-separate", action="store_true", 
                       help="Process each input FASTA file separately (OPTIONAL)")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    
    args = parser.parse_args()
    cfg = load_config_file(args.config)
    cfg.update({
        "kmeansbenchmark_project_directory": args.project,
        "kmeansbenchmark_k_range": args.k_range,
        "kmeansbenchmark_n_runs": args.n_runs,
        "kmeansbenchmark_run_controls": args.run_controls,
        "kmeansbenchmark_compare_algorithms": args.compare_algorithms,
        "kmeansbenchmark_keepseparate": args.keep_separate,
    })
    
    kmeansbenchmark_run(cfg)

def gui_main():
    """Launch the GUI"""
    from uht_discovery.gui import main as gui_main_func
    gui_main_func()

def main():
    """Main entry point for uht-discovery CLI with subcommands"""
    parser = argparse.ArgumentParser(
        prog="uht-discovery",
        description="UHT Discovery - Semi-automated protein discovery pipeline",
        epilog="""
═══════════════════════════════════════════════════════════════════════════════
AVAILABLE SUBCOMMANDS:
═══════════════════════════════════════════════════════════════════════════════

  blast          BLAST sequence search against NCBI databases
  trim           Sequence quality control and length-based trimming
  clust          Protein language model clustering (plmclustv2 - recommended)
  clust-v1       Protein language model clustering (plmclust v1 - legacy)
  optimizer      Sequence optimizer for protein design
  mutation       Test mutations and evaluate their effects
  comprehensive  Comprehensive clustering analysis with benchmarking
  biophysical    Analyze biophysical signals in protein sequences
  sequence       Analyze sequence similarity between proteins
  phylo          Phylogenetic analysis and tree construction
  tsne           Generate t-SNE visualization of sequence embeddings
  kmeans         Benchmark K-means clustering with various parameters
  gui            Launch the interactive web-based GUI

═══════════════════════════════════════════════════════════════════════════════
EXAMPLES:
═══════════════════════════════════════════════════════════════════════════════

  uht-discovery blast --project my_project --email user@example.com
  uht-discovery trim --project my_project --auto
  uht-discovery clust --project my_project --clusters auto
  uht-discovery gui

═══════════════════════════════════════════════════════════════════════════════
For detailed help on a specific subcommand:
  uht-discovery <subcommand> --help
═══════════════════════════════════════════════════════════════════════════════
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "subcommand",
        nargs="?",
        choices=[
            "blast", "trim", "clust", "clust-v1", "optimizer", "mutation",
            "comprehensive", "biophysical", "sequence", "phylo", "tsne",
            "kmeans", "gui"
        ],
        help="Subcommand to run"
    )
    
    # Parse known args to get subcommand
    args, remaining = parser.parse_known_args()
    
    if not args.subcommand:
        parser.print_help()
        sys.exit(1)
    
    # Map subcommands to functions
    subcommand_map = {
        "blast": blaster_cli,
        "trim": trim_cli,
        "clust": plmclustv2_cli,
        "clust-v1": plmclust_cli,
        "optimizer": optimizer_cli,
        "mutation": mutation_tester_cli,
        "comprehensive": comprehensive_cli,
        "biophysical": biophysical_cli,
        "sequence": sequence_similarity_cli,
        "phylo": phylo_cli,
        "tsne": tsne_cli,
        "kmeans": kmeansbenchmark_cli,
        "gui": gui_main,
    }
    
    # Call the appropriate function
    func = subcommand_map[args.subcommand]
    # Restore sys.argv for the subcommand (remove 'uht-discovery' and subcommand)
    sys.argv = [sys.argv[0].split('/')[-1] if '/' in sys.argv[0] else sys.argv[0]] + remaining
    func()

if __name__ == "__main__":
    main()

