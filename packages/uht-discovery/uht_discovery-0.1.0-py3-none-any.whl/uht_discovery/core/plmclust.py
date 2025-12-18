import os
import glob
import yaml
import datetime
import torch
import esm
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from .common import project_dir
import time

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

def compute_embeddings(headers, sequences, device='cpu', batch_size=1):
    """
    Compute deterministic ESM2 embeddings (no random masking).
    Returns numpy array of shape (N, D).
    """
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval().to(device)
    batch_converter = alphabet.get_batch_converter()
    embeddings = []
    total = len(sequences)
    print(f"Computing embeddings for {total} sequences...")
    for i in tqdm(range(0, total, batch_size), desc="Computing embeddings"):
        batch = list(zip(headers[i:i+batch_size], sequences[i:i+batch_size]))
        labels, strs, tokens = batch_converter(batch)
        tokens = tokens.to(device)
        with torch.no_grad():
            out = model(tokens, repr_layers=[33], return_contacts=False)
            reps = out['representations'][33]
            for j, seq in enumerate(strs):
                emb = reps[j, 1:len(seq)+1].mean(0)
                embeddings.append(emb.cpu().numpy())
        # Memory cleanup
        del out, reps, tokens
        if device == 'mps':
            torch.mps.empty_cache()
    print("  Progress: Done.")
    return np.array(embeddings)

def compute_perplexities_stats(headers, sequences, device='cpu', n_maskings=5):
    """
    Compute mean/std perplexities over n_maskings.
    Returns lists means, stds.
    """
    N = len(sequences)
    if n_maskings == 0:
        return [None]*N, [None]*N
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval().to(device)
    batch_converter = alphabet.get_batch_converter()
    criterion = torch.nn.CrossEntropyLoss(ignore_index=alphabet.padding_idx, reduction='sum')
    means, stds = [], []
    print(f"Computing perplexities for {N} sequences...")
    for idx in tqdm(range(N), desc="Computing perplexities"):
        pps = []
        for _ in range(n_maskings):
            with torch.no_grad():
                lbl, strs, tokens = batch_converter([(headers[idx], sequences[idx])])
                tokens = tokens.to(device)
                masked = tokens.clone()
                prob = torch.full(masked.shape, 0.15, device=masked.device)
                mask = (masked==alphabet.padding_idx)|(masked==alphabet.cls_idx)|(masked==alphabet.eos_idx)
                prob.masked_fill_(mask, 0.0)
                idxs = torch.bernoulli(prob).bool()
                masked[idxs] = alphabet.mask_idx
                out = model(masked, repr_layers=[33], return_contacts=False)
                logits = out['logits'][idxs]
                targets = tokens[idxs]
                if targets.numel()>0:
                    loss = criterion(logits, targets)
                    pp = float(np.exp(loss.item()/targets.numel()))
                else:
                    pp = float('inf')
                pps.append(pp)
            # Memory cleanup for each masking
            del out, logits, targets, masked, tokens
            if device == 'mps':
                torch.mps.empty_cache()
        means.append(float(np.mean(pps)))
        stds.append(float(np.std(pps)) if n_maskings>1 else 0.0)
    print("  Progress: Done.")
    return means, stds

def cluster_embeddings(embeddings, n_clusters):
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):
        km = KMeans(n_clusters=n_clusters, random_state=0, n_init=10)
        return km.fit_predict(embeddings)

def perform_silhouette_search(embeddings, min_k, max_k, num_samples, results_dir, target):
    records = []
    iter_no = 1
    cur_min, cur_max = min_k, max_k
    cmap = plt.get_cmap('tab10')
    while True:
        span = cur_max - cur_min +1
        if span <= num_samples:
            ks = list(range(cur_min, cur_max+1))
            delta = 1
        else:
            step = (cur_max-cur_min)/(num_samples-1)
            ks = sorted({int(np.floor(cur_min+i*step)) for i in range(num_samples)})
            ks[0], ks[-1] = cur_min, cur_max
            delta = ks[1]-ks[0]
        scores = {}
        for k in ks:
            lbls = cluster_embeddings(embeddings, k)
            score = silhouette_score(embeddings, lbls)
            scores[k] = score
            records.append({'iteration':iter_no,'tested_k':k,'silhouette_score':score})
        best_k = max(scores, key=scores.get)
        new_min = max(cur_min, best_k-delta)
        new_max = min(cur_max, best_k+delta)
        if (new_min==cur_min and new_max==cur_max) or ((new_max-new_min)<2):
            final_k = best_k
            break
        cur_min, cur_max = new_min, new_max
        iter_no += 1
    df = pd.DataFrame(records)
    csv_all = os.path.join(results_dir, f"silhouette_search_{target}_all_rounds.csv")
    df.to_csv(csv_all, index=False)
    plt.figure(figsize=(8,6))
    for i in sorted(df.iteration.unique()):
        sub = df[df.iteration==i]
        plt.scatter(sub.tested_k, sub.silhouette_score, color=cmap((i-1)%10), label=f'Iteration {i}', s=50)
    plt.xlabel('k')
    plt.ylabel('Silhouette Score')
    plt.title(f"Silhouette Search (TARGET={target})")
    plt.legend(fontsize='small')
    plt.tight_layout()
    png = os.path.join(results_dir, f"silhouette_search_{target}.png")
    plt.savefig(png, dpi=300)
    plt.close()
    return final_k, df, csv_all, png

def write_run_log(log_path, start_time, end_time, input_files, output_files,
                  target, cluster_param, silhouette_range, final_k,
                  num_sequences, n_maskings, num_iterations):
    duration = end_time - start_time
    with open(log_path, 'w') as log_f:
        log_f.write("pLM-clust Run Log\n=================\n\n")
        log_f.write(f"Run start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Run end:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Duration:  {duration}\n\n")
        log_f.write("Configuration:\n")
        log_f.write(f"  TARGET: {target}\n  cluster_number: {cluster_param}\n")
        if isinstance(cluster_param, str) and cluster_param.lower()=='auto':
            log_f.write(f"  silhouette_range: {silhouette_range}\n  final k: {final_k}\n  iterations: {num_iterations}\n")
        else:
            log_f.write(f"  final k (fixed): {final_k}\n")
        log_f.write(f"Sequences: {num_sequences}\nmaskings: {n_maskings}\n\n")
        log_f.write("Inputs:\n")
        for f in input_files:
            log_f.write(f"  - {f}\n")
        log_f.write("\nOutputs:\n")
        for f in output_files:
            log_f.write(f"  - {f}\n")
        log_f.write("\nNotes:\n  - Embeddings: ESM2 t33_650M_UR50D\n")

def run(cfg):
    target = project_dir('plmclust', cfg)
    if not target:
        raise ValueError("Need project directory")
    cluster_param = cfg.get('plmclust_cluster_number', 10)
    silhouette_range = cfg.get('silhouette_range', [2,10])
    n_maskings = cfg.get('plm_clust_replicates', 5)
    start_time = datetime.datetime.now()
    fasta_paths = sorted(glob.glob(os.path.join('inputs','plmclust',target,'*.fasta')))
    headers, sequences = [], []
    for fp in fasta_paths:
        hdrs, seqs = load_sequences(fp)
        headers.extend(hdrs)
        sequences.extend(seqs)
    num_sequences = len(sequences)
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    #device = 'cpu'
    print(f"Using device: {device}")
    results_dir = os.path.join('results','plmclust',target)
    os.makedirs(results_dir, exist_ok=True)
    embeddings = compute_embeddings(headers, sequences, device=device)
    if isinstance(cluster_param, str) and cluster_param.lower()=='auto':
        min_k, max_k = map(int, silhouette_range)
        best_k, sil_df, sil_csv, sil_png = perform_silhouette_search(
            embeddings, max(2,min_k), min(max_k,num_sequences-1), num_samples=10,
            results_dir=results_dir, target=target)
        final_k = best_k
        num_iters = sil_df.iteration.max()
        print(f"Auto-selected k: {final_k}")
    else:
        final_k = int(cluster_param)
        sil_csv = sil_png = None
        num_iters = 0
        print(f"Using fixed k: {final_k}")
    labels = cluster_embeddings(embeddings, final_k)
    perps, perps_std = compute_perplexities_stats(
        headers, sequences, device=device, n_maskings=n_maskings)
    metrics = [(-pp if pp is not None else None) for pp in perps]
    rep = {}
    for i, lbl in enumerate(labels):
        m = metrics[i]
        if lbl not in rep or (m is not None and m > rep[lbl]['metric']):
            rep[lbl] = {'header': headers[i], 'seq': sequences[i], 'metric': m}
    rep_fasta = os.path.join(results_dir, f"top_cluster_representatives_{target}.fasta")
    with open(rep_fasta, 'w') as wf:
        for lbl in sorted(rep):
            wf.write(f"{rep[lbl]['header']} cluster={lbl}\n{rep[lbl]['seq']}\n")
    df = pd.DataFrame({
        'header': headers,
        'sequence': sequences,
        'cluster': labels,
        'perplexity': perps,
        'negative_plmll': metrics
    })
    if n_maskings > 2:
        df['perplexity_std'] = perps_std
    metrics_csv = os.path.join(results_dir, f"pLM-clust_sequences_with_metrics_{target}.csv")
    df.to_csv(metrics_csv, index=False)
    cluster_dir = os.path.join(results_dir, f"{final_k}_clusters_{target}")
    os.makedirs(cluster_dir, exist_ok=True)
    cluster_paths = []
    for cid in set(labels):
        pth = os.path.join(cluster_dir, f"cluster_{cid}.fasta")
        with open(pth, 'w') as cf:
            for h, s, l in zip(headers, sequences, labels):
                if l == cid:
                    cf.write(f"{h}\n{s}\n")
        cluster_paths.append(pth)
    data_2d = PCA(n_components=50).fit_transform(embeddings) if embeddings.shape[1] > 50 else embeddings
    coords = TSNE(n_components=2, random_state=42, max_iter=1000).fit_transform(data_2d)
    tsne_df = pd.DataFrame({
        'header': headers,
        'Dim1': coords[:, 0],
        'Dim2': coords[:, 1],
        'cluster': labels,
        'perplexity': perps
    })
    tsne_csv = os.path.join(results_dir, f"tsne_coordinates_{target}.csv")
    tsne_df.to_csv(tsne_csv, index=False)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=tsne_df, x='Dim1', y='Dim2', hue='cluster', s=50)
    plt.tight_layout()
    tsne_png = os.path.join(results_dir, f"tsne_clusters_{target}.png")
    plt.savefig(tsne_png, dpi=300)
    plt.close()
    end_time = datetime.datetime.now()
    log_path = os.path.join(results_dir, f"run_log_{target}.txt")
    outputs = [rep_fasta, metrics_csv, tsne_csv, tsne_png] + cluster_paths
    if sil_csv:
        outputs += [sil_csv, sil_png]
    write_run_log(log_path, start_time, end_time, fasta_paths, outputs,
                  target, cluster_param, silhouette_range, final_k,
                  num_sequences, n_maskings, num_iters)
    print(f"Top representatives: {rep_fasta}")
    print(f"Metrics CSV: {metrics_csv}")
    print(f"t-SNE coords saved to: {tsne_csv}")
    print(f"t-SNE plot: {tsne_png}")
