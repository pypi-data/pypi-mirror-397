#!/usr/bin/env python3
"""
Comprehensive Benchmarking Pipeline for plmclustv2
"""

import os
import yaml
import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

# Import modules
# Note: These modules may not be implemented yet - using try/except for graceful degradation
try:
    from .embedding_methods import benchmark_embedding_methods, compare_embedding_methods
except ImportError:
    benchmark_embedding_methods = None
    compare_embedding_methods = None

try:
    from .state_of_the_art_comparison import benchmark_clustering_methods, create_comparison_report
except ImportError:
    benchmark_clustering_methods = None
    create_comparison_report = None

try:
    from .enzyme_property_analysis import EnzymePropertyAnalyzer, create_sample_enzyme_data
except ImportError:
    EnzymePropertyAnalyzer = None
    create_sample_enzyme_data = None

from .plmclustv2 import load_sequences, compute_embeddings_and_scores, cluster_embeddings

class ComprehensiveBenchmarkingPipeline:
    """Main pipeline for comprehensive benchmarking"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.results_dir = None
        self.target = None
        self.results = {"embedding_benchmarks": {}, "clustering_benchmarks": {}, "enzyme_analysis": {}}
    
    def _load_config(self) -> Dict:
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            return {}
    
    def setup_experiment(self, target: str, results_dir: str = None):
        self.target = target
        self.results_dir = results_dir or os.path.join('results', 'comprehensive_benchmarking', target)
        os.makedirs(self.results_dir, exist_ok=True)
        print(f"Experiment setup: {target} -> {self.results_dir}")
    
    def run_embedding_benchmarks(self, representations: np.ndarray) -> Dict:
        print("\n=== EMBEDDING METHOD BENCHMARKING ===")
        if benchmark_embedding_methods is None or compare_embedding_methods is None:
            raise ImportError("embedding_methods module not found. This feature is not yet implemented.")
        benchmark_results = benchmark_embedding_methods(representations)
        comparison_results = compare_embedding_methods(representations)
        
        self.results["embedding_benchmarks"] = {
            "benchmark_results": benchmark_results,
            "comparison_results": comparison_results
        }
        
        # Save results
        import json
        with open(os.path.join(self.results_dir, "embedding_benchmarks.json"), 'w') as f:
            json.dump(comparison_results, f, indent=2, default=str)
        
        return benchmark_results
    
    def run_clustering_benchmarks(self, sequences: List[str], embeddings: np.ndarray, 
                                n_clusters: int = 5) -> Dict:
        print("\n=== CLUSTERING METHOD BENCHMARKING ===")
        if benchmark_clustering_methods is None or create_comparison_report is None:
            raise ImportError("state_of_the_art_comparison module not found. This feature is not yet implemented.")
        benchmark_results = benchmark_clustering_methods(
            sequences, embeddings, n_clusters=n_clusters
        )
        
        report_df = create_comparison_report(benchmark_results)
        self.results["clustering_benchmarks"] = {
            "benchmark_results": benchmark_results,
            "comparison_report": report_df.to_dict('records')
        }
        
        # Save results
        report_df.to_csv(os.path.join(self.results_dir, "clustering_benchmarks.csv"), index=False)
        
        return benchmark_results
    
    def run_enzyme_analysis(self, cluster_labels: np.ndarray, embeddings: np.ndarray,
                           sequences: List[str], headers: List[str],
                           enzyme_properties: Optional[Dict] = None) -> Dict:
        print("\n=== ENZYME PROPERTY ANALYSIS ===")
        
        if EnzymePropertyAnalyzer is None or create_sample_enzyme_data is None:
            raise ImportError("enzyme_property_analysis module not found. This feature is not yet implemented.")
        analyzer = EnzymePropertyAnalyzer()
        analyzer.set_clustering_data(cluster_labels, embeddings, sequences, headers)
        
        if enzyme_properties is None:
            print("Creating sample enzyme data...")
            enzyme_properties = create_sample_enzyme_data(len(sequences))
        
        for prop_name, prop_values in enzyme_properties.items():
            analyzer.add_property(prop_name, prop_values)
        
        analysis_results = analyzer.run_comprehensive_analysis()
        
        # Create plots
        plots_dir = os.path.join(self.results_dir, "enzyme_analysis_plots")
        plot_paths = analyzer.create_analysis_plots(analysis_results, plots_dir)
        
        self.results["enzyme_analysis"] = {
            "analysis_results": analysis_results,
            "plot_paths": plot_paths
        }
        
        # Save results
        analyzer.save_analysis_results(analysis_results, 
                                     os.path.join(self.results_dir, "enzyme_analysis.json"))
        
        return analysis_results
    
    def run_plmclustv2_analysis(self, fasta_paths: List[str], n_clusters: int = 5, 
                                device: str = 'cpu') -> Dict:
        print("\n=== PLMCLUSTV2 ANALYSIS ===")
        
        # Load sequences
        headers, sequences = [], []
        for fp in fasta_paths:
            hdrs, seqs = load_sequences(fp)
            headers.extend(hdrs)
            sequences.extend(seqs)
        
        print(f"Loaded {len(sequences)} sequences")
        
        # Compute embeddings and scores
        embeddings, scores = compute_embeddings_and_scores(
            headers, sequences, device=device, batch_size=1
        )
        
        # Perform clustering
        cluster_labels = cluster_embeddings(embeddings, n_clusters)
        
        # Save results
        np.save(os.path.join(self.results_dir, "plmclustv2_embeddings.npy"), embeddings)
        np.save(os.path.join(self.results_dir, "plmclustv2_labels.npy"), cluster_labels)
        
        return {
            "headers": headers, "sequences": sequences, "embeddings": embeddings,
            "scores": scores, "cluster_labels": cluster_labels, "n_clusters": n_clusters
        }
    
    def run_comprehensive_benchmarking(self, target: str, fasta_paths: List[str],
                                     n_clusters: int = 5, device: str = 'cpu',
                                     enzyme_properties: Optional[Dict] = None) -> Dict:
        print("="*80)
        print("COMPREHENSIVE BENCHMARKING PIPELINE")
        print(f"Target: {target}, Clusters: {n_clusters}, Device: {device}")
        print("="*80)
        
        # Setup
        self.setup_experiment(target)
        
        # Step 1: plmclustv2 analysis
        plmclustv2_results = self.run_plmclustv2_analysis(fasta_paths, n_clusters, device)
        
        # Step 2: Embedding benchmarks
        self.run_embedding_benchmarks(plmclustv2_results["embeddings"])
        
        # Step 3: Clustering benchmarks
        self.run_clustering_benchmarks(
            plmclustv2_results["sequences"],
            plmclustv2_results["embeddings"],
            n_clusters
        )
        
        # Step 4: Enzyme analysis
        self.run_enzyme_analysis(
            plmclustv2_results["cluster_labels"],
            plmclustv2_results["embeddings"],
            plmclustv2_results["sequences"],
            plmclustv2_results["headers"],
            enzyme_properties
        )
        
        print(f"\nBenchmarking completed! Results saved to: {self.results_dir}")
        return self.results

def main():
    import argparse
    import glob
    
    parser = argparse.ArgumentParser(description="Comprehensive Benchmarking Pipeline")
    parser.add_argument("--target", required=True, help="Target dataset identifier")
    parser.add_argument("--fasta-dir", required=True, help="Directory with FASTA files")
    parser.add_argument("--n-clusters", type=int, default=5, help="Number of clusters")
    parser.add_argument("--device", default="cpu", help="Device (cpu/cuda/mps)")
    
    args = parser.parse_args()
    
    # Find FASTA files
    fasta_paths = sorted(glob.glob(os.path.join(args.fasta_dir, "*.fasta")))
    if not fasta_paths:
        print(f"No FASTA files in {args.fasta_dir}")
        return
    
    # Run pipeline
    pipeline = ComprehensiveBenchmarkingPipeline()
    try:
        results = pipeline.run_comprehensive_benchmarking(
            target=args.target,
            fasta_paths=fasta_paths,
            n_clusters=args.n_clusters,
            device=args.device
        )
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
