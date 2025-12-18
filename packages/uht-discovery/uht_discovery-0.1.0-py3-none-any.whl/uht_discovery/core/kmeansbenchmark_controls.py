#!/usr/bin/env python3
"""
K-means Reproducibility Assessment Controls
Essential controls to make reproducibility tests meaningful
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering, SpectralClustering, DBSCAN
from sklearn.datasets import make_blobs
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from .kmeansbenchmark import assess_clustering_reproducibility, compute_stability_metrics
import os

def generate_random_permutation_control(embeddings, k_values, n_runs=10):
    """
    Control: Randomly permute cluster assignments to establish baseline.
    This tests if observed stability is due to actual structure or chance.
    """
    print("Generating random permutation control...")
    
    # Randomly permute the embeddings
    permuted_embeddings = np.random.permutation(embeddings)
    
    return assess_clustering_reproducibility(permuted_embeddings, k_values, n_runs)

def generate_random_data_control(embeddings_shape, k_values, n_runs=10):
    """
    Control: Generate completely random data with same dimensions.
    This establishes the null hypothesis baseline.
    """
    print("Generating random data control...")
    
    # Generate random data with same shape as embeddings
    random_data = np.random.randn(*embeddings_shape)
    
    return assess_clustering_reproducibility(random_data, k_values, n_runs)

def generate_synthetic_clustered_data(n_samples=1193, n_features=1280, n_clusters=5, noise_level=0.1):
    """
    Control: Generate synthetic data with known cluster structure.
    This tests if the method can detect known clustering.
    """
    print(f"Generating synthetic clustered data with {n_clusters} clusters...")
    
    # Generate synthetic clustered data
    synthetic_data, true_labels = make_blobs(
        n_samples=n_samples, 
        n_features=n_features, 
        centers=n_clusters, 
        cluster_std=noise_level,
        random_state=42
    )
    
    return synthetic_data, true_labels

def generate_hierarchical_data_control(embeddings, k_values, n_runs=10, noise_level=0.1):
    """
    Control: Test with data that has known hierarchical structure.
    This validates if the method can detect natural groupings.
    """
    print("Generating hierarchical data control...")
    
    # Create hierarchical structure by adding noise to existing embeddings
    hierarchical_data = embeddings + np.random.normal(0, noise_level, embeddings.shape)
    
    return assess_clustering_reproducibility(hierarchical_data, k_values, n_runs)

def compare_clustering_algorithms(embeddings, k_values, n_runs=10):
    """
    Control: Compare k-means with other clustering algorithms.
    This tests if observed stability is algorithm-specific.
    """
    print("Comparing clustering algorithms...")
    
    algorithms = {
        'kmeans': KMeans,
        'hierarchical': AgglomerativeClustering,
        'spectral': SpectralClustering
    }
    
    results = {}
    for name, algorithm in algorithms.items():
        print(f"Testing {name}...")
        results[name] = assess_clustering_reproducibility_with_algorithm(
            embeddings, k_values, algorithm, n_runs
        )
    
    return results

def assess_clustering_reproducibility_with_algorithm(embeddings, k_values, algorithm, n_runs=10):
    """
    Assess reproducibility with a specific clustering algorithm.
    """
    results = {
        'k_values': k_values,
        'n_runs': n_runs,
        'clusterings': {},
        'stability_metrics': {},
        'summary_stats': {}
    }
    
    for k in k_values:
        clusterings_k = []
        for run_idx in range(n_runs):
            if algorithm == KMeans:
                model = algorithm(n_clusters=k, random_state=run_idx, n_init=10)
            elif algorithm == AgglomerativeClustering:
                model = algorithm(n_clusters=k)
            elif algorithm == SpectralClustering:
                model = algorithm(n_clusters=k, random_state=run_idx)
            else:
                model = algorithm(n_clusters=k)
            
            labels = model.fit_predict(embeddings)
            clusterings_k.append(labels)
        
        results['clusterings'][k] = clusterings_k
        stability_metrics = compute_stability_metrics(clusterings_k)
        results['stability_metrics'][k] = stability_metrics
        
        # Compute summary statistics
        if stability_metrics['ari_matrix'] is not None:
            ari_values = stability_metrics['ari_matrix'][np.triu_indices_from(stability_metrics['ari_matrix'], k=1)]
            nmi_values = stability_metrics['nmi_matrix'][np.triu_indices_from(stability_metrics['nmi_matrix'], k=1)]
            
            results['summary_stats'][k] = {
                'ari_mean': np.mean(ari_values),
                'ari_std': np.std(ari_values),
                'nmi_mean': np.mean(nmi_values),
                'nmi_std': np.std(nmi_values)
            }
    
    return results

def subsampling_control(embeddings, k_values, n_runs=10, subsample_sizes=[500, 800, 1000]):
    """
    Control: Test stability with different sample sizes.
    This tests if stability is sample size dependent.
    """
    print("Testing subsampling control...")
    
    results = {}
    for size in tqdm(subsample_sizes, desc="Subsampling"):
        if size < len(embeddings):
            subsample_indices = np.random.choice(len(embeddings), size, replace=False)
            subsample_embeddings = embeddings[subsample_indices]
            results[size] = assess_clustering_reproducibility(subsample_embeddings, k_values, n_runs)
    
    return results

def noise_addition_control(embeddings, k_values, n_runs=10, noise_levels=[0.01, 0.05, 0.1, 0.2]):
    """
    Control: Add varying levels of noise to test robustness.
    This tests if stability is sensitive to data quality.
    """
    print("Testing noise addition control...")
    
    results = {}
    for noise in tqdm(noise_levels, desc="Noise levels"):
        noisy_embeddings = embeddings + np.random.normal(0, noise, embeddings.shape)
        results[noise] = assess_clustering_reproducibility(noisy_embeddings, k_values, n_runs)
    
    return results

def bootstrap_confidence_intervals(embeddings, k_values, n_bootstrap=1000):
    """
    Control: Generate bootstrap confidence intervals for stability metrics.
    This provides statistical significance testing.
    """
    print(f"Generating bootstrap confidence intervals with {n_bootstrap} iterations...")
    
    bootstrap_results = []
    for _ in tqdm(range(n_bootstrap), desc="Bootstrap"):
        # Bootstrap sample with replacement
        bootstrap_indices = np.random.choice(len(embeddings), len(embeddings), replace=True)
        bootstrap_embeddings = embeddings[bootstrap_indices]
        results = assess_clustering_reproducibility(bootstrap_embeddings, k_values, n_runs=5)
        bootstrap_results.append(results)
    
    return bootstrap_results

def permutation_test_control(embeddings, k_values, n_permutations=1000):
    """
    Control: Permutation tests to assess statistical significance.
    This tests if observed stability is statistically significant.
    """
    print(f"Generating permutation test control with {n_permutations} permutations...")
    
    # Observed stability
    observed_results = assess_clustering_reproducibility(embeddings, k_values, n_runs=10)
    
    # Permutation distribution
    permutation_results = []
    for _ in tqdm(range(n_permutations), desc="Permutations"):
        permuted_embeddings = np.random.permutation(embeddings)
        perm_results = assess_clustering_reproducibility(permuted_embeddings, k_values, n_runs=5)
        permutation_results.append(perm_results)
    
    return observed_results, permutation_results

def run_comprehensive_controls(embeddings, k_values, results_dir, target):
    """
    Run all controls and generate comprehensive comparison.
    """
    print("Running comprehensive controls...")
    
    controls = {}
    
    # 1. Random permutation control
    controls['random_permutation'] = generate_random_permutation_control(embeddings, k_values)
    
    # 2. Random data control
    controls['random_data'] = generate_random_data_control(embeddings.shape, k_values)
    
    # 3. Synthetic clustered data
    synthetic_data, true_labels = generate_synthetic_clustered_data(
        n_samples=embeddings.shape[0], 
        n_features=embeddings.shape[1], 
        n_clusters=5
    )
    controls['synthetic_clustered'] = assess_clustering_reproducibility(synthetic_data, k_values)
    
    # 4. Hierarchical data control
    controls['hierarchical'] = generate_hierarchical_data_control(embeddings, k_values)
    
    # 5. Algorithm comparison
    controls['algorithms'] = compare_clustering_algorithms(embeddings, k_values)
    
    # 6. Subsampling control
    controls['subsampling'] = subsampling_control(embeddings, k_values)
    
    # 7. Noise addition control
    controls['noise'] = noise_addition_control(embeddings, k_values)
    
    # 8. Bootstrap confidence intervals
    controls['bootstrap'] = bootstrap_confidence_intervals(embeddings, k_values, n_bootstrap=500)
    
    # 9. Permutation test
    controls['permutation'] = permutation_test_control(embeddings, k_values, n_permutations=500)
    
    # Generate control comparison plots
    generate_control_comparison_plots(controls, results_dir, target)
    
    return controls

def generate_control_comparison_plots(controls, results_dir, target):
    """
    Generate comparison plots for all controls.
    """
    print("Generating control comparison plots...")
    
    # 1. Compare observed vs random controls
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # ARI comparison
    k_values = list(controls['random_permutation']['summary_stats'].keys())
    
    # Observed data (assuming it's in controls)
    if 'observed' in controls:
        observed_ari = [controls['observed']['summary_stats'][k]['ari_mean'] for k in k_values]
        observed_ari_std = [controls['observed']['summary_stats'][k]['ari_std'] for k in k_values]
        axes[0, 0].errorbar(k_values, observed_ari, yerr=observed_ari_std, marker='o', label='Observed', capsize=5)
    
    # Random permutation
    random_perm_ari = [controls['random_permutation']['summary_stats'][k]['ari_mean'] for k in k_values]
    random_perm_ari_std = [controls['random_permutation']['summary_stats'][k]['ari_std'] for k in k_values]
    axes[0, 0].errorbar(k_values, random_perm_ari, yerr=random_perm_ari_std, marker='s', label='Random Permutation', capsize=5)
    
    # Random data
    random_data_ari = [controls['random_data']['summary_stats'][k]['ari_mean'] for k in k_values]
    random_data_ari_std = [controls['random_data']['summary_stats'][k]['ari_std'] for k in k_values]
    axes[0, 0].errorbar(k_values, random_data_ari, yerr=random_data_ari_std, marker='^', label='Random Data', capsize=5)
    
    axes[0, 0].set_xlabel('Number of clusters (k)')
    axes[0, 0].set_ylabel('Adjusted Rand Index')
    axes[0, 0].set_title('ARI Comparison: Observed vs Controls')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # NMI comparison
    if 'observed' in controls:
        observed_nmi = [controls['observed']['summary_stats'][k]['nmi_mean'] for k in k_values]
        observed_nmi_std = [controls['observed']['summary_stats'][k]['nmi_std'] for k in k_values]
        axes[0, 1].errorbar(k_values, observed_nmi, yerr=observed_nmi_std, marker='o', label='Observed', capsize=5)
    
    random_perm_nmi = [controls['random_permutation']['summary_stats'][k]['nmi_mean'] for k in k_values]
    random_perm_nmi_std = [controls['random_permutation']['summary_stats'][k]['nmi_std'] for k in k_values]
    axes[0, 1].errorbar(k_values, random_perm_nmi, yerr=random_perm_nmi_std, marker='s', label='Random Permutation', capsize=5)
    
    random_data_nmi = [controls['random_data']['summary_stats'][k]['nmi_mean'] for k in k_values]
    random_data_nmi_std = [controls['random_data']['summary_stats'][k]['nmi_std'] for k in k_values]
    axes[0, 1].errorbar(k_values, random_data_nmi, yerr=random_data_nmi_std, marker='^', label='Random Data', capsize=5)
    
    axes[0, 1].set_xlabel('Number of clusters (k)')
    axes[0, 1].set_ylabel('Normalized Mutual Information')
    axes[0, 1].set_title('NMI Comparison: Observed vs Controls')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Algorithm comparison
    if 'algorithms' in controls:
        algorithms = ['kmeans', 'hierarchical', 'spectral']
        colors = ['blue', 'orange', 'green']
        
        for i, (alg, color) in enumerate(zip(algorithms, colors)):
            if alg in controls['algorithms']:
                alg_ari = [controls['algorithms'][alg]['summary_stats'][k]['ari_mean'] for k in k_values]
                axes[1, 0].plot(k_values, alg_ari, marker='o', label=alg, color=color)
        
        axes[1, 0].set_xlabel('Number of clusters (k)')
        axes[1, 0].set_ylabel('Adjusted Rand Index')
        axes[1, 0].set_title('Algorithm Comparison')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    # Noise sensitivity
    if 'noise' in controls:
        noise_levels = list(controls['noise'].keys())
        k_5_ari = [controls['noise'][noise]['summary_stats'][5]['ari_mean'] for noise in noise_levels]
        axes[1, 1].plot(noise_levels, k_5_ari, marker='o', linewidth=2)
        axes[1, 1].set_xlabel('Noise Level')
        axes[1, 1].set_ylabel('ARI (k=5)')
        axes[1, 1].set_title('Noise Sensitivity')
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    control_plot_path = os.path.join(results_dir, f"control_comparison_{target}.png")
    plt.savefig(control_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return control_plot_path 