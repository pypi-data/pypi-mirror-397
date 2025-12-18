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
from Bio.SeqRecord import SeqRecord

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
            
            # Check if old cache exists and needs migration
            needs_migration = False
            if os.path.exists(self.db_path):
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        # Check if table exists and has old schema (without nll_score column)
                        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='embeddings'")
                        if cursor.fetchone():
                            cursor = conn.execute("PRAGMA table_info(embeddings)")
                            columns = [row[1] for row in cursor.fetchall()]
                            if 'nll_score' not in columns:
                                needs_migration = True
                except:
                    # If we can't read the database, we'll recreate it
                    needs_migration = True
            
            if needs_migration:
                # Remove old cache database to force recreation with new schema
                print("Removing old embedding cache (will be recreated with embeddings + NLL scores)...")
                try:
                    os.remove(self.db_path)
                except:
                    pass
            
            # Create new database with updated schema
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        sequence_hash TEXT PRIMARY KEY,
                        sequence TEXT NOT NULL,
                        embedding BLOB NOT NULL,
                        nll_score REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sequence_hash ON embeddings(sequence_hash)")
        
        def _hash_sequence(self, sequence):
            import hashlib
            return hashlib.sha256(sequence.encode()).hexdigest()
        
        def get_embedding_and_score(self, sequence):
            """Get both embedding and NLL score from cache if they exist."""
            import sqlite3
            import pickle
            sequence_hash = self._hash_sequence(sequence)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT embedding, nll_score FROM embeddings WHERE sequence_hash = ?",
                    (sequence_hash,)
                )
                result = cursor.fetchone()
                if result:
                    embedding = pickle.loads(result[0])
                    nll_score = result[1]
                    # Check if nll_score is None or invalid (0.0 is impossible for NLL)
                    if nll_score is None or nll_score == 0.0:
                        return None, None
                    return embedding, nll_score
                return None, None
        
        def remove_embedding(self, sequence):
            """Remove an embedding from cache."""
            import sqlite3
            sequence_hash = self._hash_sequence(sequence)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "DELETE FROM embeddings WHERE sequence_hash = ?",
                    (sequence_hash,)
                )
        
        def store_embedding_and_score(self, sequence, embedding, nll_score):
            """Store both embedding and NLL score in cache."""
            import sqlite3
            import pickle
            sequence_hash = self._hash_sequence(sequence)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO embeddings (sequence_hash, sequence, embedding, nll_score) VALUES (?, ?, ?, ?)",
                    (sequence_hash, sequence, pickle.dumps(embedding), float(nll_score))
                )
        
        # Backward compatibility methods (deprecated, but kept for migration)
        def get_embedding(self, sequence):
            """Deprecated: Use get_embedding_and_score instead."""
            embedding, _ = self.get_embedding_and_score(sequence)
            return embedding
        
        def store_embedding(self, sequence, embedding):
            """Deprecated: Use store_embedding_and_score instead."""
            # This should not be used anymore, but if called, store with a dummy score
            # that will be overwritten on next computation
            self.store_embedding_and_score(sequence, embedding, 0.0)

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
    Uses the caching system to avoid recomputing embeddings and scores.
    
    Both embeddings and NLL scores are computed in a single forward pass and
    cached together for efficiency.
    
    Returns tuple of (embeddings, scores) where embeddings is numpy array of shape (N, D).
    """
    # Initialize the embedding cache
    embedding_cache = EmbeddingCache()
    
    # Check cache first - get both embeddings and scores
    print("Checking embedding cache...")
    cached_embeddings = {}
    cached_scores = {}
    missing_sequences = []
    missing_headers = []
    missing_indices = []
    
    for i, (header, sequence) in enumerate(zip(headers, sequences)):
        embedding, nll_score = embedding_cache.get_embedding_and_score(sequence)
        if embedding is not None and nll_score is not None and nll_score != 0.0:
            # Both embedding and score are valid (nll_score != 0.0 is already checked in get_embedding_and_score, but double-check)
            cached_embeddings[header] = embedding
            cached_scores[header] = nll_score
        elif embedding is not None:
            # Embedding exists but score is None or 0.0 - remove old entry and recompute both
            embedding_cache.remove_embedding(sequence)
            missing_sequences.append(sequence)
            missing_headers.append(header)
            missing_indices.append(i)
        else:
            # Neither exists - need to compute both
            missing_sequences.append(sequence)
            missing_headers.append(header)
            missing_indices.append(i)
    
    print(f"Found {len(cached_embeddings)} cached embeddings with scores")
    
    # Initialize scores list with cached values or placeholders
    all_scores = [0.0] * len(sequences)
    for i, header in enumerate(headers):
        if header in cached_scores:
            all_scores[i] = cached_scores[header]
    
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
        
        # Store new embeddings and scores in cache together
        for header, embedding, score in zip(missing_headers, new_embeddings, new_scores):
            sequence = sequences[headers.index(header)]
            embedding_cache.store_embedding_and_score(sequence, embedding, score)
            cached_embeddings[header] = embedding
            # Update the score at the correct index
            idx = headers.index(header)
            all_scores[idx] = score
    
    # Verify that all scores are properly computed (not 0.0)
    zero_score_count = sum(1 for score in all_scores if score == 0.0)
    if zero_score_count > 0:
        print(f"  Warning: {zero_score_count} sequences still have 0.0 scores. This may indicate an error in score computation.")
    
    # Report score statistics
    valid_scores = [score for score in all_scores if score != 0.0]
    if valid_scores:
        print(f"  ✓ All {len(valid_scores)} sequences have valid NLL scores")
        print(f"  Score statistics: min={min(valid_scores):.4f}, max={max(valid_scores):.4f}, mean={np.mean(valid_scores):.4f}")
    
    # Combine cached and new embeddings
    # BUG FIX: Previously, embeddings variable was referenced in assertions before creation
    # This caused "local variable 'embeddings' referenced before assignment" errors
    embeddings = []
    missing_embeddings = []
    for header in headers:
        if header in cached_embeddings:
            embeddings.append(cached_embeddings[header])
        else:
            missing_embeddings.append(header)
    
    # Safety check - ensure we have embeddings for all sequences
    if missing_embeddings:
        print(f"  Error: Missing embeddings for {len(missing_embeddings)} sequences: {missing_embeddings[:3]}...")
        return None, None
    
    # Ensure we have the same number of embeddings as sequences
    assert len(embeddings) == len(sequences), f"Mismatch: {len(embeddings)} embeddings vs {len(sequences)} sequences"
    assert len(all_scores) == len(sequences), f"Mismatch: {len(all_scores)} scores vs {len(sequences)} sequences"
    
    print("  Progress: Done.")
    return np.array(embeddings), all_scores

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
        
        if not scores:
            # Fallback if no scores were computed
            final_k = min_k
            break
        
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
                  num_sequences, num_iterations):
    duration = end_time - start_time
    with open(log_path, 'w') as log_f:
        log_f.write("pLM-clust v2 Run Log\n===================\n\n")
        log_f.write(f"Run start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Run end:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Duration:  {duration}\n\n")
        log_f.write("Configuration:\n")
        log_f.write(f"  TARGET: {target}\n  cluster_number: {cluster_param}\n")
        if isinstance(cluster_param, str) and cluster_param.lower()=='auto':
            log_f.write(f"  silhouette_range: {silhouette_range}\n  final k: {final_k}\n  iterations: {num_iterations}\n")
        else:
            log_f.write(f"  final k (fixed): {final_k}\n")
        log_f.write(f"Sequences: {num_sequences}\n")
        log_f.write("Scoring: Single-pass NLL (no masking)\n\n")
        log_f.write("Inputs:\n")
        for f in input_files:
            log_f.write(f"  - {f}\n")
        log_f.write("\nOutputs:\n")
        for f in output_files:
            log_f.write(f"  - {f}\n")
        log_f.write("\nNotes:\n  - Embeddings: ESM2 t33_650M_UR50D\n")
        log_f.write("  - Scoring: Single-pass NLL (reusing embeddings)\n")

def process_single_fasta(fasta_path, target, cluster_param, silhouette_range, results_base_dir):
    """
    Process a single FASTA file independently.
    
    Args:
        fasta_path: Path to the FASTA file
        target: Target project name
        cluster_param: Cluster parameter (number or 'auto')
        silhouette_range: Range for silhouette analysis if auto
        results_base_dir: Base results directory
    
    Returns:
        dict with processing results
    """
    # Extract filename without extension for subdirectory naming
    fasta_name = os.path.basename(fasta_path)
    file_stem = os.path.splitext(fasta_name)[0]
    
    print(f"\nProcessing {fasta_name}...")
    
    # Create subdirectory for this file's results
    file_results_dir = os.path.join(results_base_dir, file_stem)
    os.makedirs(file_results_dir, exist_ok=True)
    
    # Load sequences from this file only
    headers, sequences = load_sequences(fasta_path)
    num_sequences = len(sequences)
    
    if num_sequences == 0:
        print(f"  Warning: No sequences found in {fasta_name}")
        return None
    
    # Skip files with too few sequences for meaningful clustering
    if num_sequences < 2:
        print(f"  Warning: Too few sequences ({num_sequences}) for clustering. Skipping {fasta_name}")
        return None
    
    # Calculate average sequence length and skip if too long
    avg_length = sum(len(seq) for seq in sequences) / num_sequences
    if avg_length > 1500:
        print(f"  Warning: Average sequence length ({avg_length:.1f} aa) > 1500 aa. Skipping {fasta_name}")
        return None
    
    print(f"  Loaded {num_sequences} sequences (avg length: {avg_length:.1f} aa)")
    
    # Use available device
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    
    # Compute embeddings and scores
    try:
        embeddings, scores = compute_embeddings_and_scores(headers, sequences, device=device)
        if embeddings is None or scores is None:
            print(f"  Error: compute_embeddings_and_scores returned None for {file_stem}")
            return None
    except Exception as e:
        print(f"  Error computing embeddings for {file_stem}: {e}")
        return None
    
    # Verify that we have valid embeddings and scores
    if embeddings is None or scores is None or len(embeddings) == 0 or len(scores) == 0:
        print(f"  Error: Invalid embeddings or scores returned for {file_stem}")
        return None
    
    # Ensure embeddings and scores match the number of sequences
    if len(embeddings) != num_sequences or len(scores) != num_sequences:
        print(f"  Error: Mismatch between sequences ({num_sequences}) and embeddings ({len(embeddings)}) or scores ({len(scores)}) for {file_stem}")
        return None
    
    # Determine optimal k
    if isinstance(cluster_param, str) and cluster_param.lower() == 'auto':
        min_k, max_k = map(int, silhouette_range)
        max_k = min(max_k, num_sequences - 1)
        if max_k < 2:
            print(f"  Warning: Too few sequences ({num_sequences}) for clustering. Using k=1")
            final_k = 1
            sil_csv = sil_png = None
            num_iters = 0
        else:
            best_k, sil_df, sil_csv, sil_png = perform_silhouette_search(
                embeddings, max(2, min_k), max_k, num_samples=10,
                results_dir=file_results_dir, target=file_stem)
            final_k = best_k
            num_iters = sil_df.iteration.max()
            print(f"  Auto-selected k: {final_k}")
    else:
        final_k = min(int(cluster_param), num_sequences - 1) if num_sequences > 1 else 1
        sil_csv = sil_png = None
        num_iters = 0
        print(f"  Using k: {final_k}")
    
    # Perform clustering (handle single sequence case)
    try:
        if num_sequences == 1 or final_k == 1:
            labels = [0] * num_sequences
        else:
            labels = cluster_embeddings(embeddings, final_k)
    except Exception as e:
        print(f"  Error during clustering for {file_stem}: {e}")
        return None
    
    # Convert to negative scores for consistency
    negative_scores = [-score for score in scores]
    
    # Find cluster representatives
    rep = {}
    for i, lbl in enumerate(labels):
        score = negative_scores[i]
        if lbl not in rep or score > rep[lbl]['metric']:
            rep[lbl] = {'header': headers[i], 'seq': sequences[i], 'metric': score}
    
    # Save representatives
    rep_fasta = os.path.join(file_results_dir, f"top_cluster_representatives_{file_stem}.fasta")
    with open(rep_fasta, 'w') as wf:
        for lbl in sorted(rep):
            wf.write(f"{rep[lbl]['header']} cluster={lbl}\n{rep[lbl]['seq']}\n")
    
    # Create results dataframe
    df = pd.DataFrame({
        'header': headers,
        'sequence': sequences,
        'cluster': labels,
        'nll_score': scores,
        'negative_nll': negative_scores
    })
    
    metrics_csv = os.path.join(file_results_dir, f"pLM-clustv2_sequences_with_metrics_{file_stem}.csv")
    df.to_csv(metrics_csv, index=False)
    
    # Create cluster files
    cluster_dir = os.path.join(file_results_dir, f"{final_k}_clusters_{file_stem}")
    os.makedirs(cluster_dir, exist_ok=True)
    cluster_paths = []
    for cid in set(labels):
        pth = os.path.join(cluster_dir, f"cluster_{cid}.fasta")
        with open(pth, 'w') as cf:
            for h, s, l in zip(headers, sequences, labels):
                if l == cid:
                    cf.write(f"{h}\n{s}\n")
        cluster_paths.append(pth)
    
    # Create t-SNE visualization (only if we have enough sequences)
    tsne_csv = tsne_png = None
    if num_sequences > 2:  # Need at least 3 sequences for meaningful clustering visualization
        try:
            # Ensure we have enough components for PCA
            max_components = min(50, num_sequences - 1, embeddings.shape[1])
            if max_components >= 2:
                data_2d = PCA(n_components=max_components).fit_transform(embeddings) if embeddings.shape[1] > max_components else embeddings
                if data_2d.shape[0] > 2:  # Need at least 3 points for t-SNE
                    # Adjust perplexity for small datasets
                    perplexity = min(30.0, (num_sequences - 1) / 3.0)
                    perplexity = max(1.0, perplexity)  # Ensure perplexity is at least 1
                    coords = TSNE(n_components=2, random_state=42, max_iter=1000, perplexity=perplexity).fit_transform(data_2d)
                    tsne_df = pd.DataFrame({
                        'header': headers,
                        'Dim1': coords[:, 0],
                        'Dim2': coords[:, 1],
                        'cluster': labels,
                        'nll_score': scores
                    })
                    tsne_csv = os.path.join(file_results_dir, f"tsne_coordinates_{file_stem}.csv")
                    tsne_df.to_csv(tsne_csv, index=False)
                    
                    plt.figure(figsize=(8, 6))
                    sns.scatterplot(data=tsne_df, x='Dim1', y='Dim2', hue='cluster', s=50)
                    plt.title(f't-SNE Clustering: {file_stem}')
                    plt.tight_layout()
                    tsne_png = os.path.join(file_results_dir, f"tsne_clusters_{file_stem}.png")
                    plt.savefig(tsne_png, dpi=300)
                    plt.close()
        except Exception as e:
            print(f"  Warning: Could not create t-SNE visualization for {file_stem}: {e}")
            tsne_csv = tsne_png = None
    
    # Prepare outputs list
    outputs = [rep_fasta, metrics_csv] + cluster_paths
    if tsne_csv:
        outputs.append(tsne_csv)
    if tsne_png:
        outputs.append(tsne_png)
    if sil_csv:
        outputs += [sil_csv, sil_png]
    
    print(f"  → Results saved to: {file_results_dir}")
    print(f"  → Sequences: {num_sequences}, Clusters: {final_k}")
    
    return {
        'fasta_name': fasta_name,
        'file_stem': file_stem,
        'results_dir': file_results_dir,
        'num_sequences': num_sequences,
        'final_k': final_k,
        'outputs': outputs,
        'rep_fasta': rep_fasta,
        'metrics_csv': metrics_csv,
        'tsne_csv': tsne_csv,
        'tsne_png': tsne_png,
        'sil_info': (sil_csv, sil_png, num_iters) if sil_csv else None
    }

def run(cfg):
    target = project_dir('plmclustv2', cfg)
    if not target:
        raise ValueError("Need project directory")
    cluster_param = cfg.get('plmclustv2_cluster_number', 10)
    silhouette_range = cfg.get('silhouette_range', [2,10])
    keep_separate = cfg.get('plmclustv2_keepseparate', False)
    start_time = datetime.datetime.now()
    fasta_paths = sorted(glob.glob(os.path.join('inputs','plmclustv2',target,'*.fasta')))
    
    if not fasta_paths:
        print(f"No FASTA files found in inputs/plmclustv2/{target}/")
        return
    
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"Using device: {device}")
    results_dir = os.path.join('results','plmclustv2',target)
    os.makedirs(results_dir, exist_ok=True)
    
    if keep_separate:
        print(f"Processing {len(fasta_paths)} FASTA files separately...")
        return run_separate_mode(fasta_paths, target, cluster_param, silhouette_range, results_dir, start_time)
    else:
        print(f"Processing {len(fasta_paths)} FASTA files in merged mode...")
        return run_merged_mode(fasta_paths, target, cluster_param, silhouette_range, results_dir, start_time, device)

def run_merged_mode(fasta_paths, target, cluster_param, silhouette_range, results_dir, start_time, device):
    """Original merged processing mode"""
    headers, sequences = [], []
    for fp in fasta_paths:
        hdrs, seqs = load_sequences(fp)
        headers.extend(hdrs)
        sequences.extend(seqs)
    num_sequences = len(sequences)
    
    # Compute embeddings and scores in one pass
    embeddings, scores = compute_embeddings_and_scores(headers, sequences, device=device)
    
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
    
    # Perform clustering
    labels = cluster_embeddings(embeddings, final_k)
    
    # Convert to negative scores for consistency with v1 (higher = better)
    negative_scores = [-score for score in scores]
    
    # Find cluster representatives based on scores
    rep = {}
    for i, lbl in enumerate(labels):
        score = negative_scores[i]
        if lbl not in rep or score > rep[lbl]['metric']:
            rep[lbl] = {'header': headers[i], 'seq': sequences[i], 'metric': score}
    
    rep_fasta = os.path.join(results_dir, f"top_cluster_representatives_{target}.fasta")
    with open(rep_fasta, 'w') as wf:
        for lbl in sorted(rep):
            wf.write(f"{rep[lbl]['header']} cluster={lbl}\n{rep[lbl]['seq']}\n")
    
    # Create results dataframe
    df = pd.DataFrame({
        'header': headers,
        'sequence': sequences,
        'cluster': labels,
        'nll_score': scores,
        'negative_nll': negative_scores
    })
    
    metrics_csv = os.path.join(results_dir, f"pLM-clustv2_sequences_with_metrics_{target}.csv")
    df.to_csv(metrics_csv, index=False)
    
    # Create cluster files
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
    
    # Create t-SNE visualization
    data_2d = PCA(n_components=50).fit_transform(embeddings) if embeddings.shape[1] > 50 else embeddings
    # Adjust perplexity for datasets
    perplexity = min(30.0, (num_sequences - 1) / 3.0)
    perplexity = max(1.0, perplexity)  # Ensure perplexity is at least 1
    coords = TSNE(n_components=2, random_state=42, max_iter=1000, perplexity=perplexity).fit_transform(data_2d)
    tsne_df = pd.DataFrame({
        'header': headers,
        'Dim1': coords[:, 0],
        'Dim2': coords[:, 1],
        'cluster': labels,
        'nll_score': scores
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
                  num_sequences, num_iters)
    print(f"Top representatives: {rep_fasta}")
    print(f"Metrics CSV: {metrics_csv}")
    print(f"t-SNE coords saved to: {tsne_csv}")
    print(f"t-SNE plot: {tsne_png}")

def run_separate_mode(fasta_paths, target, cluster_param, silhouette_range, results_dir, start_time):
    """Process each FASTA file separately"""
    all_results = []
    
    for i, fasta_path in enumerate(fasta_paths, 1):
        print(f"\n--- Processing file {i}/{len(fasta_paths)} ---")
        result = process_single_fasta(
            fasta_path, target, cluster_param, silhouette_range, results_dir
        )
        if result:
            all_results.append(result)
    
    # Create a summary log for all files
    end_time = datetime.datetime.now()
    summary_log_path = os.path.join(results_dir, f"summary_log_{target}.txt")
    
    with open(summary_log_path, 'w') as log_f:
        log_f.write("pLM-clust v2 Separate Mode Summary\n")
        log_f.write("===================================\n\n")
        log_f.write(f"Run start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Run end:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Duration:  {end_time - start_time}\n\n")
        log_f.write("Configuration:\n")
        log_f.write(f"  TARGET: {target}\n")
        log_f.write(f"  Mode: Keep Separate\n")
        log_f.write(f"  cluster_number: {cluster_param}\n")
        if isinstance(cluster_param, str) and cluster_param.lower() == 'auto':
            log_f.write(f"  silhouette_range: {silhouette_range}\n")
        log_f.write(f"  Total files processed: {len(all_results)}\n\n")
        
        total_sequences = sum(r['num_sequences'] for r in all_results)
        log_f.write(f"Total sequences across all files: {total_sequences}\n\n")
        
        log_f.write("File-by-file results:\n")
        for result in all_results:
            log_f.write(f"\n  File: {result['fasta_name']}\n")
            log_f.write(f"    Sequences: {result['num_sequences']}\n")
            log_f.write(f"    Clusters: {result['final_k']}\n")
            log_f.write(f"    Results directory: {result['results_dir']}\n")
            if result['sil_info']:
                sil_csv, sil_png, num_iters = result['sil_info']
                log_f.write(f"    Silhouette iterations: {num_iters}\n")
        
        log_f.write(f"\nAll results saved under: {results_dir}\n")
        log_f.write("Each file has its own subdirectory with complete analysis.\n")
    
    print(f"\n=== SUMMARY ===")
    print(f"Processed {len(all_results)} files successfully")
    print(f"Total sequences: {sum(r['num_sequences'] for r in all_results)}")
    print(f"Summary log: {summary_log_path}")
    print(f"Results directory: {results_dir}")
    
    return {
        'mode': 'separate',
        'files_processed': len(all_results),
        'total_sequences': sum(r['num_sequences'] for r in all_results),
        'results': all_results,
        'summary_log': summary_log_path,
        'results_dir': results_dir
    } 