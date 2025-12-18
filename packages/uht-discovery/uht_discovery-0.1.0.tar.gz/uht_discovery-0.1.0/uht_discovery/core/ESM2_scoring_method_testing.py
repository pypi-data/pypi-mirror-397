import os
import glob
import yaml
import torch
import esm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import psutil
import gc
from tqdm import tqdm
from scipy.stats import pearsonr, spearmanr
from matplotlib import cm
from matplotlib.colors import Normalize
import seaborn as sns
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def load_sequences(fasta_file):
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

def compute_single_forward_nll(headers, sequences, device='cpu'):
    """
    Single forward pass method from optimizer.py
    Computes NLL for each sequence in a single forward pass
    """
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval().to(device)
    batch_converter = alphabet.get_batch_converter()
    pad_idx = batch_converter.alphabet.padding_idx

    results = []
    timings = []
    memory_usage = []
    
    for hdr, seq in tqdm(zip(headers, sequences), desc="Single Forward NLL", total=len(sequences)):
        start_time = time.time()
        start_memory = get_memory_usage()
        
        # Single forward pass
        labels, seqs, toks = batch_converter([(hdr, seq)])
        toks = toks.to(device)
        
        with torch.no_grad():
            out = model(toks, repr_layers=[], return_contacts=False)
        
        # Compute NLL like in optimizer.py
        lps = torch.log_softmax(out["logits"], dim=-1)
        tp = lps.gather(2, toks.unsqueeze(-1)).squeeze(-1)
        mask = (toks != pad_idx)
        raw_nll = -(tp * mask).sum(dim=1).cpu().numpy()
        lengths = mask.sum(dim=1).cpu().numpy()
        norm_nll = raw_nll / lengths
        
        end_time = time.time()
        end_memory = get_memory_usage()
        
        timings.append(end_time - start_time)
        memory_usage.append(end_memory - start_memory)
        results.append(float(norm_nll[0]))  # Single sequence
        
        # Clear cache after each sequence
        gc.collect()
        if device != 'cpu':
            if hasattr(torch.mps, 'empty_cache'):
                torch.mps.empty_cache()
            else:
                torch.cuda.empty_cache()
    
    return np.array(results), np.array(timings), np.array(memory_usage)

def compute_avg_masked_nll(headers, sequences, device='cpu'):
    """
    For each sequence, mask one position at a time, compute the NLL of that single masked token,
    then average across all positions.
    """
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval().to(device)
    batch_converter = alphabet.get_batch_converter()
    mask_idx = alphabet.mask_idx

    results = []
    timings = []
    memory_usage = []
    
    for hdr, seq in tqdm(zip(headers, sequences), desc="Masked‐one NLL", total=len(sequences)):
        start_time = time.time()
        start_memory = get_memory_usage()
        
        _, _, tokens = batch_converter([(hdr, seq)])
        tokens = tokens.to(device)
        L = tokens.size(1)

        nlls = []
        # skip CLS (pos=0) and EOS (pos=L-1)
        for pos in range(1, L-1):
            masked = tokens.clone()
            masked[0, pos] = mask_idx
            with torch.no_grad():
                out = model(masked, repr_layers=[33], return_contacts=False)
                logits = out['logits'][0, pos]                     # (vocab_size,)
                tgt   = tokens[0, pos]                            # scalar
                nll   = -torch.log_softmax(logits, dim=-1)[tgt]   # scalar tensor
                nlls.append(nll.item())
        
        end_time = time.time()
        end_memory = get_memory_usage()
        
        timings.append(end_time - start_time)
        memory_usage.append(end_memory - start_memory)
        results.append(np.mean(nlls))
        
        # Clear cache after each sequence
        gc.collect()
        if device != 'cpu':
            if hasattr(torch.mps, 'empty_cache'):
                torch.mps.empty_cache()
            else:
                torch.cuda.empty_cache()
    
    return np.array(results), np.array(timings), np.array(memory_usage)

def compute_perplexities(headers, sequences, device='cpu', maskings_list=None):
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval().to(device)
    batch_converter = alphabet.get_batch_converter()
    criterion = torch.nn.CrossEntropyLoss(ignore_index=alphabet.padding_idx, reduction='sum')
    maskings_list = maskings_list or [5]
    pp_dict = {n: [] for n in maskings_list}
    timing_dict = {n: [] for n in maskings_list}
    memory_dict = {n: [] for n in maskings_list}
    confidence_dict = {n: [] for n in maskings_list}

    for hdr, seq in tqdm(zip(headers, sequences), desc="Perplexities", total=len(sequences)):
        _, _, tokens = batch_converter([(hdr, seq)])
        tokens = tokens.to(device)
        
        for n in maskings_list:
            start_time = time.time()
            start_memory = get_memory_usage()
            pp_list = []
            
            for _ in range(n):
                masked = tokens.clone()
                # 15% random mask
                prob = torch.full(masked.shape, 0.15, device=device)
                special = ((masked == alphabet.padding_idx) |
                           (masked == alphabet.cls_idx) |
                           (masked == alphabet.eos_idx))
                prob.masked_fill_(special, 0)
                mask_idx = torch.bernoulli(prob).bool()
                masked[mask_idx] = alphabet.mask_idx
                with torch.no_grad():
                    out    = model(masked, repr_layers=[33], return_contacts=False)
                    logits = out['logits'][mask_idx]
                    targets= tokens[mask_idx]
                    if targets.numel() > 0:
                        loss = criterion(logits, targets)
                        pp_list.append(float(np.exp(loss.item() / targets.numel())))
            
            end_time = time.time()
            end_memory = get_memory_usage()
            
            timing_dict[n].append(end_time - start_time)
            memory_dict[n].append(end_memory - start_memory)
            
            if pp_list:
                pp_dict[n].append(np.mean(pp_list))
                # Calculate confidence interval (std of multiple runs)
                confidence_dict[n].append(np.std(pp_list))
            else:
                pp_dict[n].append(np.nan)
                confidence_dict[n].append(np.nan)
        
        # Clear cache after each sequence
        gc.collect()
        if device != 'cpu':
            if hasattr(torch.mps, 'empty_cache'):
                torch.mps.empty_cache()
            else:
                torch.cuda.empty_cache()
    
    return pp_dict, timing_dict, memory_dict, confidence_dict

def create_correlation_analysis_plot(df, results_dir, target):
    """Create correlation analysis to answer speed-accuracy trade-off question"""
    import math
    # Set style
    plt.style.use('seaborn-v0_8')
    
    # Get all methods
    pp_cols = [col for col in df.columns if col.startswith('pp_') and not col.endswith('_time')]
    all_methods = ['single_forward'] + pp_cols
    
    # Only include methods with both correlation and timing
    correlations = []
    avg_times = []
    method_names = []
    for method in all_methods:
        if method in df.columns and 'saturation' in df.columns:
            time_col = f'{method}_time' if method != 'single_forward' else 'single_forward_time'
            if time_col in df.columns:
                avg_time = df[time_col].mean()
                corr, _ = pearsonr(df['saturation'], df[method])
                correlations.append(abs(corr))
                avg_times.append(avg_time)
                method_names.append(method)
    n_methods = len(method_names)
    n_scatter = min(n_methods, 3)
    nrows = 2
    ncols = max(3, n_scatter+1)
    fig, axes = plt.subplots(nrows, ncols, figsize=(6*ncols, 6*nrows))
    if nrows == 1 or ncols == 1:
        axes = np.atleast_2d(axes)
    # 1. Correlation vs Speed scatter plot (MAIN ANSWER)
    scatter = axes[0,0].scatter(avg_times, correlations, s=150, alpha=0.8, c=range(len(correlations)), cmap='viridis')
    axes[0,0].set_xlabel('Average Processing Time (s)')
    axes[0,0].set_ylabel('|Correlation with Saturation|')
    axes[0,0].set_title('Speed vs Accuracy Trade-off\n(Higher correlation + Lower time = Better)')
    axes[0,0].grid(True, alpha=0.3)
    for i, (x, y, name) in enumerate(zip(avg_times, correlations, method_names)):
        axes[0,0].annotate(name, (x, y), xytext=(5, 5), textcoords='offset points', fontsize=10)
    cbar = plt.colorbar(scatter, ax=axes[0,0])
    cbar.set_label('Method Index')
    # 2. Efficiency score (correlation/time ratio)
    efficiency_scores = [corr/time for corr, time in zip(correlations, avg_times)]
    bars = axes[0,1].bar(method_names, efficiency_scores, alpha=0.8, color='green')
    axes[0,1].set_ylabel('Efficiency Score (Correlation/Time)')
    axes[0,1].set_title('Method Efficiency\n(Higher = Better Speed-Accuracy Trade-off)')
    axes[0,1].tick_params(axis='x', rotation=45)
    for bar, value in zip(bars, efficiency_scores):
        axes[0,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{value:.2f}', ha='center', va='bottom', fontsize=9)
    # 3. Method ranking by efficiency
    sorted_indices = np.argsort(efficiency_scores)[::-1]
    sorted_efficiency = [efficiency_scores[i] for i in sorted_indices]
    sorted_names = [method_names[i] for i in sorted_indices]
    bars = axes[0,2].barh(sorted_names, sorted_efficiency, alpha=0.8, color='orange')
    axes[0,2].set_xlabel('Efficiency Score')
    axes[0,2].set_title('Method Ranking by Efficiency\n(Best Speed-Accuracy Trade-off)')
    for i, (bar, value) in enumerate(zip(bars, sorted_efficiency)):
        axes[0,2].text(value + 0.01, bar.get_y() + bar.get_height()/2,
                       f'{value:.2f}', va='center', fontsize=9)
    # 4. Correlation matrix heatmap
    plot_cols = ['saturation'] + all_methods
    plot_cols = [col for col in plot_cols if col in df.columns]
    if len(plot_cols) > 1:
        im = axes[1,0].imshow(df[plot_cols].corr(), cmap='coolwarm', vmin=-1, vmax=1)
        axes[1,0].set_xticks(range(len(plot_cols)))
        axes[1,0].set_yticks(range(len(plot_cols)))
        axes[1,0].set_xticklabels(plot_cols, rotation=45, ha='right')
        axes[1,0].set_yticklabels(plot_cols)
        axes[1,0].set_title('Correlation Matrix')
        for i in range(len(plot_cols)):
            for j in range(len(plot_cols)):
                axes[1,0].text(j, i, f'{df[plot_cols].corr().iloc[i, j]:.2f}',
                               ha="center", va="center", color="black", fontsize=8)
        plt.colorbar(im, ax=axes[1,0])
    # 5. Individual scatter plots vs saturation
    if 'saturation' in df.columns:
        for i, method in enumerate(method_names[:n_scatter]):
            row = 1
            col = i+1
            axes[row, col].scatter(df['saturation'], df[method], alpha=0.7, s=50)
            axes[row, col].set_xlabel('Saturation Score')
            axes[row, col].set_ylabel(f'{method} Score')
            axes[row, col].set_title(f'Saturation vs {method}')
            corr, _ = pearsonr(df['saturation'], df[method])
            axes[row, col].text(0.05, 0.95, f'r = {corr:.3f}', 
                               transform=axes[row, col].transAxes, 
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    plt.tight_layout()
    correlation_plot_path = os.path.join(results_dir, f"correlation_analysis_{target}.png")
    plt.savefig(correlation_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved correlation analysis → {correlation_plot_path}")
    # Print summary of findings
    print("\n" + "="*60)
    print("CORRELATION ANALYSIS SUMMARY")
    print("="*60)
    if efficiency_scores:
        best_idx = np.argmax(efficiency_scores)
        best_method = method_names[best_idx]
        best_efficiency = efficiency_scores[best_idx]
        best_correlation = correlations[best_idx]
        best_time = avg_times[best_idx]
        print(f"BEST METHOD: {best_method}")
        print(f"  Efficiency Score: {best_efficiency:.3f}")
        print(f"  Correlation with Saturation: {best_correlation:.3f}")
        print(f"  Average Time: {best_time:.3f}s")
        print(f"  Speedup vs Saturation: {df['saturation_time'].mean()/best_time:.1f}x")
        print(f"\nALL METHODS RANKED BY EFFICIENCY:")
        for i, idx in enumerate(sorted_indices):
            method = method_names[idx]
            efficiency = efficiency_scores[idx]
            correlation = correlations[idx]
            time = avg_times[idx]
            print(f"  {i+1}. {method}: efficiency={efficiency:.3f}, corr={correlation:.3f}, time={time:.3f}s")
    return best_method if efficiency_scores else None

def create_comprehensive_plots(df, results_dir, target):
    """Create analysis plots"""
    
    # Set style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # 1. Computational Complexity Analysis
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    sequence_lengths = [len(seq) for seq in df.get('sequences', [])]
    
    # Time vs sequence length
    if 'saturation_time' in df.columns and sequence_lengths:
        axes[0,0].scatter(sequence_lengths, df['saturation_time'], alpha=0.7, s=50)
        # Fit polynomial
        z = np.polyfit(sequence_lengths, df['saturation_time'], 2)
        p = np.poly1d(z)
        x_trend = np.linspace(min(sequence_lengths), max(sequence_lengths), 100)
        axes[0,0].plot(x_trend, p(x_trend), 'r--', alpha=0.8, label=f'Quadratic fit')
        axes[0,0].set_xlabel('Sequence Length')
        axes[0,0].set_ylabel('Processing Time (s)')
        axes[0,0].set_title('Computational Complexity: Saturation Method')
        axes[0,0].legend()
        
        # Add R²
        r2 = r2_score(df['saturation_time'], p(sequence_lengths))
        axes[0,0].text(0.05, 0.95, f'R² = {r2:.3f}', transform=axes[0,0].transAxes, 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # Random masking complexity
    pp_timing_cols = [col for col in df.columns if col.endswith('_time') and col != 'saturation_time']
    if pp_timing_cols and sequence_lengths:
        for col in pp_timing_cols[:3]:  # Show first 3 methods
            method_name = col.replace('_time', '')
            axes[0,1].scatter(sequence_lengths, df[col], alpha=0.7, s=50, label=method_name)
        
        # Linear fit for random masking (using individual data points)
        if len(sequence_lengths) > 1:
            # Use all data points for fitting
            all_times = []
            all_lengths = []
            for col in pp_timing_cols:
                all_times.extend(df[col].values)
                all_lengths.extend(sequence_lengths)
            
            if len(all_times) > 1:
                z_linear = np.polyfit(all_lengths, all_times, 1)
                p_linear = np.poly1d(z_linear)
                axes[0,1].plot(x_trend, p_linear(x_trend), 'g--', alpha=0.8, label='Linear fit')
        
        axes[0,1].set_xlabel('Sequence Length')
        axes[0,1].set_ylabel('Processing Time (s)')
        axes[0,1].set_title('Computational Complexity: Random Masking')
        axes[0,1].legend()
    
    # 2. Accuracy vs Speed Trade-off
    if 'saturation' in df.columns and pp_timing_cols:
        # Calculate correlations
        correlations = []
        method_names = []
        for col in pp_timing_cols:
            pp_col = col.replace('_time', '')
            if pp_col in df.columns:
                corr, _ = pearsonr(df['saturation'], df[pp_col])
                correlations.append(corr)
                method_names.append(pp_col)
        
        # Plot correlation vs time
        avg_times = [df[col].mean() for col in pp_timing_cols]
        axes[1,0].scatter(avg_times, correlations, s=100, alpha=0.8)
        for i, name in enumerate(method_names):
            axes[1,0].annotate(name, (avg_times[i], correlations[i]), 
                              xytext=(5, 5), textcoords='offset points')
        axes[1,0].set_xlabel('Average Processing Time (s)')
        axes[1,0].set_ylabel('Correlation with Saturation')
        axes[1,0].set_title('Accuracy vs Speed Trade-off')
        axes[1,0].grid(True, alpha=0.3)
    
    # 3. Memory Usage Analysis
    memory_cols = [col for col in df.columns if 'memory' in col]
    if memory_cols:
        memory_data = [df[col].mean() for col in memory_cols]
        memory_labels = [col.replace('_memory', '') for col in memory_cols]
        bars = axes[1,1].bar(memory_labels, memory_data, alpha=0.8)
        axes[1,1].set_ylabel('Memory Usage (MB)')
        axes[1,1].set_title('Memory Usage by Method')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, memory_data):
            axes[1,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                          f'{value:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    complexity_plot_path = os.path.join(results_dir, f"computational_complexity_{target}.png")
    plt.savefig(complexity_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved computational complexity analysis → {complexity_plot_path}")
    
    # 4. Method Ranking Dashboard
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    
    # Speed ranking
    if pp_timing_cols:
        avg_times = [df[col].mean() for col in pp_timing_cols]
        method_names = [col.replace('_time', '') for col in pp_timing_cols]
        
        # Sort by speed (ascending)
        sorted_indices = np.argsort(avg_times)
        sorted_times = [avg_times[i] for i in sorted_indices]
        sorted_names = [method_names[i] for i in sorted_indices]
        
        bars = axes[0,0].barh(sorted_names, sorted_times, alpha=0.8)
        axes[0,0].set_xlabel('Average Time (s)')
        axes[0,0].set_title('Speed Ranking (Faster = Better)')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, sorted_times)):
            axes[0,0].text(value + 0.01, bar.get_y() + bar.get_height()/2,
                          f'{value:.3f}s', va='center')
    
    # Accuracy ranking
    if 'saturation' in df.columns and pp_timing_cols:
        correlations = []
        for col in pp_timing_cols:
            pp_col = col.replace('_time', '')
            if pp_col in df.columns:
                corr, _ = pearsonr(df['saturation'], df[pp_col])
                correlations.append(abs(corr))  # Use absolute correlation
        
        # Sort by accuracy (descending)
        sorted_indices = np.argsort(correlations)[::-1]
        sorted_corrs = [correlations[i] for i in sorted_indices]
        sorted_names = [method_names[i] for i in sorted_indices]
        
        bars = axes[0,1].barh(sorted_names, sorted_corrs, alpha=0.8, color='green')
        axes[0,1].set_xlabel('|Correlation with Saturation|')
        axes[0,1].set_title('Accuracy Ranking (Higher = Better)')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, sorted_corrs)):
            axes[0,1].text(value + 0.01, bar.get_y() + bar.get_height()/2,
                          f'{value:.3f}', va='center')
    
    # Efficiency ranking (tokens per second)
    if 'saturation_time' in df.columns and sequence_lengths:
        saturation_efficiency = np.array(sequence_lengths) / df['saturation_time']
        efficiency_data = [saturation_efficiency.mean()]
        efficiency_names = ['saturation']
        
        for col in pp_timing_cols:
            pp_efficiency = np.array(sequence_lengths) / df[col]
            efficiency_data.append(pp_efficiency.mean())
            efficiency_names.append(col.replace('_time', ''))
        
        # Sort by efficiency (descending)
        sorted_indices = np.argsort(efficiency_data)[::-1]
        sorted_efficiency = [efficiency_data[i] for i in sorted_indices]
        sorted_names = [efficiency_names[i] for i in sorted_indices]
        
        bars = axes[0,2].barh(sorted_names, sorted_efficiency, alpha=0.8, color='orange')
        axes[0,2].set_xlabel('Tokens per Second')
        axes[0,2].set_title('Efficiency Ranking (Higher = Better)')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, sorted_efficiency)):
            axes[0,2].text(value + 0.1, bar.get_y() + bar.get_height()/2,
                          f'{value:.1f}', va='center')
    
    # 5. Confidence Analysis
    confidence_cols = [col for col in df.columns if 'confidence' in col]
    if confidence_cols:
        confidence_data = [df[col].mean() for col in confidence_cols]
        confidence_labels = [col.replace('_confidence', '') for col in confidence_cols]
        
        bars = axes[1,0].bar(confidence_labels, confidence_data, alpha=0.8, color='purple')
        axes[1,0].set_ylabel('Average Confidence (Std Dev)')
        axes[1,0].set_title('Method Reliability (Lower = More Reliable)')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, confidence_data):
            axes[1,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                          f'{value:.3f}', ha='center', va='bottom')
    
    # 6. Speedup Analysis
    if 'saturation_time' in df.columns and pp_timing_cols:
        saturation_avg = df['saturation_time'].mean()
        speedups = []
        speedup_labels = []
        for col in pp_timing_cols:
            pp_avg = df[col].mean()
            if pp_avg > 0:
                speedup = saturation_avg / pp_avg
                speedups.append(speedup)
                speedup_labels.append(col.replace('_time', ''))
        
        bars = axes[1,1].bar(speedup_labels, speedups, alpha=0.8, color='red')
        axes[1,1].set_ylabel('Speedup Factor')
        axes[1,1].set_title('Speedup vs Saturation Method')
        axes[1,1].tick_params(axis='x', rotation=45)
        axes[1,1].axhline(y=1, color='black', linestyle='--', alpha=0.7, label='No speedup')
        
        # Add value labels
        for bar, value in zip(bars, speedups):
            axes[1,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                          f'{value:.1f}x', ha='center', va='bottom')
        axes[1,1].legend()
    
    # 7. Performance vs Time Scatter
    if 'saturation' in df.columns and 'saturation_time' in df.columns:
        axes[1,2].scatter(df['saturation_time'], df['saturation'], alpha=0.7, s=50)
        axes[1,2].set_xlabel('Processing Time (s)')
        axes[1,2].set_ylabel('Saturation Score')
        axes[1,2].set_title('Performance vs Time')
        
        # Add trend line
        z = np.polyfit(df['saturation_time'], df['saturation'], 1)
        p = np.poly1d(z)
        axes[1,2].plot(df['saturation_time'], p(df['saturation_time']), 'r--', alpha=0.8)
    
    plt.tight_layout()
    dashboard_plot_path = os.path.join(results_dir, f"method_ranking_dashboard_{target}.png")
    plt.savefig(dashboard_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved method ranking dashboard → {dashboard_plot_path}")
    
    # 8. Correlation Analysis
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Correlation heatmap with all metrics
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    # Remove time and memory columns for cleaner heatmap
    plot_cols = [col for col in numeric_cols if not any(x in col for x in ['time', 'memory', 'confidence'])]
    if len(plot_cols) > 1:
        correlation_matrix = df[plot_cols].corr()
        
        im = axes[0,0].imshow(correlation_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        axes[0,0].set_xticks(range(len(correlation_matrix.columns)))
        axes[0,0].set_yticks(range(len(correlation_matrix.columns)))
        axes[0,0].set_xticklabels(correlation_matrix.columns, rotation=45, ha='right')
        axes[0,0].set_yticklabels(correlation_matrix.columns)
        axes[0,0].set_title('Correlation Matrix (Performance Metrics)')
        
        # Add correlation values
        for i in range(len(correlation_matrix.columns)):
            for j in range(len(correlation_matrix.columns)):
                text = axes[0,0].text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                                     ha="center", va="center", color="black", fontsize=8)
        
        plt.colorbar(im, ax=axes[0,0])
    
    # Distribution comparison with confidence intervals
    pp_cols = [col for col in df.columns if col.startswith('pp_') and not col.endswith('_time')]
    if pp_cols and confidence_cols:
        for i, (pp_col, conf_col) in enumerate(zip(pp_cols, confidence_cols)):
            if i < 3:  # Show first 3 methods
                axes[0,1].errorbar(df[pp_col].mean(), i, xerr=df[conf_col].mean(), 
                                  fmt='o', capsize=5, capthick=2, markersize=8,
                                  label=pp_col)
        axes[0,1].set_xlabel('Perplexity Value')
        axes[0,1].set_ylabel('Method')
        axes[0,1].set_title('Perplexity with Confidence Intervals')
        axes[0,1].legend()
        axes[0,1].set_yticks(range(len(pp_cols[:3])))
        axes[0,1].set_yticklabels(pp_cols[:3])
    
    # Spearman vs Pearson correlation
    if 'saturation' in df.columns and pp_cols:
        pearson_corrs = []
        spearman_corrs = []
        method_names = []
        
        for pp_col in pp_cols:
            if pp_col in df.columns:
                pearson_corr, _ = pearsonr(df['saturation'], df[pp_col])
                spearman_corr, _ = spearmanr(df['saturation'], df[pp_col])
                pearson_corrs.append(pearson_corr)
                spearman_corrs.append(spearman_corr)
                method_names.append(pp_col)
        
        x = np.arange(len(method_names))
        width = 0.35
        
        axes[1,0].bar(x - width/2, pearson_corrs, width, label='Pearson', alpha=0.8)
        axes[1,0].bar(x + width/2, spearman_corrs, width, label='Spearman', alpha=0.8)
        axes[1,0].set_xlabel('Method')
        axes[1,0].set_ylabel('Correlation Coefficient')
        axes[1,0].set_title('Pearson vs Spearman Correlation')
        axes[1,0].set_xticks(x)
        axes[1,0].set_xticklabels(method_names, rotation=45)
        axes[1,0].legend()
        axes[1,0].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Performance stability analysis
    if 'saturation' in df.columns and pp_cols:
        stability_metrics = []
        for pp_col in pp_cols:
            if pp_col in df.columns:
                # Calculate coefficient of variation (std/mean)
                cv = df[pp_col].std() / df[pp_col].mean()
                stability_metrics.append(cv)
        
        bars = axes[1,1].bar(method_names, stability_metrics, alpha=0.8, color='teal')
        axes[1,1].set_ylabel('Coefficient of Variation')
        axes[1,1].set_title('Method Stability (Lower = More Stable)')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, stability_metrics):
            axes[1,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                          f'{value:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    advanced_plot_path = os.path.join(results_dir, f"advanced_correlation_analysis_{target}.png")
    plt.savefig(advanced_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved advanced correlation analysis → {advanced_plot_path}")

def create_additional_plots(df, results_dir, target):
    """Create additional plots"""
    
    # 1. Timing analysis
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Timing vs sequence length
    sequence_lengths = [len(seq) for seq in df.get('sequences', [])]
    if 'saturation_time' in df.columns and sequence_lengths:
        axes[0,0].scatter(sequence_lengths, df['saturation_time'], alpha=0.6)
        axes[0,0].set_xlabel('Sequence Length')
        axes[0,0].set_ylabel('Saturation Time (s)')
        axes[0,0].set_title('Saturation Time vs Sequence Length')
    
    # Perplexity timing comparison
    pp_timing_cols = [col for col in df.columns if col.endswith('_time') and col != 'saturation_time']
    if pp_timing_cols:
        timing_data = [df[col].mean() for col in pp_timing_cols]
        timing_labels = [col.replace('_time', '') for col in pp_timing_cols]
        axes[0,1].bar(timing_labels, timing_data)
        axes[0,1].set_ylabel('Average Time (s)')
        axes[0,1].set_title('Average Time per Method')
        axes[0,1].tick_params(axis='x', rotation=45)
    
    # Speedup analysis
    if 'saturation_time' in df.columns and pp_timing_cols:
        saturation_time = df['saturation_time'].mean()
        speedups = []
        speedup_labels = []
        for col in pp_timing_cols:
            avg_time = df[col].mean()
            if avg_time > 0:
                speedup = saturation_time / avg_time
                speedups.append(speedup)
                speedup_labels.append(col.replace('_time', ''))
        
        if speedups:
            axes[1,0].bar(speedup_labels, speedups)
            axes[1,0].set_ylabel('Speedup Factor')
            axes[1,0].set_title('Speedup: Saturation vs Random Masking')
            axes[1,0].tick_params(axis='x', rotation=45)
            axes[1,0].axhline(y=1, color='red', linestyle='--', alpha=0.7)
    
    # Efficiency analysis (time per token)
    if 'saturation_time' in df.columns and sequence_lengths:
        tokens_per_second = np.array(sequence_lengths) / df['saturation_time']
        axes[1,1].hist(tokens_per_second, bins=20, alpha=0.7)
        axes[1,1].set_xlabel('Tokens per Second')
        axes[1,1].set_ylabel('Frequency')
        axes[1,1].set_title('Processing Efficiency Distribution')
    
    plt.tight_layout()
    timing_plot_path = os.path.join(results_dir, f"timing_analysis_{target}.png")
    plt.savefig(timing_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved timing analysis → {timing_plot_path}")
    
    # 2. Method comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Correlation heatmap
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlation_matrix = df[numeric_cols].corr()
    
    im = axes[0,0].imshow(correlation_matrix, cmap='coolwarm', vmin=-1, vmax=1)
    axes[0,0].set_xticks(range(len(correlation_matrix.columns)))
    axes[0,0].set_yticks(range(len(correlation_matrix.columns)))
    axes[0,0].set_xticklabels(correlation_matrix.columns, rotation=45, ha='right')
    axes[0,0].set_yticklabels(correlation_matrix.columns)
    axes[0,0].set_title('Correlation Matrix')
    
    # Add correlation values
    for i in range(len(correlation_matrix.columns)):
        for j in range(len(correlation_matrix.columns)):
            text = axes[0,0].text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                                 ha="center", va="center", color="black", fontsize=8)
    
    plt.colorbar(im, ax=axes[0,0])
    
    # Distribution comparison
    pp_cols = [col for col in df.columns if col.startswith('pp_')]
    if pp_cols:
        for col in pp_cols:
            axes[0,1].hist(df[col].dropna(), alpha=0.5, label=col, bins=20)
        axes[0,1].set_xlabel('Perplexity Value')
        axes[0,1].set_ylabel('Frequency')
        axes[0,1].set_title('Perplexity Distributions')
        axes[0,1].legend()
    
    # Saturation vs perplexity scatter
    if 'saturation' in df.columns and pp_cols:
        for col in pp_cols:
            axes[1,0].scatter(df['saturation'], df[col], alpha=0.6, label=col)
        axes[1,0].set_xlabel('Saturation Score')
        axes[1,0].set_ylabel('Perplexity')
        axes[1,0].set_title('Saturation vs Perplexity')
        axes[1,0].legend()
    
    # Performance vs time scatter
    if 'saturation' in df.columns and 'saturation_time' in df.columns:
        axes[1,1].scatter(df['saturation_time'], df['saturation'], alpha=0.6)
        axes[1,1].set_xlabel('Processing Time (s)')
        axes[1,1].set_ylabel('Saturation Score')
        axes[1,1].set_title('Performance vs Time')
    
    plt.tight_layout()
    comparison_plot_path = os.path.join(results_dir, f"method_comparison_{target}.png")
    plt.savefig(comparison_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved method comparison → {comparison_plot_path}")

def main():
    # ─── Load config & FASTAs ─────────────────────────────────────────
    with open('config.yaml') as f:
        cfg = yaml.safe_load(f)
    
    # HARDCODED! Use the new benchmarking dataset
    target = 'cazy'
    paths = [os.path.join('inputs', 'benchmarking', target, 'cazy_medium_subset.fasta')]

    headers, sequences = [], []
    for p in tqdm(paths, desc="Loading FASTAs", unit="file"):
        h, s = load_sequences(p)
        headers.extend(h)
        sequences.extend(s)

    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    results_dir = os.path.join('results', target)
    os.makedirs(results_dir, exist_ok=True)

    print(f"Processing {len(sequences)} sequences on {device}")

    # ─── Compute single forward pass NLL (optimizer method) ──────────────────────────
    single_forward_nll, single_forward_times, single_forward_memory = compute_single_forward_nll(headers, sequences, device=device)

    # ─── Compute new masked‐one‐at‐a‐time NLL ──────────────────────────
    avg_masked_nll, saturation_times, saturation_memory = compute_avg_masked_nll(headers, sequences, device=device)

    # ─── Compute random‐masking perplexities ──────────────────────────
    maskings = list(range(1, 9))
    pp_dict, timing_dict, memory_dict, confidence_dict = compute_perplexities(headers, sequences, device=device, maskings_list=maskings)

    # ─── Assemble DataFrame & save ───────────────────────────────────
    df = pd.DataFrame({
        'single_forward': single_forward_nll,
        'single_forward_time': single_forward_times,
        'single_forward_memory': single_forward_memory,
        'saturation': avg_masked_nll,
        'saturation_time': saturation_times,
        'saturation_memory': saturation_memory,
        'sequences': sequences
    })
    
    for n in maskings:
        df[f'pp_{n}'] = pp_dict[n]
        df[f'pp_{n}_time'] = timing_dict[n]
        df[f'pp_{n}_memory'] = memory_dict[n]
        df[f'pp_{n}_confidence'] = confidence_dict[n]
    
    out_csv = os.path.join(results_dir, f"saturation_vs_pp_{target}.csv")
    df.to_csv(out_csv, index=False)
    print(f"Saved CSV → {out_csv}")

    # ─── Create plots ──────────────────────────────────────
    create_comprehensive_plots(df, results_dir, target)
    create_additional_plots(df, results_dir, target)
    create_correlation_analysis_plot(df, results_dir, target)

    # ─── Plot correlation grid ────────────────────────────────────────
    metrics = [f'pp_{n}' for n in maskings]
    k = len(metrics)
    fig, axes = plt.subplots(k, k, figsize=(4*k, 4*k), sharex='col', sharey='row')
    cmap = cm.get_cmap('bwr')
    norm = Normalize(vmin=-1, vmax=1)

    for i, mi in enumerate(metrics):
        for j, mj in enumerate(metrics):
            ax = axes[i, j]
            x = df[mj]                       # pp_mj
            y = df[mi]                       # pp_mi

            if i > j:
                # Lower tri: 2D‐histogram
                bins = int(np.sqrt(len(x)))
                ax.hist2d(x, y, bins=bins, cmap='Greys')
            elif i == j:
                # Diagonal: scatter vs saturation
                ax.scatter(df['saturation'], df[mi], s=15, color='k')
                r, _ = pearsonr(df['saturation'], df[mi])
                ax.set_facecolor(cmap(norm(r)))
                ax.text(0.5, 0.5, f"{r:.2f}",
                        transform=ax.transAxes, ha='center', va='center',
                        fontsize=24, fontweight='bold',
                        color='white' if abs(r) > 0.5 else 'black')
            else:
                # Upper tri: just Pearson‐annotated
                r, _ = pearsonr(x, y)
                ax.set_facecolor(cmap(norm(r)))
                ax.text(0.5, 0.5, f"{r:.2f}",
                        transform=ax.transAxes, ha='center', va='center',
                        fontsize=24, fontweight='bold',
                        color='white' if abs(r) > 0.5 else 'black')

            ax.tick_params(labelsize=12)
            if i == k-1:
                ax.set_xlabel(mj, fontsize=14)
            if j == 0:
                ax.set_ylabel(mi, fontsize=14)

    plt.tight_layout()
    out_png = os.path.join(results_dir, f"saturation_vs_pp_grid_{target}.png")
    plt.savefig(out_png, dpi=300)
    plt.close()
    print(f"Saved grid plot → {out_png}")

    # ─── Print summary statistics ────────────────────────────────────
    print("\n" + "="*50)
    print("SUMMARY STATISTICS")
    print("="*50)
    
    print(f"Total sequences processed: {len(sequences)}")
    print(f"Average sequence length: {np.mean([len(s) for s in sequences]):.1f}")
    
    if 'single_forward_time' in df.columns:
        print(f"Average single forward time: {df['single_forward_time'].mean():.3f}s")
        print(f"Total single forward time: {df['single_forward_time'].sum():.1f}s")
    
    if 'saturation_time' in df.columns:
        print(f"Average saturation time: {df['saturation_time'].mean():.3f}s")
        print(f"Total saturation time: {df['saturation_time'].sum():.1f}s")
    
    for n in maskings:
        time_col = f'pp_{n}_time'
        if time_col in df.columns:
            print(f"Average pp_{n} time: {df[time_col].mean():.3f}s")
            print(f"Total pp_{n} time: {df[time_col].sum():.1f}s")
    
    # Speedup analysis
    if 'saturation_time' in df.columns:
        saturation_avg = df['saturation_time'].mean()
        single_forward_avg = df['single_forward_time'].mean() if 'single_forward_time' in df.columns else 0
        
        print(f"\nSpeedup Analysis:")
        if single_forward_avg > 0:
            speedup_vs_single = saturation_avg / single_forward_avg
            print(f"Speedup (saturation vs single forward): {speedup_vs_single:.2f}x")
        
        for n in maskings:
            time_col = f'pp_{n}_time'
            if time_col in df.columns:
                pp_avg = df[time_col].mean()
                if pp_avg > 0:
                    speedup = saturation_avg / pp_avg
                    print(f"Speedup (saturation vs pp_{n}): {speedup:.2f}x")
                    
                    if single_forward_avg > 0:
                        speedup_vs_single = single_forward_avg / pp_avg
                        print(f"Speedup (single forward vs pp_{n}): {speedup_vs_single:.2f}x")

if __name__ == '__main__':
    main()
