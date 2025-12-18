#!/usr/bin/env python3
"""
Port script to transfer data from plmclustv2 output to input directories
for biophysical_signals and sequence_similarity analysis.

This script takes the cluster outputs from plmclustv2 and organizes them
into the expected input structure for downstream analysis.
"""

import os
import shutil
import glob
import argparse
from pathlib import Path


def port_plmclustv2_to_analyses(project_name, plmclustv2_results_dir, 
                                biophysical_signals_input_dir, sequence_similarity_input_dir):
    """
    Port data from plmclustv2 output to analysis input directories.
    
    Args:
        project_name: Name of the project (e.g., 'GH_sampled')
        plmclustv2_results_dir: Path to plmclustv2 results directory
        biophysical_signals_input_dir: Path to biophysical_signals input directory
        sequence_similarity_input_dir: Path to sequence_similarity input directory
    """
    
    # Construct full paths
    plmclustv2_project_dir = os.path.join(plmclustv2_results_dir, project_name)
    
    if not os.path.exists(plmclustv2_project_dir):
        print(f"Error: plmclustv2 project directory not found: {plmclustv2_project_dir}")
        return False
    
    print(f"Porting data from: {plmclustv2_project_dir}")
    
    # Find all subdirectories in the plmclustv2 project
    subdirs = [d for d in os.listdir(plmclustv2_project_dir) 
               if os.path.isdir(os.path.join(plmclustv2_project_dir, d))]
    
    print(f"Found {len(subdirs)} subdirectories to process")
    
    total_clusters = 0
    processed_subdirs = 0
    
    for subdir in subdirs:
        subdir_path = os.path.join(plmclustv2_project_dir, subdir)
        
        # Look for cluster directories (e.g., "6_clusters_GH1_sequences_trimmed")
        cluster_dirs = [d for d in os.listdir(subdir_path) 
                       if '_clusters_' in d and os.path.isdir(os.path.join(subdir_path, d))]
        
        if not cluster_dirs:
            print(f"  Skipping {subdir}: No cluster directory found")
            continue
        
        # Use the first cluster directory found
        cluster_dir = cluster_dirs[0]
        cluster_dir_path = os.path.join(subdir_path, cluster_dir)
        
        # Find all cluster FASTA files
        cluster_files = glob.glob(os.path.join(cluster_dir_path, "cluster_*.fasta"))
        
        if not cluster_files:
            print(f"  Skipping {subdir}: No cluster FASTA files found in {cluster_dir}")
            continue
        
        print(f"  Processing {subdir}: {len(cluster_files)} clusters")
        
        # Create subdirectory-specific folders in both input directories
        biophys_subdir = os.path.join(biophysical_signals_input_dir, project_name, subdir)
        seqsim_subdir = os.path.join(sequence_similarity_input_dir, project_name, subdir)
        
        os.makedirs(biophys_subdir, exist_ok=True)
        os.makedirs(seqsim_subdir, exist_ok=True)
        
        # Copy cluster files to both output directories
        for cluster_file in cluster_files:
            cluster_filename = os.path.basename(cluster_file)
            
            # Copy to biophysical_signals subdirectory
            biophys_dest = os.path.join(biophys_subdir, cluster_filename)
            shutil.copy2(cluster_file, biophys_dest)
            
            # Copy to sequence_similarity subdirectory
            seqsim_dest = os.path.join(seqsim_subdir, cluster_filename)
            shutil.copy2(cluster_file, seqsim_dest)
            
            total_clusters += 1
        
        processed_subdirs += 1
    
    print(f"\nPorting completed successfully!")
    print(f"Processed {processed_subdirs} subdirectories")
    print(f"Total cluster files copied: {total_clusters}")
    print(f"Files copied to:")
    print(f"  - Biophysical signals: {biophysical_signals_input_dir}/{project_name}/")
    print(f"  - Sequence similarity: {sequence_similarity_input_dir}/{project_name}/")
    
    return True


def main():
    """Main function to handle command line arguments and run the porting process."""
    
    parser = argparse.ArgumentParser(
        description="Port data from plmclustv2 output to analysis input directories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Port GH_sampled project data
  python core/port.py GH_sampled
  
  # Port with custom paths
  python core/port.py GH_sampled --plmclustv2-results results/plmclustv2 \\
                                 --biophysical-signals inputs/biophysical_signals \\
                                 --sequence-similarity inputs/sequence_similarity
        """
    )
    
    parser.add_argument("project_name", 
                       help="Name of the project to port (e.g., 'GH_sampled')")
    
    parser.add_argument("--plmclustv2-results", 
                       default="results/plmclustv2",
                       help="Path to plmclustv2 results directory (default: results/plmclustv2)")
    
    parser.add_argument("--biophysical-signals", 
                       default="inputs/biophysical_signals",
                       help="Path to biophysical_signals input directory (default: inputs/biophysical_signals)")
    
    parser.add_argument("--sequence-similarity", 
                       default="inputs/sequence_similarity",
                       help="Path to sequence_similarity input directory (default: inputs/sequence_similarity)")
    
    args = parser.parse_args()
    
    # Validate paths
    if not os.path.exists(args.plmclustv2_results):
        print(f"Error: plmclustv2 results directory not found: {args.plmclustv2_results}")
        return 1
    
    if not os.path.exists(args.biophysical_signals):
        print(f"Error: biophysical_signals input directory not found: {args.biophysical_signals}")
        return 1
    
    if not os.path.exists(args.sequence_similarity):
        print(f"Error: sequence_similarity input directory not found: {args.sequence_similarity}")
        return 1
    
    # Run the porting process
    success = port_plmclustv2_to_analyses(
        args.project_name,
        args.plmclustv2_results,
        args.biophysical_signals,
        args.sequence_similarity
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
