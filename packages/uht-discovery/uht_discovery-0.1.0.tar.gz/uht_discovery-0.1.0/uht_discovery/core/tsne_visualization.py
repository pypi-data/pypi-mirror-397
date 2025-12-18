import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from .common import project_dir


def load_tsne_data(input_dir, target):
    """
    Load tSNE coordinates from CSV file.
    """
    # Look for CSV files in the input directory
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")
    
    # Use the first CSV file found (or could be more specific)
    csv_file = csv_files[0]
    csv_path = os.path.join(input_dir, csv_file)
    
    print(f"Loading tSNE data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Check if required columns exist
    required_cols = ['Dim1', 'Dim2', 'cluster']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    print(f"Loaded {len(df)} data points with {df['cluster'].nunique()} clusters")
    return df


def create_colorblind_friendly_palette(n_clusters):
    """
    Create a colorblind-friendly color palette.
    Uses a combination of colors that are distinguishable for colorblind individuals.
    Based on scientific research and ColorBrewer palettes.
    """
    # Colorblind-friendly colors (scientifically validated)
    # These colors are distinguishable for most types of colorblindness
    colors = [
        '#1f77b4',  # blue
        '#ff7f0e',  # orange
        '#2ca02c',  # green
        '#d62728',  # red
        '#9467bd',  # purple
        '#8c564b',  # brown
        '#e377c2',  # pink
        '#7f7f7f',  # gray
        '#bcbd22',  # olive
        '#17becf',  # cyan
        '#a6cee3',  # light blue
        '#fb9a99',  # light red
        '#fdbf6f',  # light orange
        '#cab2d6',  # light purple
        '#ffff99',  # light yellow
        '#b15928',  # dark orange
    ]
    
    # Alternative colorblind-friendly palette (more distinct)
    alt_colors = [
        '#000000',  # black
        '#E69F00',  # orange
        '#56B4E9',  # sky blue
        '#009E73',  # bluish green
        '#F0E442',  # yellow
        '#0072B2',  # blue
        '#D55E00',  # vermillion
        '#CC79A7',  # reddish purple
        '#999999',  # gray
        '#000000',  # black (repeated for cycling)
    ]
    
    # Use the alternative palette for better colorblind accessibility
    if n_clusters <= len(alt_colors):
        colors = alt_colors[:n_clusters]
    else:
        # If we need more colors, cycle through the alternative palette
        extended_colors = alt_colors * (n_clusters // len(alt_colors) + 1)
        colors = extended_colors[:n_clusters]
    
    return colors


def create_tsne_plot(df, results_dir, target):
    """
    Create a publication-grade tSNE plot with colorblind-friendly colors.
    """
    print("Creating tSNE visualization...")
    
    # Get unique clusters and sort them
    clusters = sorted(df['cluster'].unique())
    n_clusters = len(clusters)
    
    # Create colorblind-friendly palette
    colors = create_colorblind_friendly_palette(n_clusters)
    
    # Create the plot
    plt.figure(figsize=(14, 10))
    
    # Create scatter plot with custom colors
    for i, cluster in enumerate(clusters):
        cluster_data = df[df['cluster'] == cluster]
        cluster_size = len(cluster_data)
        plt.scatter(
            cluster_data['Dim1'], 
            cluster_data['Dim2'], 
            c=[colors[i]], 
            label=f'Cluster {cluster} (n={cluster_size})',
            s=50,
            alpha=0.7,
            edgecolors='white',
            linewidth=0.5
        )
    
    # Customize the plot
    plt.xlabel('t-SNE Dimension 1', fontsize=14, fontweight='bold')
    plt.ylabel('t-SNE Dimension 2', fontsize=14, fontweight='bold')
    plt.title(f't-SNE Visualization of Sequence Clusters\n{target}', fontsize=16, pad=20, fontweight='bold')
    
    # Add legend with better positioning
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=11, frameon=True, fancybox=True, shadow=True)
    
    # Set axis limits with some padding
    plt.xlim(df['Dim1'].min() - 2, df['Dim1'].max() + 2)
    plt.ylim(df['Dim2'].min() - 2, df['Dim2'].max() + 2)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    plot_path = os.path.join(results_dir, f'tsne_visualization_{target}.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"tSNE plot saved to: {plot_path}")
    return plot_path


def create_tsne_plot_seaborn(df, results_dir, target):
    """
    Create an alternative tSNE plot using seaborn for different styling.
    """
    print("Creating seaborn tSNE visualization...")
    
    # Set seaborn style (no grid)
    sns.set_style("white")
    sns.set_palette("husl")  # seaborn's colorblind-friendly palette
    
    # Create the plot
    plt.figure(figsize=(14, 10))
    
    # Add cluster sizes to the dataframe for legend
    cluster_sizes = df['cluster'].value_counts().to_dict()
    df['cluster_with_size'] = df['cluster'].apply(lambda x: f'Cluster {x} (n={cluster_sizes[x]})')
    
    # Create scatter plot using seaborn
    scatter = sns.scatterplot(
        data=df,
        x='Dim1',
        y='Dim2',
        hue='cluster_with_size',
        palette='husl',
        s=50,
        alpha=0.7,
        edgecolor='white',
        linewidth=0.5
    )
    
    # Customize the plot
    plt.xlabel('t-SNE Dimension 1', fontsize=14, fontweight='bold')
    plt.ylabel('t-SNE Dimension 2', fontsize=14, fontweight='bold')
    plt.title(f't-SNE Visualization of Sequence Clusters (Seaborn)\n{target}', fontsize=16, pad=20, fontweight='bold')
    
    # Add legend with better positioning
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=11, title='Cluster', frameon=True, fancybox=True, shadow=True)
    
    # Set axis limits with some padding
    plt.xlim(df['Dim1'].min() - 2, df['Dim1'].max() + 2)
    plt.ylim(df['Dim2'].min() - 2, df['Dim2'].max() + 2)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    plot_path = os.path.join(results_dir, f'tsne_visualization_seaborn_{target}.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Seaborn tSNE plot saved to: {plot_path}")
    return plot_path


def generate_summary_statistics(df, results_dir, target):
    """
    Generate summary statistics for the tSNE visualization.
    """
    print("Generating summary statistics...")
    
    # Calculate cluster statistics
    cluster_stats = df.groupby('cluster').agg({
        'Dim1': ['count', 'mean', 'std', 'min', 'max'],
        'Dim2': ['mean', 'std', 'min', 'max']
    }).round(4)
    
    # Flatten column names
    cluster_stats.columns = ['_'.join(col).strip() for col in cluster_stats.columns]
    cluster_stats = cluster_stats.reset_index()
    
    # Save statistics
    stats_path = os.path.join(results_dir, f'tsne_statistics_{target}.csv')
    cluster_stats.to_csv(stats_path, index=False)
    
    print(f"Statistics saved to: {stats_path}")
    return stats_path


def run(cfg):
    """
    Main function to run tSNE visualization.
    """
    # Get project directory from config
    target = project_dir('tsnereplicate', cfg)
    if not target:
        raise ValueError("Need project directory")
    
    print(f"Running tSNE visualization for project: {target}")
    
    # Set up input and output directories
    input_dir = os.path.join('inputs', 'tsnereplicate', target)
    results_dir = os.path.join('results', 'tsnereplicate', target)
    
    # Create results directory if it doesn't exist
    os.makedirs(results_dir, exist_ok=True)
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Load tSNE data
    df = load_tsne_data(input_dir, target)
    
    # Create visualizations
    plot_path = create_tsne_plot(df, results_dir, target)
    seaborn_plot_path = create_tsne_plot_seaborn(df, results_dir, target)
    
    # Generate summary statistics
    stats_path = generate_summary_statistics(df, results_dir, target)
    
    # Print summary
    print("\n" + "="*60)
    print("T-SNE VISUALIZATION COMPLETE")
    print("="*60)
    print(f"Project: {target}")
    print(f"Results directory: {results_dir}")
    print(f"Total data points: {len(df)}")
    print(f"Number of clusters: {df['cluster'].nunique()}")
    print(f"\nGenerated files:")
    print(f"  - tSNE plot: {plot_path}")
    print(f"  - Seaborn tSNE plot: {seaborn_plot_path}")
    print(f"  - Statistics: {stats_path}")
    print("="*60)
    
    return {
        'plot_path': plot_path,
        'seaborn_plot_path': seaborn_plot_path,
        'stats_path': stats_path,
        'n_points': len(df),
        'n_clusters': df['cluster'].nunique()
    } 