#!/usr/bin/env python3
"""
Sequence Similarity Analysis
Core module for analyzing sequence similarity within and between clusters

This module provides analysis of sequence similarity patterns
within and between protein clusters using MAFFT multiple sequence alignment.
It generates publication-grade visualizations including heatmaps, distribution plots, 
and statistical summaries.

Key Features:
- Calculates pairwise sequence similarities using MAFFT multiple sequence alignment
- Uses caching to avoid recomputing alignments for improved performance
- Handles gaps and insertions/deletions properly
- Limits analysis to 10,000 pairs to avoid memory issues
- Generates publication-grade visualizations (heatmaps, distribution plots)
- Provides statistical analysis with significance testing
- Follows codebase conventions for modularity and configurability

Sequence Similarity Calculation:
- Uses MAFFT multiple sequence alignment with optimized parameters
- Caches alignment results to avoid recomputation
- Similarity = (exact matches) / (total aligned positions excluding gaps)
- Fallback to Biopython PairwiseAligner if MAFFT unavailable
- Final fallback to simple character matching if all else fails

Performance Optimizations:
- Alignment caching to avoid recomputing identical pairs
- Fast MAFFT parameters (--auto, --maxiterate 0)
- Timeout protection (30s per alignment)
- Batch processing capability for multiple sequences
- Efficient parsing of MAFFT output

Usage:
    python run.py sequence_similarity

Configuration:
    Add to config.yaml:
    sequence_similarity_project_directory: gh1

Input:
    - FASTA files in inputs/sequence_similarity/{project}/
    - Each .fasta file represents a cluster

Output:
    - results/sequence_similarity/{project}/
    - sequence_similarity_heatmap_{project}.png
    - sequence_similarity_distribution_{project}.png
    - sequence_similarity_matrix_{project}.png
    - sequence_similarity_summary_{project}.csv
    - sequence_similarity_detailed_{project}.csv

Author: AI Assistant
Date: 2024
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from Bio import SeqIO
from collections import defaultdict
from tqdm import tqdm
import warnings
from .common import project_dir
import random
from scipy.stats import mannwhitneyu, ttest_ind
from sklearn.metrics import pairwise_distances
import itertools

# Set publication-quality plotting style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['figure.dpi'] = 300

warnings.filterwarnings('ignore')

def load_sequences_from_fasta(fasta_file):
    """
    Load sequences from a FASTA file.
    Returns lists of headers and sequences.
    """
    headers, sequences = [], []
    for record in SeqIO.parse(fasta_file, 'fasta'):
        headers.append(record.description)
        sequences.append(str(record.seq))
    return headers, sequences

def calculate_sequence_similarity_mafft_batch(sequences, headers=None):
    """
    Calculate pairwise similarities for multiple sequences using MAFFT batch processing.
    This is much more efficient than pairwise alignments.
    
    Args:
        sequences: List of sequences to compare
        headers: Optional list of headers for the sequences
    
    Returns:
        similarity_matrix: numpy array of pairwise similarities
    """
    try:
        import subprocess
        import tempfile
        import os
        from Bio import AlignIO
        import numpy as np
        
        n_sequences = len(sequences)
        similarity_matrix = np.zeros((n_sequences, n_sequences))
        
        # Create temporary FASTA file with all sequences
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_fasta:
            for i, seq in enumerate(sequences):
                header = headers[i] if headers else f"seq_{i}"
                temp_fasta.write(f">{header}\n{seq}\n")
            temp_fasta_path = temp_fasta.name
        
        try:
            # Run MAFFT alignment on all sequences at once
            cmd = [
                'mafft', 
                '--quiet',  # Suppress output
                '--auto',   # Auto-select best algorithm
                '--maxiterate', '0',  # No iterations for speed
                '--thread', '1',  # Single thread for consistency
                temp_fasta_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout for batch alignment
            )
            
            if result.returncode != 0:
                print("Warning: MAFFT batch alignment failed, using pairwise method")
                return None
            
            # Parse the alignment
            alignment_lines = result.stdout.strip().split('\n')
            if len(alignment_lines) < n_sequences * 2:
                print("Warning: MAFFT batch alignment failed, using pairwise method")
                return None
            
            # Extract aligned sequences
            aligned_sequences = []
            current_seq = ""
            seq_count = 0
            
            for line in alignment_lines:
                if line.startswith('>'):
                    if current_seq:
                        aligned_sequences.append(current_seq)
                        current_seq = ""
                        seq_count += 1
                elif line.strip() and not line.startswith('>'):
                    current_seq += line.strip()
            
            # Add the last sequence
            if current_seq:
                aligned_sequences.append(current_seq)
            
            if len(aligned_sequences) != n_sequences:
                print("Warning: MAFFT batch alignment failed, using pairwise method")
                return None
            
            # Calculate pairwise similarities from the alignment
            for i in range(n_sequences):
                for j in range(i+1, n_sequences):
                    seq1 = aligned_sequences[i]
                    seq2 = aligned_sequences[j]
                    
                    # Calculate similarity based on aligned positions
                    matches = 0
                    total_aligned = 0
                    
                    for a, b in zip(seq1, seq2):
                        if a != '-' and b != '-':  # Both positions are not gaps
                            total_aligned += 1
                            if a == b:  # Exact match
                                matches += 1
                    
                    # Calculate similarity
                    if total_aligned == 0:
                        similarity = 0.0
                    else:
                        similarity = matches / total_aligned
                    
                    # Store in matrix (symmetric)
                    similarity_matrix[i, j] = similarity
                    similarity_matrix[j, i] = similarity
            
            # Set diagonal to 1.0 (self-similarity)
            np.fill_diagonal(similarity_matrix, 1.0)
            
            return similarity_matrix
            
        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_fasta_path)
            except:
                pass
                
    except Exception as e:
        print(f"Warning: MAFFT batch alignment failed ({e}), using pairwise method")
        return None

def calculate_sequence_similarity_mafft_fast(seq1, seq2, alignment_cache=None):
    """
    Calculate sequence similarity using MAFFT with caching for efficiency.
    Returns similarity score between 0 and 1.
    
    This optimized version:
    - Uses caching to avoid recomputing alignments
    - Uses faster MAFFT parameters
    - Handles edge cases efficiently
    """
    try:
        import subprocess
        import tempfile
        import os
        import hashlib
        from Bio import AlignIO
        
        # Create cache key for this pair
        if alignment_cache is not None:
            # Sort sequences for consistent cache key
            if seq1 < seq2:
                seq_pair = (seq1, seq2)
            else:
                seq_pair = (seq2, seq1)
            
            cache_key = hashlib.md5(f"{seq_pair[0]}|{seq_pair[1]}".encode()).hexdigest()
            
            # Check if alignment is already cached
            if cache_key in alignment_cache:
                return alignment_cache[cache_key]
        
        # For very short sequences, use direct comparison
        if len(seq1) < 10 or len(seq2) < 10:
            min_len = min(len(seq1), len(seq2))
            matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
            similarity = matches / min_len if min_len > 0 else 0.0
            
            if alignment_cache is not None:
                alignment_cache[cache_key] = similarity
            return similarity
        
        # Create temporary files for MAFFT input and output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_fasta:
            # Write sequences to temporary FASTA file
            temp_fasta.write(f">seq1\n{seq1}\n")
            temp_fasta.write(f">seq2\n{seq2}\n")
            temp_fasta_path = temp_fasta.name
        
        try:
            # Run MAFFT with optimized parameters for speed
            cmd = [
                'mafft', 
                '--quiet',  # Suppress output
                '--auto',   # Auto-select best algorithm
                '--maxiterate', '0',  # No iterations for speed
                '--thread', '1',  # Single thread for consistency
                temp_fasta_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30  # Timeout after 30 seconds
            )
            
            if result.returncode != 0:
                # MAFFT failed, use fallback
                return calculate_sequence_similarity_fallback(seq1, seq2)
            
            # Parse the alignment from stdout
            alignment_lines = result.stdout.strip().split('\n')
            if len(alignment_lines) < 4:
                return calculate_sequence_similarity_fallback(seq1, seq2)
            
            # Extract aligned sequences using Bio.AlignIO
            try:
                # Write alignment to temporary file for Bio.AlignIO
                with tempfile.NamedTemporaryFile(mode='w', suffix='.aln', delete=False) as temp_aln:
                    temp_aln.write(result.stdout)
                    temp_aln_path = temp_aln.name
                
                # Parse with Bio.AlignIO
                alignment = AlignIO.read(temp_aln_path, 'fasta')
                
                if len(alignment) < 2:
                    return calculate_sequence_similarity_fallback(seq1, seq2)
                
                # Get aligned sequences
                aligned_seq1 = str(alignment[0].seq)
                aligned_seq2 = str(alignment[1].seq)
                
                # Clean up temporary alignment file
                try:
                    os.unlink(temp_aln_path)
                except:
                    pass
                
            except:
                # Fallback parsing if Bio.AlignIO fails
                aligned_seq1 = ""
                aligned_seq2 = ""
                current_seq = None
                
                for line in alignment_lines:
                    if line.startswith('>seq1'):
                        current_seq = 1
                    elif line.startswith('>seq2'):
                        current_seq = 2
                    elif line.strip() and not line.startswith('>'):
                        if current_seq == 1:
                            aligned_seq1 += line.strip()
                        elif current_seq == 2:
                            aligned_seq2 += line.strip()
                
                if not aligned_seq1 or not aligned_seq2:
                    return calculate_sequence_similarity_fallback(seq1, seq2)
            
            # Calculate similarity based on aligned positions
            matches = 0
            total_aligned = 0
            
            for a, b in zip(aligned_seq1, aligned_seq2):
                if a != '-' and b != '-':  # Both positions are not gaps
                    total_aligned += 1
                    if a == b:  # Exact match
                        matches += 1
            
            # Return similarity as fraction of matches
            if total_aligned == 0:
                similarity = 0.0
            else:
                similarity = matches / total_aligned
            
            # Cache the result
            if alignment_cache is not None:
                alignment_cache[cache_key] = similarity
            
            return similarity
            
        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_fasta_path)
            except:
                pass
                
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ImportError) as e:
        # MAFFT failed, use fallback
        return calculate_sequence_similarity_fallback(seq1, seq2)
    except Exception as e:
        # Any other error, use fallback
        return calculate_sequence_similarity_fallback(seq1, seq2)

def calculate_sequence_similarity_fallback(seq1, seq2):
    """
    Fallback sequence similarity calculation using Biopython's PairwiseAligner.
    Used when MAFFT is not available or fails.
    """
    try:
        from Bio.Align import PairwiseAligner
        from Bio.Align import substitution_matrices
        
        # Initialize the aligner
        aligner = PairwiseAligner()
        
        # Use BLOSUM62 scoring matrix for biologically meaningful scoring
        try:
            aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
        except:
            # Fallback to simple scoring if BLOSUM62 not available
            aligner.match_score = 1.0
            aligner.mismatch_score = -1.0
        
        # Set gap penalties (standard values)
        aligner.open_gap_score = -11.0
        aligner.extend_gap_score = -1.0
        
        # Perform global alignment
        alignments = aligner.align(seq1, seq2)
        
        if not alignments:
            return 0.0
        
        # Get the best alignment
        best_alignment = alignments[0]
        
        # Calculate similarity based on aligned positions
        aligned_seq1 = best_alignment.target
        aligned_seq2 = best_alignment.query
        
        # Count matches and total aligned positions (excluding gaps)
        matches = 0
        total_aligned = 0
        
        for a, b in zip(aligned_seq1, aligned_seq2):
            if a != '-' and b != '-':  # Both positions are not gaps
                total_aligned += 1
                if a == b:  # Exact match
                    matches += 1
        
        # Return similarity as fraction of matches
        if total_aligned == 0:
            return 0.0
        
        similarity = matches / total_aligned
        return similarity
        
    except ImportError:
        # Final fallback to simple character matching
        print("Warning: Biopython not available, using simple character matching")
        min_len = min(len(seq1), len(seq2))
        if min_len == 0:
            return 0
        
        matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
        return matches / min_len if min_len > 0 else 0
    except Exception as e:
        print(f"Warning: Alignment failed, using simple character matching: {e}")
        # Final fallback to simple character matching
        min_len = min(len(seq1), len(seq2))
        if min_len == 0:
            return 0
        
        matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
        return matches / min_len if min_len > 0 else 0

def calculate_sequence_similarity(seq1, seq2):
    """
    Calculate sequence similarity using MAFFT multiple sequence alignment.
    Returns similarity score between 0 and 1.
    
    This is the main function that uses MAFFT for high-quality alignment
    and falls back to Biopython's PairwiseAligner if MAFFT fails.
    """
    return calculate_sequence_similarity_mafft_fast(seq1, seq2)

def load_clusters(cluster_dir):
    """
    Load all clusters from the specified directory.
    Returns a dictionary mapping cluster_id to (headers, sequences).
    """
    clusters = {}
    fasta_files = sorted(glob.glob(os.path.join(cluster_dir, '*.fasta')))
    
    print(f"Loading {len(fasta_files)} clusters from {cluster_dir}")
    
    for fasta_file in fasta_files:
        cluster_id = os.path.basename(fasta_file).replace('.fasta', '')
        headers, sequences = load_sequences_from_fasta(fasta_file)
        clusters[cluster_id] = (headers, sequences)
        print(f"  Loaded {cluster_id}: {len(sequences)} sequences")
    
    return clusters

def calculate_pairwise_similarities(clusters, max_pairs=1000):
    """
    Calculate pairwise similarities within and between clusters.
    Limits the number of pairs to avoid memory issues.
    Uses caching for MAFFT alignments to improve performance.
    Implements balanced sampling to ensure equal representation of within and between cluster pairs.
    """
    print("Calculating pairwise similarities...")
    
    # Collect all sequences with their cluster information
    all_sequences = []
    all_headers = []
    cluster_labels = []
    
    for cluster_id, (headers, sequences) in clusters.items():
        for header, seq in zip(headers, sequences):
            all_sequences.append(seq)
            all_headers.append(header)
            cluster_labels.append(cluster_id)
    
    n_sequences = len(all_sequences)
    print(f"Total sequences: {n_sequences}")
    
    # Calculate total possible pairs
    total_pairs = n_sequences * (n_sequences - 1) // 2
    
    if total_pairs > max_pairs:
        print(f"Limiting to {max_pairs} pairs (from {total_pairs} total possible pairs)")
        
        # Implement balanced sampling: 50% within-cluster, 50% between-cluster
        max_pairs_per_type = max_pairs // 2
        
        pairs = []
        
        # Sample within-cluster pairs (50% of total)
        within_pairs = []
        for cluster_id in clusters.keys():
            cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
            if len(cluster_indices) > 1:
                cluster_pairs = list(itertools.combinations(cluster_indices, 2))
                within_pairs.extend(cluster_pairs)
        
        # Sample within-cluster pairs
        if len(within_pairs) > max_pairs_per_type:
            within_pairs = random.sample(within_pairs, max_pairs_per_type)
        pairs.extend(within_pairs)
        
        # Sample between-cluster pairs (50% of total)
        between_pairs = []
        for i, j in itertools.combinations(range(n_sequences), 2):
            if cluster_labels[i] != cluster_labels[j]:
                between_pairs.append((i, j))
        
        if len(between_pairs) > max_pairs_per_type:
            between_pairs = random.sample(between_pairs, max_pairs_per_type)
        pairs.extend(between_pairs)
        
        # If we don't have enough pairs of one type, fill with the other
        if len(pairs) < max_pairs:
            remaining_pairs_needed = max_pairs - len(pairs)
            if len(within_pairs) < max_pairs_per_type:
                # Need more within-cluster pairs
                additional_within = []
                for cluster_id in clusters.keys():
                    cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
                    if len(cluster_indices) > 1:
                        cluster_pairs = list(itertools.combinations(cluster_indices, 2))
                        # Remove already sampled pairs
                        existing_pairs = set(pairs)
                        new_pairs = [p for p in cluster_pairs if p not in existing_pairs]
                        if new_pairs:
                            additional_within.extend(new_pairs)
                
                if additional_within:
                    if len(additional_within) > remaining_pairs_needed:
                        additional_within = random.sample(additional_within, remaining_pairs_needed)
                    pairs.extend(additional_within)
            
            elif len(between_pairs) < max_pairs_per_type:
                # Need more between-cluster pairs
                additional_between = []
                for i, j in itertools.combinations(range(n_sequences), 2):
                    if cluster_labels[i] != cluster_labels[j]:
                        if (i, j) not in pairs:
                            additional_between.append((i, j))
                
                if additional_between:
                    if len(additional_between) > remaining_pairs_needed:
                        additional_between = random.sample(additional_between, remaining_pairs_needed)
                    pairs.extend(additional_between)
        
        # Shuffle to avoid bias
        random.shuffle(pairs)
    else:
        # Use all pairs
        pairs = list(itertools.combinations(range(n_sequences), 2))
    
    print(f"Calculating similarities for {len(pairs)} pairs...")
    
    # Initialize alignment cache for MAFFT
    alignment_cache = {}
    
    # Calculate similarities
    similarities = []
    pair_info = []
    
    for i, j in tqdm(pairs, desc="Computing similarities"):
        similarity = calculate_sequence_similarity_mafft_fast(
            all_sequences[i], 
            all_sequences[j], 
            alignment_cache=alignment_cache
        )
        similarities.append(similarity)
        
        cluster_i = cluster_labels[i]
        cluster_j = cluster_labels[j]
        pair_type = 'within' if cluster_i == cluster_j else 'between'
        
        pair_info.append({
            'seq1_idx': i,
            'seq2_idx': j,
            'seq1_header': all_headers[i],
            'seq2_header': all_headers[j],
            'cluster1': cluster_i,
            'cluster2': cluster_j,
            'pair_type': pair_type,
            'similarity': similarity
        })
    
    print(f"Alignment cache size: {len(alignment_cache)} entries")
    
    # Print sampling statistics
    within_count = sum(1 for p in pair_info if p['pair_type'] == 'within')
    between_count = sum(1 for p in pair_info if p['pair_type'] == 'between')
    print(f"Sampling distribution: {within_count} within-cluster pairs, {between_count} between-cluster pairs")
    
    return pd.DataFrame(pair_info), all_sequences, all_headers, cluster_labels

def create_similarity_heatmap(similarity_df, results_dir, target):
    """
    Create a publication-grade heatmap of sequence similarities.
    """
    print("Creating similarity heatmap...")
    
    # Create pivot table for heatmap
    pivot_data = similarity_df.pivot_table(
        values='similarity',
        index='cluster1',
        columns='cluster2',
        aggfunc='mean'
    )
    
    # Fill diagonal with NaN for better visualization
    np.fill_diagonal(pivot_data.values, np.nan)
    
    # Save the matrix as CSV for re-plotting
    matrix_csv_path = os.path.join(results_dir, f'sequence_similarity_matrix_{target}.csv')
    pivot_data.to_csv(matrix_csv_path)
    print(f"Similarity matrix CSV saved to: {matrix_csv_path}")
    
    # Create the heatmap
    plt.figure(figsize=(10, 8))
    
    # Create custom colormap (blue to red)
    cmap = sns.color_palette("RdBu_r", as_cmap=True)
    
    # Create heatmap without annotations
    sns.heatmap(
        pivot_data,
        annot=False,  # Remove score annotations
        cmap=cmap,
        cbar_kws={'label': 'Sequence Similarity'},
        square=True,
        linewidths=0.5,
        linecolor='white'
    )
    
    plt.title(f'Average Sequence Similarity Between Clusters\n{target}', pad=20)
    plt.xlabel('Cluster')
    plt.ylabel('Cluster')
    plt.tight_layout()
    
    # Save the plot
    heatmap_path = os.path.join(results_dir, f'sequence_similarity_heatmap_{target}.png')
    plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Heatmap saved to: {heatmap_path}")
    return heatmap_path

def create_similarity_distribution_plot(similarity_df, results_dir, target):
    """
    Create a publication-grade distribution plot comparing within vs between cluster similarities.
    """
    print("Creating similarity distribution plot...")
    
    # Separate within and between cluster similarities
    within_similarities = similarity_df[similarity_df['pair_type'] == 'within']['similarity']
    between_similarities = similarity_df[similarity_df['pair_type'] == 'between']['similarity']
    
    # Perform statistical test
    try:
        stat, p_value = mannwhitneyu(within_similarities, between_similarities, alternative='greater')
    except:
        stat, p_value = 0, 1
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Violin plot
    data_for_violin = []
    labels_for_violin = []
    
    for similarity_data, label in [(within_similarities, 'Within Clusters'), 
                                  (between_similarities, 'Between Clusters')]:
        if len(similarity_data) > 0:
            data_for_violin.extend(similarity_data)
            labels_for_violin.extend([label] * len(similarity_data))
    
    if data_for_violin:
        violin_df = pd.DataFrame({
            'Similarity': data_for_violin,
            'Type': labels_for_violin
        })
        
        sns.violinplot(data=violin_df, x='Type', y='Similarity', ax=ax1, palette=['#2E86AB', '#A23B72'])
        ax1.set_title('Distribution of Sequence Similarities')
        ax1.set_ylabel('Sequence Similarity')
        ax1.set_xlabel('')
        
        # Add statistical significance
        if p_value < 0.001:
            sig_text = '***'
        elif p_value < 0.01:
            sig_text = '**'
        elif p_value < 0.05:
            sig_text = '*'
        else:
            sig_text = 'ns'
        
        ax1.text(0.5, 0.95, f'p = {p_value:.3e} {sig_text}', 
                transform=ax1.transAxes, ha='center', va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Box plot
    if len(within_similarities) > 0 and len(between_similarities) > 0:
        box_data = [within_similarities, between_similarities]
        box_labels = ['Within Clusters', 'Between Clusters']
        
        bp = ax2.boxplot(box_data, labels=box_labels, patch_artist=True)
        bp['boxes'][0].set_facecolor('#2E86AB')
        bp['boxes'][1].set_facecolor('#A23B72')
        
        ax2.set_title('Sequence Similarity Summary Statistics')
        ax2.set_ylabel('Sequence Similarity')
        ax2.set_xlabel('')
        
        # Add mean values
        for i, data in enumerate(box_data):
            mean_val = np.mean(data)
            ax2.text(i+1, mean_val, f'μ={mean_val:.3f}', 
                    ha='center', va='bottom', fontweight='bold')
    
    plt.suptitle(f'Sequence Similarity Analysis: Within vs Between Clusters\n{target}', fontsize=14)
    plt.tight_layout()
    
    # Save the plot
    dist_path = os.path.join(results_dir, f'sequence_similarity_distribution_{target}.png')
    plt.savefig(dist_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Distribution plot saved to: {dist_path}")
    return dist_path

def create_cluster_similarity_matrix(similarity_df, results_dir, target):
    """
    Create a detailed similarity matrix showing all pairwise similarities.
    """
    print("Creating detailed similarity matrix...")
    
    # Get unique clusters
    clusters = sorted(set(similarity_df['cluster1'].unique()) | set(similarity_df['cluster2'].unique()))
    
    # Create similarity matrix
    similarity_matrix = np.zeros((len(clusters), len(clusters)))
    
    for i, cluster1 in enumerate(clusters):
        for j, cluster2 in enumerate(clusters):
            if i == j:
                # Within cluster similarity
                mask = (similarity_df['cluster1'] == cluster1) & (similarity_df['cluster2'] == cluster2)
                if mask.any():
                    similarity_matrix[i, j] = similarity_df[mask]['similarity'].mean()
            else:
                # Between cluster similarity
                mask = ((similarity_df['cluster1'] == cluster1) & (similarity_df['cluster2'] == cluster2)) | \
                       ((similarity_df['cluster1'] == cluster2) & (similarity_df['cluster2'] == cluster1))
                if mask.any():
                    similarity_matrix[i, j] = similarity_df[mask]['similarity'].mean()
    
    # Save the matrix as CSV for re-plotting
    matrix_df = pd.DataFrame(similarity_matrix, index=clusters, columns=clusters)
    matrix_csv_path = os.path.join(results_dir, f'sequence_similarity_detailed_matrix_{target}.csv')
    matrix_df.to_csv(matrix_csv_path)
    print(f"Detailed similarity matrix CSV saved to: {matrix_csv_path}")
    
    # Create the heatmap
    plt.figure(figsize=(12, 10))
    
    # Create custom colormap (blue to red)
    cmap = sns.color_palette("RdBu_r", as_cmap=True)
    
    # Create heatmap without annotations
    sns.heatmap(
        similarity_matrix,
        annot=False,  # Remove score annotations
        cmap=cmap,
        cbar_kws={'label': 'Average Sequence Similarity'},
        square=True,
        linewidths=0.5,
        linecolor='white',
        xticklabels=clusters,
        yticklabels=clusters
    )
    
    plt.title(f'Detailed Sequence Similarity Matrix\n{target}', pad=20)
    plt.xlabel('Cluster')
    plt.ylabel('Cluster')
    plt.tight_layout()
    
    # Save the plot
    matrix_path = os.path.join(results_dir, f'sequence_similarity_matrix_{target}.png')
    plt.savefig(matrix_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Similarity matrix saved to: {matrix_path}")
    return matrix_path

def generate_statistical_summary(similarity_df, results_dir, target):
    """
    Generate statistical summary of the similarity analysis.
    """
    print("Generating statistical summary...")
    
    # Calculate summary statistics
    within_similarities = similarity_df[similarity_df['pair_type'] == 'within']['similarity']
    between_similarities = similarity_df[similarity_df['pair_type'] == 'between']['similarity']
    
    summary_stats = {
        'within_clusters': {
            'count': len(within_similarities),
            'mean': np.mean(within_similarities),
            'std': np.std(within_similarities),
            'median': np.median(within_similarities),
            'min': np.min(within_similarities),
            'max': np.max(within_similarities)
        },
        'between_clusters': {
            'count': len(between_similarities),
            'mean': np.mean(between_similarities),
            'std': np.std(between_similarities),
            'median': np.median(between_similarities),
            'min': np.min(between_similarities),
            'max': np.max(between_similarities)
        }
    }
    
    # Perform statistical tests
    try:
        mw_stat, mw_p = mannwhitneyu(within_similarities, between_similarities, alternative='greater')
        t_stat, t_p = ttest_ind(within_similarities, between_similarities)
    except:
        mw_stat, mw_p = 0, 1
        t_stat, t_p = 0, 1
    
    summary_stats['statistical_tests'] = {
        'mann_whitney_u': {
            'statistic': mw_stat,
            'p_value': mw_p
        },
        't_test': {
            'statistic': t_stat,
            'p_value': t_p
        }
    }
    
    # Save summary to CSV
    summary_df = pd.DataFrame([
        {
            'metric': 'within_clusters',
            'count': summary_stats['within_clusters']['count'],
            'mean': summary_stats['within_clusters']['mean'],
            'std': summary_stats['within_clusters']['std'],
            'median': summary_stats['within_clusters']['median'],
            'min': summary_stats['within_clusters']['min'],
            'max': summary_stats['within_clusters']['max']
        },
        {
            'metric': 'between_clusters',
            'count': summary_stats['between_clusters']['count'],
            'mean': summary_stats['between_clusters']['mean'],
            'std': summary_stats['between_clusters']['std'],
            'median': summary_stats['between_clusters']['median'],
            'min': summary_stats['between_clusters']['min'],
            'max': summary_stats['between_clusters']['max']
        }
    ])
    
    summary_path = os.path.join(results_dir, f'sequence_similarity_summary_{target}.csv')
    summary_df.to_csv(summary_path, index=False)
    
    # Save detailed similarity data
    detailed_path = os.path.join(results_dir, f'sequence_similarity_detailed_{target}.csv')
    similarity_df.to_csv(detailed_path, index=False)
    
    print(f"Summary statistics saved to: {summary_path}")
    print(f"Detailed similarity data saved to: {detailed_path}")
    
    return summary_path, detailed_path

def process_single_unit(unit_name, unit_path, results_base_dir):
    """
    Process a single unit independently.
    
    Args:
        unit_name: Name of the unit
        unit_path: Path to the unit directory containing FASTA files
        results_base_dir: Base results directory
    
    Returns:
        dict with processing results
    """
    import glob
    
    print(f"\nProcessing unit: {unit_name}")
    
    # Create subdirectory for this unit's results
    unit_results_dir = os.path.join(results_base_dir, unit_name)
    os.makedirs(unit_results_dir, exist_ok=True)
    
    # Find all FASTA files in the unit directory
    fasta_files = glob.glob(os.path.join(unit_path, '*.fasta'))
    
    if not fasta_files:
        print(f"  Warning: No FASTA files found in {unit_path}")
        return None
    
    print(f"  Found {len(fasta_files)} cluster files")
    
    try:
        # Load clusters for this unit
        clusters = load_clusters(unit_path)
        
        if not clusters:
            print(f"  Warning: No clusters loaded from {unit_path}")
            return {
                'unit_name': unit_name,
                'unit_path': unit_path,
                'error': 'No clusters loaded',
                'success': False
            }
        
        # Calculate pairwise similarities
        similarity_df, all_sequences, all_headers, cluster_labels = calculate_pairwise_similarities(
            clusters, max_pairs=1000
        )
        
        if similarity_df.empty:
            print(f"  Warning: No similarity data calculated for {unit_name}")
            return {
                'unit_name': unit_name,
                'unit_path': unit_path,
                'error': 'No similarity data calculated',
                'success': False
            }
        
        # Create visualizations
        heatmap_path = create_similarity_heatmap(similarity_df, unit_results_dir, unit_name)
        dist_path = create_similarity_distribution_plot(similarity_df, unit_results_dir, unit_name)
        matrix_path = create_cluster_similarity_matrix(similarity_df, unit_results_dir, unit_name)
        
        # Generate statistical summary
        summary_path, detailed_path = generate_statistical_summary(similarity_df, unit_results_dir, unit_name)
        
        # Calculate key metrics
        within_similarities = similarity_df[similarity_df['pair_type'] == 'within']['similarity']
        between_similarities = similarity_df[similarity_df['pair_type'] == 'between']['similarity']
        
        within_mean = np.mean(within_similarities) if len(within_similarities) > 0 else 0
        between_mean = np.mean(between_similarities) if len(between_similarities) > 0 else 0
        
        print(f"  → Results saved to: {unit_results_dir}")
        print(f"  → Clusters: {len(clusters)}")
        print(f"  → Sequences: {len(all_sequences)}")
        print(f"  → Similarity pairs: {len(similarity_df)}")
        print(f"  → Within-cluster similarity: {within_mean:.3f}")
        print(f"  → Between-cluster similarity: {between_mean:.3f}")
        
        return {
            'unit_name': unit_name,
            'unit_path': unit_path,
            'results_dir': unit_results_dir,
            'num_clusters': len(clusters),
            'num_sequences': len(all_sequences),
            'num_pairs': len(similarity_df),
            'within_similarity_mean': within_mean,
            'between_similarity_mean': between_mean,
            'similarity_difference': within_mean - between_mean,
            'files': {
                'heatmap': heatmap_path,
                'distribution': dist_path,
                'matrix': matrix_path,
                'summary': summary_path,
                'detailed': detailed_path
            },
            'success': True
        }
        
    except Exception as e:
        print(f"   Error processing unit {unit_name}: {str(e)}")
        return {
            'unit_name': unit_name,
            'unit_path': unit_path,
            'error': str(e),
            'success': False
        }

def create_summary_log(all_results, results_dir, project_name, start_time, end_time):
    """Create a summary log for all processed units."""
    os.makedirs(results_dir, exist_ok=True)
    summary_log_path = os.path.join(results_dir, f"summary_log_{project_name}.txt")
    
    successful_results = [r for r in all_results if r['success']]
    failed_results = [r for r in all_results if not r['success']]
    
    with open(summary_log_path, 'w') as log_f:
        log_f.write("Sequence Similarity Analysis Summary\n")
        log_f.write("==================================\n\n")
        log_f.write(f"Run start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Run end:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Duration:  {end_time - start_time}\n\n")
        log_f.write("Configuration:\n")
        log_f.write(f"  PROJECT: {project_name}\n")
        log_f.write(f"  Total units processed: {len(all_results)}\n")
        log_f.write(f"  Successful: {len(successful_results)}\n")
        log_f.write(f"  Failed: {len(failed_results)}\n\n")
        
        if successful_results:
            total_clusters = sum(r['num_clusters'] for r in successful_results)
            total_sequences = sum(r['num_sequences'] for r in successful_results)
            total_pairs = sum(r['num_pairs'] for r in successful_results)
            avg_within = np.mean([r['within_similarity_mean'] for r in successful_results])
            avg_between = np.mean([r['between_similarity_mean'] for r in successful_results])
            
            log_f.write(f"Total clusters across all units: {total_clusters}\n")
            log_f.write(f"Total sequences across all units: {total_sequences}\n")
            log_f.write(f"Total similarity pairs: {total_pairs}\n")
            log_f.write(f"Average within-cluster similarity: {avg_within:.3f}\n")
            log_f.write(f"Average between-cluster similarity: {avg_between:.3f}\n")
            log_f.write(f"Average similarity difference: {avg_within - avg_between:.3f}\n\n")
            
            log_f.write("Successful unit-by-unit results:\n")
            for result in successful_results:
                log_f.write(f"\n  Unit: {result['unit_name']}\n")
                log_f.write(f"    Clusters: {result['num_clusters']}\n")
                log_f.write(f"    Sequences: {result['num_sequences']}\n")
                log_f.write(f"    Similarity pairs: {result['num_pairs']}\n")
                log_f.write(f"    Within-cluster similarity: {result['within_similarity_mean']:.3f}\n")
                log_f.write(f"    Between-cluster similarity: {result['between_similarity_mean']:.3f}\n")
                log_f.write(f"    Similarity difference: {result['similarity_difference']:.3f}\n")
                log_f.write(f"    Results directory: {result['results_dir']}\n")
        
        if failed_results:
            log_f.write(f"\nFailed units:\n")
            for result in failed_results:
                log_f.write(f"\n  Unit: {result['unit_name']}\n")
                log_f.write(f"    Error: {result['error']}\n")
        
        log_f.write(f"\nAll results saved under: {results_dir}\n")
        log_f.write("Each successful unit has its own subdirectory with complete sequence similarity analysis.\n")
    
    print(f"Summary log saved to: {summary_log_path}")

def run(cfg):
    """
    Main function to run sequence similarity analysis.
    """
    import glob
    import datetime
    
    # Get project directory from config
    target = project_dir('sequence_similarity', cfg)
    if not target:
        raise ValueError("Need sequence_similarity_project_directory in config or SEQUENCE_SIMILARITY_PROJECT_ID environment variable")
    
    # Construct paths
    input_dir = os.path.join('inputs', 'sequence_similarity', target)
    results_dir = os.path.join('results', 'sequence_similarity', target)
    
    print(f"Sequence Similarity Analysis")
    print(f"Project: {target}")
    print(f"Input directory: {input_dir}")
    print(f"Results directory: {results_dir}")
    print()
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Auto-discover unit directories
    unit_dirs = []
    for item in os.listdir(input_dir):
        item_path = os.path.join(input_dir, item)
        if os.path.isdir(item_path):
            # Check if this directory contains FASTA files
            fasta_files = glob.glob(os.path.join(item_path, '*.fasta'))
            if fasta_files:
                unit_dirs.append((item, item_path))
    
    if not unit_dirs:
        print(f"No unit directories with FASTA files found in '{input_dir}'.")
        return
    
    print(f"Found {len(unit_dirs)} unit(s) to process:")
    for unit_name, _ in unit_dirs:
        print(f"  - {unit_name}")
    print()
    
    start_time = datetime.datetime.now()
    
    # Process each unit independently
    all_results = []
    for i, (unit_name, unit_path) in enumerate(unit_dirs, 1):
        print(f"--- Processing unit {i}/{len(unit_dirs)}: {unit_name} ---")
        result = process_single_unit(unit_name, unit_path, results_dir)
        if result:
            all_results.append(result)
    
    # Create summary log
    end_time = datetime.datetime.now()
    create_summary_log(all_results, results_dir, target, start_time, end_time)
    
    print(f"\n=== SUMMARY ===")
    successful_results = [r for r in all_results if r.get('success', False)]
    print(f"Processed {len(successful_results)}/{len(all_results)} units successfully")
    if successful_results:
        total_clusters = sum(r['num_clusters'] for r in successful_results)
        total_sequences = sum(r['num_sequences'] for r in successful_results)
        total_pairs = sum(r['num_pairs'] for r in successful_results)
        avg_within = np.mean([r['within_similarity_mean'] for r in successful_results])
        avg_between = np.mean([r['between_similarity_mean'] for r in successful_results])
        
        print(f"Total clusters: {total_clusters}")
        print(f"Total sequences: {total_sequences}")
        print(f"Total similarity pairs: {total_pairs}")
        print(f"Average within-cluster similarity: {avg_within:.3f}")
        print(f"Average between-cluster similarity: {avg_between:.3f}")
        print(f"Average similarity difference: {avg_within - avg_between:.3f}")
    print(f"Results directory: {results_dir}")
    print(f"Duration: {end_time - start_time}")
    
    return {
        'units_processed': len(all_results),
        'results': all_results,
        'results_dir': results_dir,
        'duration': end_time - start_time
    } 