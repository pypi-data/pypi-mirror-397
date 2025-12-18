#!/usr/bin/env python3
"""
K-means Reproducibility Assessment Module
Assesses the reproducibility of k-means clustering across different numbers of clusters
"""

import os
import glob
import yaml
import datetime
import torch
import esm
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.cluster import KMeans, AgglomerativeClustering, SpectralClustering
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score
from sklearn.metrics.cluster import contingency_matrix
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt
import seaborn as sns
from .common import project_dir
import time
from Bio.SeqRecord import SeqRecord
import warnings
from itertools import combinations

warnings.filterwarnings('ignore')

# Import the EmbeddingCache class
try:
    from .phylogenetic_analysis import EmbeddingCache
except ImportError:
    # If phylogenetic_analysis is not available, create a simple cache class
    class EmbeddingCache:
        def __init__(self, cache_dir="embeddings/esm2"):
            self.cache_dir = cache_dir
            os.makedirs(cache_dir, exist_ok=True)
            self.db_path = os.path.join(cache_dir, "embeddings.db")
            self._init_database()
        
        def _init_database(self):
            import sqlite3
            import pickle
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        sequence_hash TEXT PRIMARY KEY,
                        sequence TEXT NOT NULL,
                        embedding BLOB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sequence_hash ON embeddings(sequence_hash)")
        
        def _hash_sequence(self, sequence):
            import hashlib
            return hashlib.sha256(sequence.encode()).hexdigest()
        
        def get_embedding(self, sequence):
            import sqlite3
            import pickle
            sequence_hash = self._hash_sequence(sequence)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT embedding FROM embeddings WHERE sequence_hash = ?",
                    (sequence_hash,)
                )
                result = cursor.fetchone()
                if result:
                    return pickle.loads(result[0])
                return None
        
        def store_embedding(self, sequence, embedding):
            import sqlite3
            import pickle
            sequence_hash = self._hash_sequence(sequence)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO embeddings (sequence_hash, sequence, embedding) VALUES (?, ?, ?)",
                    (sequence_hash, sequence, pickle.dumps(embedding))
                )

def load_sequences(fasta_file):
    """
    Load sequences from a single FASTA file.
    Returns lists of headers and sequences.
    """
    sequences, headers = [], []
    with open(fasta_file, 'r') as f:
        seq, header = '', ''
        for line in f:
            if line.startswith('>'):
                if seq:
                    sequences.append(seq)
                    headers.append(header)
                    seq = ''
                header = line.strip()
            else:
                seq += line.strip()
        if seq:
            sequences.append(seq)
            headers.append(header)
    return headers, sequences

def compute_embeddings_and_scores(headers, sequences, device='cpu', batch_size=1):
    """
    Compute both embeddings and single-pass NLL scores in one model pass.
    Uses the caching system to avoid recomputing embeddings.
    Returns tuple of (embeddings, scores) where embeddings is numpy array of shape (N, D).
    """
    # Initialize the embedding cache
    embedding_cache = EmbeddingCache()
    
    # Check cache first
    print("Checking embedding cache...")
    cached_embeddings = {}
    missing_sequences = []
    missing_headers = []
    missing_indices = []
    
    for i, (header, sequence) in enumerate(zip(headers, sequences)):
        embedding = embedding_cache.get_embedding(sequence)
        if embedding is not None:
            cached_embeddings[header] = embedding
        else:
            missing_sequences.append(sequence)
            missing_headers.append(header)
            missing_indices.append(i)
    
    print(f"Found {len(cached_embeddings)} cached embeddings")
    
    # Initialize scores list with placeholders
    all_scores = [0.0] * len(sequences)
    
    if missing_sequences:
        print(f"Generating {len(missing_sequences)} new embeddings...")
        
        # Compute embeddings for missing sequences
        model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
        model.eval().to(device)
        batch_converter = alphabet.get_batch_converter()
        pad_idx = batch_converter.alphabet.padding_idx
        
        new_embeddings = []
        new_scores = []
        
        for i in tqdm(range(0, len(missing_sequences), batch_size), desc="Computing embeddings and scores"):
            batch = list(zip(missing_headers[i:i+batch_size], missing_sequences[i:i+batch_size]))
            labels, strs, tokens = batch_converter(batch)
            tokens = tokens.to(device)
            
            with torch.no_grad():
                # Get both representations and logits in one pass
                out = model(tokens, repr_layers=[33], return_contacts=False)
                
                # Extract embeddings
                reps = out['representations'][33]
                for j, seq in enumerate(strs):
                    emb = reps[j, 1:len(seq)+1].mean(0)
                    new_embeddings.append(emb.cpu().numpy())
                
                # Extract scores
                lps = torch.log_softmax(out["logits"], dim=-1)
                tp = lps.gather(2, tokens.unsqueeze(-1)).squeeze(-1)
                mask = (tokens != pad_idx)
                raw = -(tp * mask).sum(dim=1).cpu().numpy()
                lengths = mask.sum(dim=1).cpu().numpy()
                norm = raw / lengths
                new_scores.extend(norm)
            
            # Memory cleanup
            del out, reps, lps, tp, tokens
            if device == 'mps':
                torch.mps.empty_cache()
        
        # Store new embeddings in cache and update scores
        for header, embedding, score in zip(missing_headers, new_embeddings, new_scores):
            embedding_cache.store_embedding(sequences[headers.index(header)], embedding)
            cached_embeddings[header] = embedding
            # Update the score at the correct index
            idx = headers.index(header)
            all_scores[idx] = score
    
    # For cached embeddings, we need to recompute scores
    if cached_embeddings and len(cached_embeddings) < len(sequences):
        print(f"Recomputing scores for {len(cached_embeddings)} cached embeddings...")
        
        # Get all cached sequences that need scores
        cached_headers = [h for h in headers if h in cached_embeddings]
        cached_sequences = [sequences[headers.index(h)] for h in cached_headers]
        
        # Compute scores for cached sequences
        model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
        model.eval().to(device)
        batch_converter = alphabet.get_batch_converter()
        pad_idx = batch_converter.alphabet.padding_idx
        
        cached_scores = []
        
        for i in tqdm(range(0, len(cached_sequences), batch_size), desc="Computing scores for cached embeddings"):
            batch = list(zip(cached_headers[i:i+batch_size], cached_sequences[i:i+batch_size]))
            labels, strs, tokens = batch_converter(batch)
            tokens = tokens.to(device)
            
            with torch.no_grad():
                # Get logits for score computation
                out = model(tokens, repr_layers=[33], return_contacts=False)
                
                # Extract scores
                lps = torch.log_softmax(out["logits"], dim=-1)
                tp = lps.gather(2, tokens.unsqueeze(-1)).squeeze(-1)
                mask = (tokens != pad_idx)
                raw = -(tp * mask).sum(dim=1).cpu().numpy()
                lengths = mask.sum(dim=1).cpu().numpy()
                norm = raw / lengths
                cached_scores.extend(norm)
            
            # Memory cleanup
            del out, lps, tp, tokens
            if device == 'mps':
                torch.mps.empty_cache()
        
        # Update scores for cached embeddings
        for header, score in zip(cached_headers, cached_scores):
            idx = headers.index(header)
            all_scores[idx] = score
    
    # Combine cached and new embeddings
    embeddings = []
    for header in headers:
        embeddings.append(cached_embeddings[header])
    
    print("  Progress: Done.")
    return np.array(embeddings), all_scores

def cluster_embeddings_with_seed(embeddings, n_clusters, random_state, algorithm='kmeans'):
    """
    Cluster embeddings using specified algorithm with a specific random seed.
    Returns cluster labels.
    
    Spectral Clustering Parameters:
    - affinity: 'nearest_neighbors' (default) or 'rbf' (radial basis function)
    - n_neighbors: Number of neighbors for nearest_neighbors affinity (default: 10)
    - gamma: Kernel coefficient for rbf affinity (default: 1.0)
    - assign_labels: 'kmeans' (default) or 'discretize'
    """
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):
        if algorithm == 'kmeans':
            km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        elif algorithm == 'hierarchical':
            km = AgglomerativeClustering(n_clusters=n_clusters)
        elif algorithm == 'spectral':
            # Spectral clustering with configurable parameters
            km = SpectralClustering(
                n_clusters=n_clusters, 
                random_state=random_state, 
                affinity='nearest_neighbors',
                n_neighbors=10,  # Number of neighbors for graph construction
                assign_labels='kmeans',  # How to assign labels after spectral embedding
                n_init=10  # Number of k-means runs for label assignment
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        return km.fit_predict(embeddings)

def compute_stability_metrics(clusterings):
    """
    Compute stability metrics between multiple clusterings.
    
    Args:
        clusterings: List of cluster label arrays from different runs
        
    Returns:
        dict: Dictionary containing ARI, NMI, and Jaccard similarity matrices
    """
    n_runs = len(clusterings)
    if n_runs < 2:
        return {'ari_matrix': None, 'nmi_matrix': None, 'jaccard_matrix': None}
    
    # Initialize matrices
    ari_matrix = np.zeros((n_runs, n_runs))
    nmi_matrix = np.zeros((n_runs, n_runs))
    jaccard_matrix = np.zeros((n_runs, n_runs))
    
    # Compute pairwise similarities
    for i, j in tqdm(combinations(range(n_runs), 2), 
                    total=n_runs*(n_runs-1)//2, 
                    desc="Computing stability metrics"):
        
        # Adjusted Rand Index
        ari = adjusted_rand_score(clusterings[i], clusterings[j])
        ari_matrix[i, j] = ari
        ari_matrix[j, i] = ari
        
        # Normalized Mutual Information
        nmi = normalized_mutual_info_score(clusterings[i], clusterings[j])
        nmi_matrix[i, j] = nmi
        nmi_matrix[j, i] = nmi
        
        # Jaccard similarity (using pairwise sample similarity)
        # Create pairwise similarity matrices for each clustering
        n_samples = len(clusterings[i])
        
        # Create binary similarity matrices (1 if samples are in same cluster, 0 otherwise)
        sim_i = np.zeros((n_samples, n_samples), dtype=bool)
        sim_j = np.zeros((n_samples, n_samples), dtype=bool)
        
        for row in range(n_samples):
            for col in range(n_samples):
                sim_i[row, col] = clusterings[i][row] == clusterings[i][col]
                sim_j[row, col] = clusterings[j][row] == clusterings[j][col]
        
        # Compute Jaccard similarity between the two similarity matrices
        intersection = np.sum(sim_i & sim_j)
        union = np.sum(sim_i | sim_j)
        jaccard = intersection / union if union > 0 else 0
        
        jaccard_matrix[i, j] = jaccard
        jaccard_matrix[j, i] = jaccard
    
    # Set diagonal to 1.0
    np.fill_diagonal(ari_matrix, 1.0)
    np.fill_diagonal(nmi_matrix, 1.0)
    np.fill_diagonal(jaccard_matrix, 1.0)
    
    return {
        'ari_matrix': ari_matrix,
        'nmi_matrix': nmi_matrix,
        'jaccard_matrix': jaccard_matrix
    }

def assess_clustering_reproducibility(embeddings, k_values, n_runs=10, random_seeds=None, algorithm='kmeans'):
    """
    Assess reproducibility of clustering across different k values.
    
    Args:
        embeddings: numpy array of embeddings
        k_values: list of k values to test
        n_runs: number of runs per k value
        random_seeds: list of random seeds to use (if None, will generate)
        algorithm: clustering algorithm to use ('kmeans', 'hierarchical', 'spectral')
    
    Returns:
        dict: Dictionary containing all results
    """
    if random_seeds is None:
        random_seeds = list(range(42, 42 + n_runs))
    
    results = {
        'k_values': k_values,
        'n_runs': n_runs,
        'random_seeds': random_seeds,
        'algorithm': algorithm,
        'clusterings': {},
        'stability_metrics': {},
        'summary_stats': {}
    }
    
    print(f"Assessing reproducibility across {len(k_values)} k values with {n_runs} runs each using {algorithm}...")
    
    for k in tqdm(k_values, desc="Testing k values"):
        print(f"\nTesting k={k}...")
        
        # Run clustering multiple times
        clusterings_k = []
        run_times_k = {}
        for run_idx in tqdm(range(n_runs), desc=f"Running k={k}"):
            seed = random_seeds[run_idx]
            start_time = time.time()
            labels = cluster_embeddings_with_seed(embeddings, k, seed, algorithm)
            end_time = time.time()
            run_time = end_time - start_time
            clusterings_k.append(labels)
            run_times_k[run_idx] = run_time
        
        # Store clusterings
        results['clusterings'][k] = clusterings_k
        
        # Compute stability metrics
        stability_metrics = compute_stability_metrics(clusterings_k)
        results['stability_metrics'][k] = stability_metrics
        
        # Compute summary statistics
        if stability_metrics['ari_matrix'] is not None:
            ari_values = stability_metrics['ari_matrix'][np.triu_indices_from(stability_metrics['ari_matrix'], k=1)]
            nmi_values = stability_metrics['nmi_matrix'][np.triu_indices_from(stability_metrics['nmi_matrix'], k=1)]
            jaccard_values = stability_metrics['jaccard_matrix'][np.triu_indices_from(stability_metrics['jaccard_matrix'], k=1)]
            
            results['summary_stats'][k] = {
                'ari_mean': np.mean(ari_values),
                'ari_std': np.std(ari_values),
                'ari_cv': np.std(ari_values) / np.mean(ari_values) if np.mean(ari_values) > 0 else 0,
                'nmi_mean': np.mean(nmi_values),
                'nmi_std': np.std(nmi_values),
                'nmi_cv': np.std(nmi_values) / np.mean(nmi_values) if np.mean(nmi_values) > 0 else 0,
                'jaccard_mean': np.mean(jaccard_values),
                'jaccard_std': np.std(jaccard_values),
                'jaccard_cv': np.std(jaccard_values) / np.mean(jaccard_values) if np.mean(jaccard_values) > 0 else 0
            }
        else:
            results['summary_stats'][k] = {
                'ari_mean': 0, 'ari_std': 0, 'ari_cv': 0,
                'nmi_mean': 0, 'nmi_std': 0, 'nmi_cv': 0,
                'jaccard_mean': 0, 'jaccard_std': 0, 'jaccard_cv': 0
            }
    
    return results

# Critical Controls
def generate_random_permutation_control(embeddings, k_values, n_runs=10):
    """
    Control: Randomly permute cluster assignments to establish baseline.
    This tests if observed stability is due to actual structure or chance.
    
    PURPOSE:
    - Tests whether observed clustering stability is due to actual data structure
    - Establishes baseline for "structure-preserving" randomization
    - Helps distinguish between meaningful patterns and chance correlations
    
    METHOD:
    - Randomly permutes the order of samples in the embedding matrix
    - Preserves the overall distribution and dimensionality of the data
    - Maintains the same feature correlations but destroys sample relationships
    
    INTERPRETATION:
    - High stability (close to observed): Data structure is robust to permutation
    - Low stability (close to random): Observed structure is fragile
    - Expected result: Moderate stability (0.3-0.7) for well-structured data
    
    SCIENTIFIC VALUE:
    - Validates that clustering method can detect structure when it exists
    - Tests robustness of observed patterns
    - Helps identify if stability is due to algorithm bias vs. true structure
    """
    print("Generating random permutation control...")
    print("  Purpose: Test if observed stability is due to actual structure or chance")
    print("  Method: Randomly permute sample order while preserving feature distributions")
    print("  Expected: Moderate stability (0.3-0.7) for well-structured data")
    print("  ⚠️  FIXED: Now permutes data DIFFERENTLY for each replicate")
    
    # Create a custom reproducibility function that permutes data for each replicate
    results = {
        'k_values': k_values,
        'n_runs': n_runs,
        'random_seeds': list(range(42, 42 + n_runs)),
        'algorithm': 'kmeans',
        'clusterings': {},
        'stability_metrics': {},
        'summary_stats': {}
    }
    
    print(f"Assessing reproducibility across {len(k_values)} k values with {n_runs} runs each using kmeans...")
    
    for k in tqdm(k_values, desc="Testing k values"):
        print(f"\nTesting k={k}...")
        
        # Run clustering multiple times with DIFFERENT permutations for each run
        clusterings_k = []
        run_times_k = {}
        for run_idx in tqdm(range(n_runs), desc=f"Running k={k}"):
            seed = results['random_seeds'][run_idx]
            
            # Generate NEW permutation for each replicate
            np.random.seed(seed)  # Set seed for reproducible permutation
            permuted_embeddings = np.random.permutation(embeddings)
            
            # Run clustering on this specific permutation
            start_time = time.time()
            labels = cluster_embeddings_with_seed(permuted_embeddings, k, seed, 'kmeans')
            end_time = time.time()
            run_time = end_time - start_time
            clusterings_k.append(labels)
            run_times_k[run_idx] = run_time
        
        # Store clusterings
        results['clusterings'][k] = clusterings_k
        
        # Compute stability metrics
        stability_metrics = compute_stability_metrics(clusterings_k)
        results['stability_metrics'][k] = stability_metrics
        
        # Compute summary statistics
        if stability_metrics['ari_matrix'] is not None:
            ari_values = stability_metrics['ari_matrix'][np.triu_indices_from(stability_metrics['ari_matrix'], k=1)]
            nmi_values = stability_metrics['nmi_matrix'][np.triu_indices_from(stability_metrics['nmi_matrix'], k=1)]
            jaccard_values = stability_metrics['jaccard_matrix'][np.triu_indices_from(stability_metrics['jaccard_matrix'], k=1)]
            
            results['summary_stats'][k] = {
                'ari_mean': np.mean(ari_values),
                'ari_std': np.std(ari_values),
                'ari_cv': np.std(ari_values) / np.mean(ari_values) if np.mean(ari_values) > 0 else 0,
                'nmi_mean': np.mean(nmi_values),
                'nmi_std': np.std(nmi_values),
                'nmi_cv': np.std(nmi_values) / np.mean(nmi_values) if np.mean(nmi_values) > 0 else 0,
                'jaccard_mean': np.mean(jaccard_values),
                'jaccard_std': np.std(jaccard_values),
                'jaccard_cv': np.std(jaccard_values) / np.mean(jaccard_values) if np.mean(jaccard_values) > 0 else 0
            }
        else:
            results['summary_stats'][k] = {
                'ari_mean': 0, 'ari_std': 0, 'ari_cv': 0,
                'nmi_mean': 0, 'nmi_std': 0, 'nmi_cv': 0,
                'jaccard_mean': 0, 'jaccard_std': 0, 'jaccard_cv': 0
            }
    
    return results

def generate_random_data_control(embeddings_shape, k_values, n_runs=10):
    """
    Control: Generate completely random data with same dimensions.
    This establishes the null hypothesis baseline.
    
    PURPOSE:
    - Establishes the null hypothesis baseline (no structure)
    - Tests what stability looks like with completely random data
    - Provides lower bound for meaningful clustering stability
    
    METHOD:
    - Generates random Gaussian data with same shape as embeddings
    - No inherent cluster structure or relationships
    - Tests clustering algorithm's behavior on unstructured data
    
    INTERPRETATION:
    - Very low stability (0.0-0.1): Expected for random data
    - Higher stability (>0.2): Algorithm may be biased or overfitting
    - Expected result: Near-zero stability (0.0-0.05) for truly random data
    
    SCIENTIFIC VALUE:
    - Establishes baseline for "no structure" scenario
    - Helps identify algorithm bias or overfitting
    - Provides context for interpreting observed stability values
    - Critical for determining if observed structure is meaningful
    """
    print("Generating random data control...")
    print("  Purpose: Establish null hypothesis baseline (no structure)")
    print("  Method: Generate random Gaussian data with same dimensions")
    print("  Expected: Very low stability (0.0-0.05) for random data")
    
    # Generate random data with same shape as embeddings
    random_data = np.random.randn(*embeddings_shape)
    
    return assess_clustering_reproducibility(random_data, k_values, n_runs)

# Synthetic clustered data control removed as requested

def test_spectral_parameters(embeddings, k_values, n_runs=5):
    """
    Test different spectral clustering parameters to find optimal settings.
    
    Args:
        embeddings: numpy array of embeddings
        k_values: list of k values to test
        n_runs: number of runs per parameter combination
    
    Returns:
        dict: Results for different parameter combinations
    """
    print("Testing spectral clustering parameters...")
    
    # Parameter combinations to test
    param_combinations = [
        {'affinity': 'nearest_neighbors', 'n_neighbors': 5, 'assign_labels': 'kmeans'},
        {'affinity': 'nearest_neighbors', 'n_neighbors': 10, 'assign_labels': 'kmeans'},
        {'affinity': 'nearest_neighbors', 'n_neighbors': 20, 'assign_labels': 'kmeans'},
        {'affinity': 'nearest_neighbors', 'n_neighbors': 10, 'assign_labels': 'discretize'},
        {'affinity': 'rbf', 'gamma': 0.1, 'assign_labels': 'kmeans'},
        {'affinity': 'rbf', 'gamma': 1.0, 'assign_labels': 'kmeans'},
        {'affinity': 'rbf', 'gamma': 10.0, 'assign_labels': 'kmeans'},
    ]
    
    results = {}
    
    for i, params in enumerate(param_combinations):
        print(f"\nTesting parameter combination {i+1}/{len(param_combinations)}: {params}")
        
        # Test this parameter combination
        param_results = {}
        for k in k_values:
            clusterings = []
            for run in range(n_runs):
                # Create spectral clustering with these parameters
                from sklearn.cluster import SpectralClustering
                sc = SpectralClustering(
                    n_clusters=k,
                    random_state=42 + run,
                    **params
                )
                labels = sc.fit_predict(embeddings)
                clusterings.append(labels)
            
            # Compute stability metrics
            stability_metrics = compute_stability_metrics(clusterings)
            if stability_metrics['ari_matrix'] is not None:
                ari_values = stability_metrics['ari_matrix'][np.triu_indices_from(stability_metrics['ari_matrix'], k=1)]
                nmi_values = stability_metrics['nmi_matrix'][np.triu_indices_from(stability_metrics['nmi_matrix'], k=1)]
                
                param_results[k] = {
                    'ari_mean': np.mean(ari_values),
                    'ari_std': np.std(ari_values),
                    'nmi_mean': np.mean(nmi_values),
                    'nmi_std': np.std(nmi_values)
                }
        
        results[f"params_{i+1}"] = {
            'parameters': params,
            'results': param_results
        }
    
    return results

def compare_clustering_algorithms(embeddings, k_values, n_runs=10):
    """
    Control: Compare k-means with other clustering algorithms.
    This tests if observed stability is algorithm-specific.
    """
    print("Comparing clustering algorithms...")
    
    algorithms = ['kmeans', 'spectral']  # Hierarchical clustering removed
    
    results = {}
    for algorithm in algorithms:
        print(f"Testing {algorithm}...")
        start_time = time.time()
        results[algorithm] = assess_clustering_reproducibility(
            embeddings, k_values, n_runs=n_runs, algorithm=algorithm
        )
        end_time = time.time()
        
        # Add timing information
        results[algorithm]['total_time'] = end_time - start_time
        results[algorithm]['time_per_run'] = (end_time - start_time) / (len(k_values) * n_runs)
        
        print(f"  {algorithm} total time: {results[algorithm]['total_time']:.2f}s")
        print(f"  {algorithm} time per run: {results[algorithm]['time_per_run']:.3f}s")
    
    return results

def generate_reproducibility_visualizations(results, results_dir, target, controls=None):
    """
    Generate visualizations for reproducibility assessment with controls.
    """
    print("Generating reproducibility visualizations...")
    
    k_values = results['k_values']
    summary_stats = results['summary_stats']
    
    # 1. Stability trends across k values
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # ARI trends
    ari_means = [summary_stats[k]['ari_mean'] for k in k_values]
    ari_stds = [summary_stats[k]['ari_std'] for k in k_values]
    
    axes[0, 0].errorbar(k_values, ari_means, yerr=ari_stds, marker='o', capsize=5, label='Observed Data')
    
    # Add control comparisons if available
    if controls:
        if 'random_permutation' in controls:
            random_perm_ari = [controls['random_permutation']['summary_stats'][k]['ari_mean'] for k in k_values]
            random_perm_ari_std = [controls['random_permutation']['summary_stats'][k]['ari_std'] for k in k_values]
            axes[0, 0].errorbar(k_values, random_perm_ari, yerr=random_perm_ari_std, marker='s', capsize=5, label='Random Permutation', alpha=0.7)
        
        if 'random_data' in controls:
            random_data_ari = [controls['random_data']['summary_stats'][k]['ari_mean'] for k in k_values]
            random_data_ari_std = [controls['random_data']['summary_stats'][k]['ari_std'] for k in k_values]
            axes[0, 0].errorbar(k_values, random_data_ari, yerr=random_data_ari_std, marker='^', capsize=5, label='Random Data', alpha=0.7)
        
        # Synthetic clustered control removed
    
    axes[0, 0].set_xlabel('Number of clusters (k)')
    axes[0, 0].set_ylabel('Adjusted Rand Index (mean ± std)')
    axes[0, 0].set_title('ARI Stability Across k Values')
    axes[0, 0].set_ylim(0, 1)
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # NMI trends
    nmi_means = [summary_stats[k]['nmi_mean'] for k in k_values]
    nmi_stds = [summary_stats[k]['nmi_std'] for k in k_values]
    
    axes[0, 1].errorbar(k_values, nmi_means, yerr=nmi_stds, marker='o', capsize=5, color='orange', label='Observed Data')
    
    # Add control comparisons if available
    if controls:
        if 'random_permutation' in controls:
            random_perm_nmi = [controls['random_permutation']['summary_stats'][k]['nmi_mean'] for k in k_values]
            random_perm_nmi_std = [controls['random_permutation']['summary_stats'][k]['nmi_std'] for k in k_values]
            axes[0, 1].errorbar(k_values, random_perm_nmi, yerr=random_perm_nmi_std, marker='s', capsize=5, label='Random Permutation', alpha=0.7)
        
        if 'random_data' in controls:
            random_data_nmi = [controls['random_data']['summary_stats'][k]['nmi_mean'] for k in k_values]
            random_data_nmi_std = [controls['random_data']['summary_stats'][k]['nmi_std'] for k in k_values]
            axes[0, 1].errorbar(k_values, random_data_nmi, yerr=random_data_nmi_std, marker='^', capsize=5, label='Random Data', alpha=0.7)
        
        # Synthetic clustered control removed
    
    axes[0, 1].set_xlabel('Number of clusters (k)')
    axes[0, 1].set_ylabel('Normalized Mutual Information (mean ± std)')
    axes[0, 1].set_title('NMI Stability Across k Values')
    axes[0, 1].set_ylim(0, 1)
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Coefficient of variation trends
    ari_cvs = [summary_stats[k]['ari_cv'] for k in k_values]
    nmi_cvs = [summary_stats[k]['nmi_cv'] for k in k_values]
    
    axes[1, 0].plot(k_values, ari_cvs, marker='o', label='ARI CV', color='blue')
    axes[1, 0].plot(k_values, nmi_cvs, marker='s', label='NMI CV', color='orange')
    axes[1, 0].set_xlabel('Number of clusters (k)')
    axes[1, 0].set_ylabel('Coefficient of Variation')
    axes[1, 0].set_title('Stability CV Across k Values')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Combined stability score
    combined_stability = [(ari_means[i] + nmi_means[i]) / 2 for i in range(len(k_values))]
    axes[1, 1].plot(k_values, combined_stability, marker='o', color='green', linewidth=2)
    axes[1, 1].set_xlabel('Number of clusters (k)')
    axes[1, 1].set_ylabel('Combined Stability Score')
    axes[1, 1].set_title('Combined Stability (ARI + NMI) / 2')
    axes[1, 1].set_ylim(0, 1)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    stability_plot_path = os.path.join(results_dir, f"stability_by_k_{target}.png")
    plt.savefig(stability_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Algorithm comparison plot
    if controls and 'algorithms' in controls:
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        algorithms = ['kmeans', 'spectral']
        colors = ['blue', 'green']
        
        # ARI comparison
        for i, (alg, color) in enumerate(zip(algorithms, colors)):
            if alg in controls['algorithms']:
                alg_ari = [controls['algorithms'][alg]['summary_stats'][k]['ari_mean'] for k in k_values]
                axes[0].plot(k_values, alg_ari, marker='o', label=alg.capitalize(), color=color, linewidth=2)
        
        axes[0].set_xlabel('Number of clusters (k)')
        axes[0].set_ylabel('Adjusted Rand Index')
        axes[0].set_title('Algorithm Comparison - ARI')
        axes[0].set_ylim(0, 1)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # NMI comparison
        for i, (alg, color) in enumerate(zip(algorithms, colors)):
            if alg in controls['algorithms']:
                alg_nmi = [controls['algorithms'][alg]['summary_stats'][k]['nmi_mean'] for k in k_values]
                axes[1].plot(k_values, alg_nmi, marker='s', label=alg.capitalize(), color=color, linewidth=2)
        
        axes[1].set_xlabel('Number of clusters (k)')
        axes[1].set_ylabel('Normalized Mutual Information')
        axes[1].set_title('Algorithm Comparison - NMI')
        axes[1].set_ylim(0, 1)
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        algorithm_plot_path = os.path.join(results_dir, f"algorithm_comparison_{target}.png")
        plt.savefig(algorithm_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        algorithm_plot_path = None
    
    # 3. Reproducibility heatmaps for selected k values
    n_k_to_plot = min(6, len(k_values))  # Plot up to 6 k values
    k_to_plot = k_values[:n_k_to_plot] if len(k_values) <= n_k_to_plot else k_values[::len(k_values)//n_k_to_plot][:n_k_to_plot]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for i, k in enumerate(k_to_plot):
        if k in results['stability_metrics'] and results['stability_metrics'][k]['ari_matrix'] is not None:
            ari_matrix = results['stability_metrics'][k]['ari_matrix']
            im = axes[i].imshow(ari_matrix, cmap='viridis', vmin=0, vmax=1)
            axes[i].set_title(f'k={k} - ARI Reproducibility')
            axes[i].set_xlabel('Run')
            axes[i].set_ylabel('Run')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=axes[i], shrink=0.8)
            cbar.set_label('Adjusted Rand Index')
            
            # Add text annotations
            for row in range(ari_matrix.shape[0]):
                for col in range(ari_matrix.shape[1]):
                    text = axes[i].text(col, row, f'{ari_matrix[row, col]:.2f}',
                                       ha="center", va="center", color="white" if ari_matrix[row, col] < 0.5 else "black")
    
    # Hide unused subplots
    for i in range(len(k_to_plot), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    heatmap_plot_path = os.path.join(results_dir, f"reproducibility_heatmap_{target}.png")
    plt.savefig(heatmap_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return stability_plot_path, heatmap_plot_path, algorithm_plot_path

def save_reproducibility_results(results, headers, sequences, results_dir, target, controls=None):
    """
    Save reproducibility results to files.
    """
    print("Saving reproducibility results...")
    
    # 1. Save summary statistics
    summary_data = []
    for k in results['k_values']:
        stats = results['summary_stats'][k]
        summary_data.append({
            'k': k,
            'ari_mean': stats['ari_mean'],
            'ari_std': stats['ari_std'],
            'ari_cv': stats['ari_cv'],
            'nmi_mean': stats['nmi_mean'],
            'nmi_std': stats['nmi_std'],
            'nmi_cv': stats['nmi_cv'],
            'jaccard_mean': stats['jaccard_mean'],
            'jaccard_std': stats['jaccard_std'],
            'jaccard_cv': stats['jaccard_cv'],
            'algorithm': results.get('algorithm', 'kmeans'),
            'n_runs': results.get('n_runs', 0)
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_csv = os.path.join(results_dir, f"stability_metrics_{target}.csv")
    summary_df.to_csv(summary_csv, index=False)
    
    # 2. Save cluster assignments for all runs
    cluster_data = []
    for k in results['k_values']:
        for run_idx, labels in enumerate(results['clusterings'][k]):
            for seq_idx, (header, sequence, label) in enumerate(zip(headers, sequences, labels)):
                cluster_data.append({
                    'header': header,
                    'sequence': sequence,
                    'k': k,
                    'run': run_idx,
                    'cluster': label,
                    'random_seed': results['random_seeds'][run_idx],
                    'algorithm': results['algorithm'],
                    'run_time': results.get('run_times', {}).get(k, {}).get(run_idx, 0)
                })
    
    cluster_df = pd.DataFrame(cluster_data)
    cluster_csv = os.path.join(results_dir, f"cluster_assignments_{target}.csv")
    cluster_df.to_csv(cluster_csv, index=False)
    
    # 3. Save embeddings
    embeddings_path = os.path.join(results_dir, f"embeddings_{target}.npy")
    np.save(embeddings_path, results.get('embeddings', None))
    
    # 4. Save control results if available
    if controls:
        controls_data = {}
        for control_name, control_results in controls.items():
            if 'summary_stats' in control_results:
                control_summary = []
                for k in control_results['k_values']:
                    stats = control_results['summary_stats'][k]
                    control_summary.append({
                        'k': k,
                        'control': control_name,
                        'ari_mean': stats['ari_mean'],
                        'ari_std': stats['ari_std'],
                        'nmi_mean': stats['nmi_mean'],
                        'nmi_std': stats['nmi_std']
                    })
                controls_data[control_name] = control_summary
            elif control_name == 'algorithms':
                # Save algorithm comparison results with timing
                for alg_name, alg_results in control_results.items():
                    if 'summary_stats' in alg_results:
                        for k in alg_results['k_values']:
                            stats = alg_results['summary_stats'][k]
                            controls_data[f"{alg_name}_timing"] = {
                                'total_time': alg_results.get('total_time', 0),
                                'time_per_run': alg_results.get('time_per_run', 0)
                            }
                            control_summary.append({
                                'k': k,
                                'control': f"{alg_name}_clustering",
                                'ari_mean': stats['ari_mean'],
                                'ari_std': stats['ari_std'],
                                'nmi_mean': stats['nmi_mean'],
                                'nmi_std': stats['nmi_std']
                            })
        
        # Save controls to CSV
        all_controls_data = []
        for control_name, control_summary in controls_data.items():
            if isinstance(control_summary, list):
                all_controls_data.extend(control_summary)
        
        if all_controls_data:
            controls_df = pd.DataFrame(all_controls_data)
            controls_csv = os.path.join(results_dir, f"control_results_{target}.csv")
            controls_df.to_csv(controls_csv, index=False)
        
        # Save timing data separately
        timing_data = []
        for control_name, control_results in controls.items():
            if control_name == 'algorithms':
                for alg_name, alg_results in control_results.items():
                    timing_data.append({
                        'algorithm': alg_name,
                        'total_time': alg_results.get('total_time', 0),
                        'time_per_run': alg_results.get('time_per_run', 0),
                        'n_runs': alg_results.get('n_runs', 0),
                        'n_k_values': len(alg_results.get('k_values', []))
                    })
        
        if timing_data:
            timing_df = pd.DataFrame(timing_data)
            timing_csv = os.path.join(results_dir, f"timing_data_{target}.csv")
            timing_df.to_csv(timing_csv, index=False)
    
    return summary_csv, cluster_csv, embeddings_path

def write_reproducibility_report(results, headers, sequences, results_dir, target, 
                               start_time, end_time, input_files, output_files, controls=None):
    """
    Write a comprehensive reproducibility report with controls.
    """
    duration = end_time - start_time
    
    report_path = os.path.join(results_dir, f"reproducibility_report_{target}.txt")
    with open(report_path, 'w') as f:
        f.write("K-means Reproducibility Assessment Report\n")
        f.write("=========================================\n\n")
        
        f.write(f"Run start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Run end:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration:  {duration}\n\n")
        
        f.write("Configuration:\n")
        f.write(f"  TARGET: {target}\n")
        f.write(f"  k_values: {results['k_values']}\n")
        f.write(f"  n_runs: {results['n_runs']}\n")
        f.write(f"  random_seeds: {results['random_seeds']}\n")
        f.write(f"  algorithm: {results['algorithm']}\n")
        f.write(f"  sequences: {len(sequences)}\n\n")
        
        f.write("Inputs:\n")
        for file_path in input_files:
            f.write(f"  - {file_path}\n")
        f.write("\n")
        
        f.write("Outputs:\n")
        for file_path in output_files:
            f.write(f"  - {file_path}\n")
        f.write("\n")
        
        f.write("Stability Summary:\n")
        f.write("=================\n")
        for k in results['k_values']:
            stats = results['summary_stats'][k]
            f.write(f"\nk={k}:\n")
            f.write(f"  ARI: {stats['ari_mean']:.3f} ± {stats['ari_std']:.3f} (CV: {stats['ari_cv']:.3f})\n")
            f.write(f"  NMI: {stats['nmi_mean']:.3f} ± {stats['nmi_std']:.3f} (CV: {stats['nmi_cv']:.3f})\n")
            f.write(f"  Jaccard: {stats['jaccard_mean']:.3f} ± {stats['jaccard_std']:.3f} (CV: {stats['jaccard_cv']:.3f})\n")
        
        # Find most stable k
        if results['summary_stats']:
            ari_means = [results['summary_stats'][k]['ari_mean'] for k in results['k_values']]
            nmi_means = [results['summary_stats'][k]['nmi_mean'] for k in results['k_values']]
            combined_stability = [(ari_means[i] + nmi_means[i]) / 2 for i in range(len(results['k_values']))]
            
            best_k_idx = np.argmax(combined_stability)
            best_k = results['k_values'][best_k_idx]
            
            f.write(f"\nMost Stable k: {best_k} (combined stability: {combined_stability[best_k_idx]:.3f})\n")
        
        # Control results
        if controls:
            f.write("\nControl Results:\n")
            f.write("================\n")
            
            for control_name, control_results in controls.items():
                if 'summary_stats' in control_results:
                    f.write(f"\n{control_name.upper()} Control:\n")
                    # Show results for k=5 as example
                    if 5 in control_results['summary_stats']:
                        stats = control_results['summary_stats'][5]
                        f.write(f"  k=5 ARI: {stats['ari_mean']:.3f} ± {stats['ari_std']:.3f}\n")
                        f.write(f"  k=5 NMI: {stats['nmi_mean']:.3f} ± {stats['nmi_std']:.3f}\n")
        
        f.write("\nNotes:\n")
        f.write("  - Embeddings: ESM2 t33_650M_UR50D\n")
        f.write("  - Clustering: KMeans with n_init=10\n")
        f.write("  - Stability metrics: ARI, NMI, Jaccard similarity\n")
        f.write("  - Reproducibility assessed across multiple random seeds\n")
        if controls:
            f.write("  - Controls included: Random permutation, Random data, Synthetic clustered data\n")
            if 'algorithms' in controls:
                f.write("  - Algorithm comparison: K-means, Hierarchical, Spectral clustering\n")
    
    return report_path

def process_single_fasta(fasta_path, target, cfg, results_base_dir, start_time, device):
    """
    Process a single FASTA file independently.
    
    Args:
        fasta_path: Path to the FASTA file
        target: Project name
        cfg: Configuration dictionary
        results_base_dir: Base results directory
        start_time: Analysis start time
        device: Device to use for computations
    
    Returns:
        dict with processing results
    """
    import tempfile
    
    fasta_name = os.path.splitext(os.path.basename(fasta_path))[0]
    print(f"\nProcessing FASTA: {fasta_name}")
    
    # Create subdirectory for this FASTA's results
    fasta_results_dir = os.path.join(results_base_dir, fasta_name)
    os.makedirs(fasta_results_dir, exist_ok=True)
    
    # Load sequences from this FASTA file
    headers, sequences = load_sequences(fasta_path)
    num_sequences = len(sequences)
    
    print(f"  Loaded {num_sequences} sequences")
    
    if num_sequences < 2:
        print(f"  Skipping {fasta_name}: insufficient sequences for clustering (need at least 2)")
        return {
            'fasta_name': fasta_name,
            'fasta_path': fasta_path,
            'results_dir': fasta_results_dir,
            'num_sequences': num_sequences,
            'error': 'Insufficient sequences for clustering',
            'success': False
        }
    
    try:
        # Get configuration parameters
        k_range = cfg.get('kmeansbenchmark_k_range', [2, 20])
        n_runs = cfg.get('kmeansbenchmark_n_runs', 10)
        random_seeds = cfg.get('kmeansbenchmark_random_seeds', None)
        run_controls = cfg.get('kmeansbenchmark_run_controls', True)
        compare_algorithms = cfg.get('kmeansbenchmark_compare_algorithms', True)
        
        if random_seeds is None:
            random_seeds = list(range(42, 42 + n_runs))
        
        # Compute embeddings and scores
        print(f"  Computing embeddings and scores...")
        embeddings, scores = compute_embeddings_and_scores(headers, sequences, device=device)
        
        # Determine k values to test
        if isinstance(k_range, list) and len(k_range) == 2:
            min_k, max_k = k_range
            k_values = list(range(max(2, min_k), min(max_k + 1, num_sequences)))
        else:
            k_values = k_range if isinstance(k_range, list) else [k_range]
        
        # Ensure k values are within valid range
        k_values = [k for k in k_values if 2 <= k < num_sequences]
        
        if not k_values:
            print(f"  Skipping {fasta_name}: no valid k values for {num_sequences} sequences")
            return {
                'fasta_name': fasta_name,
                'fasta_path': fasta_path,
                'results_dir': fasta_results_dir,
                'num_sequences': num_sequences,
                'error': 'No valid k values',
                'success': False
            }
        
        print(f"  Testing k values: {k_values}")
        
        # Assess clustering reproducibility
        print("  Assessing k-means reproducibility...")
        results = assess_clustering_reproducibility(embeddings, k_values, n_runs, random_seeds)
        
        # Initialize controls
        controls = {}
        
        # Run controls if requested
        if run_controls:
            print("  Running controls...")
            from core.kmeansbenchmark_controls import (
                generate_random_permutation_control,
                generate_random_data_control
            )
            
            # Run basic controls
            controls['random_permutation'] = generate_random_permutation_control(embeddings, k_values, n_runs)
            controls['random_data'] = generate_random_data_control(embeddings.shape, k_values, n_runs)
        
        # Compare algorithms if requested
        if compare_algorithms:
            print("  Comparing clustering algorithms...")
            from core.kmeansbenchmark_controls import compare_clustering_algorithms
            algo_results = compare_clustering_algorithms(embeddings, k_values, n_runs)
            controls['algorithms'] = algo_results
        
        # Create visualizations
        print("  Creating visualizations...")
        stability_plot, heatmap_plot, algorithm_plot = generate_reproducibility_visualizations(
            results, fasta_results_dir, fasta_name, controls
        )
        
        # Save results
        print("  Saving results...")
        summary_csv, cluster_csv, embeddings_path = save_reproducibility_results(
            results, headers, sequences, fasta_results_dir, fasta_name, controls
        )
        
        # Generate summary report
        print("  Generating summary report...")
        output_files = [summary_csv, cluster_csv, embeddings_path, stability_plot, heatmap_plot]
        if algorithm_plot:
            output_files.append(algorithm_plot)
        
        report_path = write_reproducibility_report(
            results, headers, sequences, fasta_results_dir, fasta_name,
            start_time, datetime.datetime.now(), [fasta_path], output_files, controls
        )
        
        # Calculate key metrics for summary
        best_k = None
        best_stability = 0
        if 'kmeans_stability' in results:
            for k, stability in results['kmeans_stability'].items():
                if stability > best_stability:
                    best_stability = stability
                    best_k = k
        
        print(f"  → Results saved to: {fasta_results_dir}")
        print(f"  → Sequences: {num_sequences}")
        print(f"  → K values tested: {len(k_values)}")
        print(f"  → Best k: {best_k} (stability: {best_stability:.3f})")
        
        return {
            'fasta_name': fasta_name,
            'fasta_path': fasta_path,
            'results_dir': fasta_results_dir,
            'num_sequences': num_sequences,
            'k_values_tested': k_values,
            'best_k': best_k,
            'best_stability': best_stability,
            'success': True
        }
        
    except Exception as e:
        print(f"   Error processing {fasta_name}: {str(e)}")
        return {
            'fasta_name': fasta_name,
            'fasta_path': fasta_path,
            'results_dir': fasta_results_dir,
            'num_sequences': num_sequences,
            'error': str(e),
            'success': False
        }

def run_merged_mode(fasta_paths, target, cfg, results_dir, start_time, device):
    """
    Run kmeans benchmark in merged mode (original behavior).
    
    Args:
        fasta_paths: List of FASTA file paths
        target: Project name
        cfg: Configuration dictionary  
        results_dir: Results directory
        start_time: Analysis start time
        device: Device to use for computations
    """
    print(f"Running in merged mode - combining all FASTA files")
    
    # Load and merge all sequences
    headers, sequences = [], []
    for fp in fasta_paths:
        hdrs, seqs = load_sequences(fp)
        headers.extend(hdrs)
        sequences.extend(seqs)
    
    num_sequences = len(sequences)
    print(f"Loaded {num_sequences} sequences from {len(fasta_paths)} files")
    
    # Get configuration parameters
    k_range = cfg.get('kmeansbenchmark_k_range', [2, 20])
    n_runs = cfg.get('kmeansbenchmark_n_runs', 10)
    random_seeds = cfg.get('kmeansbenchmark_random_seeds', None)
    run_controls = cfg.get('kmeansbenchmark_run_controls', True)
    compare_algorithms = cfg.get('kmeansbenchmark_compare_algorithms', True)
    
    if random_seeds is None:
        random_seeds = list(range(42, 42 + n_runs))
    
    # Compute embeddings and scores
    print("Computing embeddings and scores...")
    embeddings, scores = compute_embeddings_and_scores(headers, sequences, device=device)
    
    # Determine k values to test
    if isinstance(k_range, list) and len(k_range) == 2:
        min_k, max_k = k_range
        k_values = list(range(max(2, min_k), min(max_k + 1, num_sequences)))
    else:
        k_values = k_range if isinstance(k_range, list) else [k_range]
    
    # Ensure k values are within valid range
    k_values = [k for k in k_values if 2 <= k < num_sequences]
    
    print(f"Testing k values: {k_values}")
    
    # Assess clustering reproducibility
    print("Assessing k-means reproducibility...")
    results = assess_clustering_reproducibility(embeddings, k_values, n_runs, random_seeds)
    
    # Initialize controls
    controls = {}
    
    # Run controls if requested
    if run_controls:
        print("Running controls...")
        from core.kmeansbenchmark_controls import (
            generate_random_permutation_control,
            generate_random_data_control
        )
        
        # Run basic controls
        controls['random_permutation'] = generate_random_permutation_control(embeddings, k_values, n_runs)
        controls['random_data'] = generate_random_data_control(embeddings.shape, k_values, n_runs)
    
    # Compare algorithms if requested
    if compare_algorithms:
        print("Comparing clustering algorithms...")
        from core.kmeansbenchmark_controls import compare_clustering_algorithms
        algo_results = compare_clustering_algorithms(embeddings, k_values, n_runs)
        controls['algorithms'] = algo_results
    
    # Create visualizations
    print("Creating visualizations...")
    stability_plot, heatmap_plot, algorithm_plot = generate_reproducibility_visualizations(
        results, results_dir, target, controls
    )
    
    # Save results
    print("Saving results...")
    summary_csv, cluster_csv, embeddings_path = save_reproducibility_results(
        results, headers, sequences, results_dir, target, controls
    )
    
    # Generate summary report
    print("Generating summary report...")
    output_files = [summary_csv, cluster_csv, embeddings_path, stability_plot, heatmap_plot]
    if algorithm_plot:
        output_files.append(algorithm_plot)
    
    report_path = write_reproducibility_report(
        results, headers, sequences, results_dir, target,
        start_time, datetime.datetime.now(), fasta_paths, output_files, controls
    )
    
    print("\n" + "="*60)
    print("K-MEANS REPRODUCIBILITY ASSESSMENT COMPLETE")
    print("="*60)
    print(f"Project: {target}")
    print(f"Results saved to: {results_dir}")
    print(f"Total sequences: {num_sequences}")
    print(f"K values tested: {k_values}")
    print("="*60)

def run_separate_mode(fasta_paths, target, cfg, results_dir, start_time):
    """
    Run kmeans benchmark in separate mode (process each FASTA independently).
    
    Args:
        fasta_paths: List of FASTA file paths
        target: Project name
        cfg: Configuration dictionary
        results_dir: Results directory
        start_time: Analysis start time
    """
    print(f"Running in separate mode - processing each FASTA file independently")
    
    # Determine device
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Process each FASTA file independently
    all_results = []
    for i, fasta_path in enumerate(fasta_paths, 1):
        print(f"\n--- Processing FASTA {i}/{len(fasta_paths)} ---")
        result = process_single_fasta(fasta_path, target, cfg, results_dir, start_time, device)
        if result:
            all_results.append(result)
    
    # Create summary log
    end_time = datetime.datetime.now()
    create_summary_log(all_results, results_dir, target, start_time, end_time)
    
    # Print summary
    successful_results = [r for r in all_results if r.get('success', False)]
    failed_results = [r for r in all_results if not r.get('success', False)]
    
    print(f"\n=== SUMMARY ===")
    print(f"Processed {len(successful_results)}/{len(all_results)} FASTA files successfully")
    if successful_results:
        total_sequences = sum(r['num_sequences'] for r in successful_results)
        avg_best_stability = np.mean([r['best_stability'] for r in successful_results if r['best_stability'] > 0])
        print(f"Total sequences: {total_sequences}")
        print(f"Average best stability: {avg_best_stability:.3f}")
    print(f"Results directory: {results_dir}")
    print(f"Duration: {end_time - start_time}")

def create_summary_log(all_results, results_dir, project_name, start_time, end_time):
    """Create a summary log for all processed FASTA files."""
    os.makedirs(results_dir, exist_ok=True)
    summary_log_path = os.path.join(results_dir, f"summary_log_{project_name}.txt")
    
    successful_results = [r for r in all_results if r['success']]
    failed_results = [r for r in all_results if not r['success']]
    
    with open(summary_log_path, 'w') as log_f:
        log_f.write("K-means Benchmarking Summary\n")
        log_f.write("===========================\n\n")
        log_f.write(f"Run start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Run end:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Duration:  {end_time - start_time}\n\n")
        log_f.write("Configuration:\n")
        log_f.write(f"  PROJECT: {project_name}\n")
        log_f.write(f"  Total FASTA files processed: {len(all_results)}\n")
        log_f.write(f"  Successful: {len(successful_results)}\n")
        log_f.write(f"  Failed: {len(failed_results)}\n\n")
        
        if successful_results:
            total_sequences = sum(r['num_sequences'] for r in successful_results)
            avg_best_stability = np.mean([r['best_stability'] for r in successful_results if r['best_stability'] > 0])
            
            log_f.write(f"Total sequences across all FASTA files: {total_sequences}\n")
            log_f.write(f"Average best stability: {avg_best_stability:.3f}\n\n")
            
            log_f.write("Successful FASTA-by-FASTA results:\n")
            for result in successful_results:
                log_f.write(f"\n  FASTA: {result['fasta_name']}\n")
                log_f.write(f"    Sequences: {result['num_sequences']}\n")
                log_f.write(f"    K values tested: {len(result['k_values_tested'])}\n")
                log_f.write(f"    Best k: {result['best_k']}\n")
                log_f.write(f"    Best stability: {result['best_stability']:.3f}\n")
                log_f.write(f"    Results directory: {result['results_dir']}\n")
        
        if failed_results:
            log_f.write(f"\nFailed FASTA files:\n")
            for result in failed_results:
                log_f.write(f"\n  FASTA: {result['fasta_name']}\n")
                log_f.write(f"    Error: {result['error']}\n")
        
        log_f.write(f"\nAll results saved under: {results_dir}\n")
        log_f.write("Each successful FASTA file has its own subdirectory with complete k-means benchmarking analysis.\n")
    
    print(f"Summary log saved to: {summary_log_path}")

def run(cfg):
    """
    Main function to run k-means reproducibility assessment with controls.
    """
    target = project_dir('kmeansbenchmark', cfg)
    if not target:
        raise ValueError("Need project directory")
    
    # Get configuration parameters
    keepseparate = cfg.get('kmeansbenchmark_keepseparate', False)
    
    start_time = datetime.datetime.now()
    
    # Load sequences
    fasta_paths = sorted(glob.glob(os.path.join('inputs', 'kmeansbenchmark', target, '*.fasta')))
    if not fasta_paths:
        raise ValueError(f"No FASTA files found in inputs/kmeansbenchmark/{target}/")
    
    print(f"K-means Reproducibility Assessment")
    print(f"Project: {target}")
    print(f"Found {len(fasta_paths)} FASTA files")
    print(f"Keep separate: {keepseparate}")
    print()
    
    # Create results directory
    results_dir = os.path.join('results', 'kmeansbenchmark', target)
    os.makedirs(results_dir, exist_ok=True)
    
    # Determine device
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    
    # Run in appropriate mode
    if keepseparate:
        run_separate_mode(fasta_paths, target, cfg, results_dir, start_time)
    else:
        run_merged_mode(fasta_paths, target, cfg, results_dir, start_time, device) 

def explain_baseline_controls(embeddings, k_values, n_runs=5):
    """
    Comprehensive explanation of baseline controls and their interpretation.
    
    Args:
        embeddings: numpy array of embeddings
        k_values: list of k values to test
        n_runs: number of runs per control
    
    Returns:
        dict: Results and interpretation of all baseline controls
    """
    print("="*80)
    print("BASELINE CONTROLS EXPLANATION")
    print("="*80)
    
    print("\n PURPOSE OF BASELINE CONTROLS")
    print("-" * 50)
    print("Baseline controls are essential for interpreting clustering stability results.")
    print("They provide context for determining whether observed stability is meaningful.")
    print("Without controls, you cannot distinguish between:")
    print("  • True biological structure vs. algorithm bias")
    print("  • Meaningful patterns vs. chance correlations")
    print("  • Good performance vs. overfitting")
    
    print("\n THREE CRITICAL CONTROLS")
    print("-" * 50)
    
    # 1. Random Permutation Control
    print("\n1. RANDOM PERMUTATION CONTROL")
    print("   " + "="*40)
    print("   PURPOSE: Test if observed stability is due to actual structure or chance")
    print("   METHOD: Randomly permute sample order while preserving feature distributions")
    print("   WHAT IT PRESERVES:")
    print("     • Overall data distribution")
    print("     • Feature correlations")
    print("     • Dimensionality and scale")
    print("   WHAT IT DESTROYS:")
    print("     • Sample-to-sample relationships")
    print("     • Cluster structure")
    print("     • Biological sequence relationships")
    print("   EXPECTED RESULT: Moderate stability (0.3-0.7) for well-structured data")
    print("   INTERPRETATION:")
    print("     • High stability (close to observed): Structure is robust to permutation")
    print("     • Low stability (close to random): Structure is fragile")
    print("     • Very high stability (>0.8): Algorithm may be biased")
    
    # 2. Random Data Control
    print("\n2. RANDOM DATA CONTROL")
    print("   " + "="*40)
    print("   PURPOSE: Establish null hypothesis baseline (no structure)")
    print("   METHOD: Generate random Gaussian data with same dimensions")
    print("   WHAT IT TESTS:")
    print("     • Algorithm behavior on unstructured data")
    print("     • Baseline for 'no structure' scenario")
    print("     • Algorithm bias or overfitting")
    print("   EXPECTED RESULT: Very low stability (0.0-0.05) for random data")
    print("   INTERPRETATION:")
    print("     • Very low stability (0.0-0.1): Algorithm works correctly")
    print("     • Higher stability (>0.2): Algorithm may be biased/overfitting")
    print("     • Moderate stability (0.1-0.3): Algorithm has some bias")
    
    print("\n INTERPRETATION FRAMEWORK, (some heuristics, don't take these as set in stone!)")
    print("-" * 50)
    print("To interpret your results, compare observed stability to controls:")
    print()
    print("  OBSERVED DATA STABILITY:")
    print("    • High (>0.8): Strong, meaningful structure")
    print("    • Moderate (0.4-0.8): Some structure, may be fragile")
    print("    • Low (<0.4): Weak or no meaningful structure")
    print()
    print("  COMPARISON TO CONTROLS:")
    print("    • vs. Random Data: Should be much higher (>10x)")
    print("    • vs. Random Permutation: Should be higher (1.5-3x)")
    print()
    print("  SCIENTIFIC CONCLUSIONS:")
    print("    • If observed >> random: Structure is meaningful")
    print("    • If observed ≈ permutation: Structure is fragile")
    print("    • If observed ≈ random: No meaningful structure")
    
    # Run the controls
    print("\n RUNNING BASELINE CONTROLS")
    print("-" * 50)
    
    controls = {}
    
    # 1. Random Permutation Control
    print("\n1. Running Random Permutation Control...")
    controls['random_permutation'] = generate_random_permutation_control(embeddings, k_values, n_runs)
    
    # 2. Random Data Control
    print("\n2. Running Random Data Control...")
    controls['random_data'] = generate_random_data_control(embeddings.shape, k_values, n_runs)
    
    # Synthetic clustered data control removed as requested
    
    # Analyze results
    print("\n CONTROL RESULTS ANALYSIS")
    print("-" * 50)
    
    for control_name, control_results in controls.items():
        if 'summary_stats' in control_results:
            print(f"\n{control_name.upper()} CONTROL RESULTS:")
            # Show results for k=5 as example
            if 5 in control_results['summary_stats']:
                stats = control_results['summary_stats'][5]
                print(f"  k=5 ARI: {stats['ari_mean']:.3f} ± {stats['ari_std']:.3f}")
                print(f"  k=5 NMI: {stats['nmi_mean']:.3f} ± {stats['nmi_std']:.3f}")
                
                # Interpretation
                if control_name == 'random_data':
                    if stats['ari_mean'] < 0.1:
                        print("  ✓ Expected: Very low stability for random data")
                    else:
                        print("   Unexpected: Higher than expected stability")
                elif control_name == 'random_permutation':
                    if 0.3 < stats['ari_mean'] < 0.7:
                        print("  ✓ Expected: Moderate stability for permuted data")
                    else:
                        print("   Unexpected: Stability outside expected range")
                # Synthetic clustered control removed
    
    print("\n CONCLUSIONS")
    print("-" * 50)
    print("Based on your control results, you can now:")
    print("1. Determine if observed stability is meaningful")
    print("2. Identify algorithm bias or limitations")
    print("3. Validate clustering method performance")
    print("4. Make confident scientific conclusions")
    print("5. Guide future experimental design")
    
    return controls

def walk_through_spectral_pipeline(embeddings, n_clusters=5, n_neighbors=10, random_state=42):
    """
    Walk through each transformation in the spectral clustering pipeline.
    
    Args:
        embeddings: numpy array of shape (n_samples, n_features)
        n_clusters: number of clusters to find
        n_neighbors: number of neighbors for graph construction
        random_state: random seed for reproducibility
    
    Returns:
        dict: Detailed information about each step
    """
    from sklearn.neighbors import kneighbors_graph
    from sklearn.metrics.pairwise import euclidean_distances
    from sklearn.cluster import SpectralClustering
    from scipy.sparse import csr_matrix
    from scipy.sparse.linalg import eigsh
    import numpy as np
    
    print("="*60)
    print("SPECTRAL CLUSTERING PIPELINE WALKTHROUGH")
    print("="*60)
    
    n_samples, n_features = embeddings.shape
    print(f"Input: {n_samples} samples × {n_features} features")
    
    # Step 1: Graph Construction (k-NN Graph)
    print(f"\n1. GRAPH CONSTRUCTION (k-NN with k={n_neighbors})")
    print("-" * 40)
    
    # Compute k-nearest neighbors graph
    knn_graph = kneighbors_graph(
        embeddings, 
        n_neighbors=n_neighbors, 
        mode='connectivity', 
        include_self=False
    )
    
    print(f"   • Computed k-NN graph: {knn_graph.shape}")
    print(f"   • Graph density: {knn_graph.nnz / (n_samples * n_samples):.4f}")
    print(f"   • Average degree: {knn_graph.sum(axis=1).mean():.1f}")
    print(f"   • Graph type: Sparse connectivity matrix")
    print(f"   • Distance metric: Euclidean (L2 norm)")
    
    # Step 2: Symmetrization
    print(f"\n2. SYMMETRIZATION")
    print("-" * 40)
    
    # Make graph symmetric (A[i,j] = A[j,i])
    symmetric_graph = knn_graph + knn_graph.T
    symmetric_graph = (symmetric_graph > 0).astype(float)
    
    print(f"   • Original graph: {knn_graph.nnz} non-zero elements")
    print(f"   • Symmetric graph: {symmetric_graph.nnz} non-zero elements")
    print(f"   • Symmetrization: A[i,j] = max(A[i,j], A[j,i])")
    
    # Step 3: Degree Matrix
    print(f"\n3. DEGREE MATRIX COMPUTATION")
    print("-" * 40)
    
    # Compute degree matrix D (diagonal matrix with row sums)
    degrees = np.array(symmetric_graph.sum(axis=1)).flatten()
    degree_matrix = csr_matrix((degrees, (range(n_samples), range(n_samples))), shape=(n_samples, n_samples))
    
    print(f"   • Degree matrix shape: {degree_matrix.shape}")
    print(f"   • Average degree: {degrees.mean():.2f}")
    print(f"   • Min degree: {degrees.min()}")
    print(f"   • Max degree: {degrees.max()}")
    print(f"   • Degree matrix type: Diagonal sparse matrix")
    
    # Step 4: Laplacian Matrix
    print(f"\n4. LAPLACIAN MATRIX COMPUTATION")
    print("-" * 40)
    
    # Compute Laplacian matrix L = D - A
    laplacian = degree_matrix - symmetric_graph
    
    print(f"   • Laplacian matrix shape: {laplacian.shape}")
    print(f"   • Laplacian type: L = D - A (Unnormalized)")
    print(f"   • Non-zero elements: {laplacian.nnz}")
    print(f"   • Matrix properties: Symmetric, positive semi-definite")
    
    # Step 5: Eigenvalue Decomposition
    print(f"\n5. EIGENVALUE DECOMPOSITION")
    print("-" * 40)
    
    # Compute the smallest k+1 eigenvalues and eigenvectors
    # (k+1 because the smallest eigenvalue is always 0)
    n_eigenvalues = min(n_clusters + 1, n_samples)
    
    try:
        eigenvalues, eigenvectors = eigsh(
            laplacian, 
            k=n_eigenvalues, 
            which='SM',  # Smallest magnitude
            sigma=0.0
        )
        
        print(f"   • Computed {n_eigenvalues} smallest eigenvalues")
        print(f"   • Eigenvalues: {eigenvalues[:5]}...")  # Show first 5
        print(f"   • Eigenvectors shape: {eigenvectors.shape}")
        print(f"   • Smallest eigenvalue (should be ~0): {eigenvalues[0]:.2e}")
        
        # Step 6: Spectral Embedding
        print(f"\n6. SPECTRAL EMBEDDING")
        print("-" * 40)
        
        # Use the k smallest non-zero eigenvectors for embedding
        # Skip the first eigenvector (corresponds to eigenvalue 0)
        spectral_embedding = eigenvectors[:, 1:n_clusters+1]
        
        print(f"   • Spectral embedding shape: {spectral_embedding.shape}")
        print(f"   • Embedding dimensions: {spectral_embedding.shape[1]}")
        print(f"   • Embedding range: [{spectral_embedding.min():.3f}, {spectral_embedding.max():.3f}]")
        print(f"   • Embedding mean: {spectral_embedding.mean():.3f}")
        print(f"   • Embedding std: {spectral_embedding.std():.3f}")
        
        # Step 7: Label Assignment
        print(f"\n7. LABEL ASSIGNMENT (K-means on spectral embedding)")
        print("-" * 40)
        
        # Apply k-means to the spectral embedding
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        labels = kmeans.fit_predict(spectral_embedding)
        
        print(f"   • Final labels shape: {labels.shape}")
        print(f"   • Number of unique labels: {len(np.unique(labels))}")
        print(f"   • Label distribution: {np.bincount(labels)}")
        print(f"   • Assignment method: K-means on spectral embedding")
        
        # Step 8: Pipeline Summary
        print(f"\n8. PIPELINE SUMMARY")
        print("-" * 40)
        
        print(f"   • Input dimensions: {n_samples} × {n_features}")
        print(f"   • Graph neighbors: {n_neighbors}")
        print(f"   • Spectral dimensions: {n_samples} × {n_clusters}")
        print(f"   • Final clusters: {n_clusters}")
        print(f"   • Computational complexity: O(n³) for eigendecomposition")
        
        return {
            'knn_graph': knn_graph,
            'symmetric_graph': symmetric_graph,
            'degree_matrix': degree_matrix,
            'laplacian': laplacian,
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors,
            'spectral_embedding': spectral_embedding,
            'labels': labels,
            'graph_density': knn_graph.nnz / (n_samples * n_samples),
            'avg_degree': degrees.mean(),
            'eigenvalue_gap': eigenvalues[1] - eigenvalues[0] if len(eigenvalues) > 1 else 0
        }
        
    except Exception as e:
        print(f"   • Error in eigenvalue decomposition: {e}")
        print(f"   • This can happen if the graph is disconnected")
        return None

def analyze_spectral_components(embeddings, n_clusters=5, n_neighbors=10):
    """
    Analyze which components are being scanned in the spectral clustering pipeline.
    
    Args:
        embeddings: numpy array of embeddings
        n_clusters: number of clusters
        n_neighbors: number of neighbors for graph construction
    
    Returns:
        dict: Analysis of spectral components
    """
    print("\n" + "="*60)
    print("SPECTRAL COMPONENTS ANALYSIS")
    print("="*60)
    
    # Run the pipeline walkthrough
    pipeline_info = walk_through_spectral_pipeline(embeddings, n_clusters, n_neighbors)
    
    if pipeline_info is None:
        return None
    
    print(f"\nCOMPONENT SCANNING ANALYSIS:")
    print("-" * 40)
    
    # Analyze which components are being scanned
    n_samples = embeddings.shape[0]
    
    print(f"1. GRAPH CONSTRUCTION SCANNING:")
    print(f"   • Scans: All pairwise distances between {n_samples} samples")
    print(f"   • Complexity: O(n² × d) where d = {embeddings.shape[1]} features")
    print(f"   • Distance metric: Euclidean (L2 norm)")
    print(f"   • For each sample: Finds {n_neighbors} nearest neighbors")
    
    print(f"\n2. EIGENVALUE DECOMPOSITION SCANNING:")
    print(f"   • Scans: Laplacian matrix of size {n_samples} × {n_samples}")
    print(f"   • Computes: {n_clusters + 1} smallest eigenvalues/eigenvectors")
    print(f"   • Method: Lanczos algorithm (eigsh)")
    print(f"   • Complexity: O(n³) for full eigendecomposition")
    
    print(f"\n3. SPECTRAL EMBEDDING SCANNING:")
    print(f"   • Scans: {n_clusters} eigenvectors (excluding first)")
    print(f"   • Embedding space: {n_samples} × {n_clusters}")
    print(f"   • Dimensionality reduction: {embeddings.shape[1]} → {n_clusters}")
    
    print(f"\n4. LABEL ASSIGNMENT SCANNING:")
    print(f"   • Scans: Spectral embedding in {n_clusters}-dimensional space")
    print(f"   • Method: K-means clustering")
    print(f"   • Complexity: O(n × k × iterations)")
    
    # Analyze the spectral gap
    if len(pipeline_info['eigenvalues']) > 1:
        spectral_gap = pipeline_info['eigenvalues'][1] - pipeline_info['eigenvalues'][0]
        print(f"\n5. SPECTRAL GAP ANALYSIS:")
        print(f"   • Spectral gap (λ₂ - λ₁): {spectral_gap:.6f}")
        print(f"   • Large gap (>0.1): Good cluster separation")
        print(f"   • Small gap (<0.01): Poor cluster separation")
        print(f"   • Your gap: {'Good' if spectral_gap > 0.1 else 'Poor' if spectral_gap < 0.01 else 'Moderate'} separation")
    
    return pipeline_info 