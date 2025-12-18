#!/usr/bin/env python3
"""
UHT Discovery - Gradio GUI
Interactive web interface for BLASTER, TRIM, and PLMCLUSTV2 workflows
"""

import os
import json
import datetime
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import yaml
from Bio import SeqIO

# Import from uht_discovery.core subpackage
from uht_discovery.core.BLASTer import run as blaster_run
from uht_discovery.core.trim import run as trim_run, run_histogram_only as trim_histogram_only
from uht_discovery.core.plmclustv2 import run as plmclustv2_run
from uht_discovery.core.common import project_dir

# Global state for progress tracking
progress_state = {"current": 0, "total": 100, "message": ""}

def save_input_parameters(workflow: str, params: dict, results_dir: str):
    """Save input parameters to a JSON file in results directory"""
    # Ensure results_dir is a directory path, not a file
    if os.path.isfile(results_dir):
        results_dir = os.path.dirname(results_dir)
    
    # Ensure directory exists
    os.makedirs(results_dir, exist_ok=True)
    
    params_file = os.path.join(results_dir, f"input_parameters_{workflow}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(params_file, 'w') as f:
        json.dump({
            "workflow": workflow,
            "timestamp": datetime.datetime.now().isoformat(),
            "parameters": params
        }, f, indent=2)
    return params_file

def update_progress(current: int, total: int, message: str):
    """Update progress state"""
    progress_state["current"] = current
    progress_state["total"] = total
    progress_state["message"] = message
    return f"Progress: {current}/{total} - {message}"

def run_blaster_workflow(
    project_name: str,
    fasta_files: List[str],
    num_hits: int,
    blast_db: str,
    evalue: float,
    email: str,
    api_key: Optional[str],
    progress=gr.Progress()
) -> Tuple[str, str, str]:
    """Run BLASTER workflow with detailed progress updates"""
    try:
        progress(0, desc="Initializing BLASTER workflow...")
        
        # Create temporary config
        cfg = {
            "blaster_project_directory": project_name,
            "blaster_num_hits": num_hits,
            "blaster_blast_db": blast_db,
            "blaster_evalue": evalue,
            "blaster_email": email,
        }
        if api_key:
            cfg["blaster_api_key"] = api_key
        
        # Create input directory and copy files
        input_dir = Path("inputs") / "blaster" / project_name
        input_dir.mkdir(parents=True, exist_ok=True)
        
        progress(0.05, desc="Preparing input files...")
        for i, file_path in enumerate(fasta_files):
            if file_path:
                shutil.copy(file_path, input_dir / os.path.basename(file_path))
        
        # Test NCBI connection
        progress(0.1, desc="Testing connection to NCBI servers...")
        try:
            from Bio.Blast import NCBIWWW
            from Bio import Entrez
            Entrez.email = email
            if api_key:
                Entrez.api_key = api_key
            # Quick connection test
            test_handle = Entrez.efetch(db="protein", id="NP_000509.1", rettype="fasta", retmode="text")
            test_handle.read()
            test_handle.close()
            progress(0.15, desc="Connection to NCBI established successfully")
        except Exception as e:
            progress(0.15, desc=f"Warning: Connection test failed - {str(e)[:50]}... (will attempt BLAST anyway)")
        
        # Run BLASTER with progress updates
        progress(0.2, desc="Loading query sequences...")
        
        # Import BLASTER functions to monitor progress
        from uht_discovery.core.BLASTer import load_query_sequences, run_blastp, parse_blast_xml, fetch_sequences_from_accessions, write_combined_fasta, write_blast_report
        import datetime as dt
        
        query_records, fasta_paths = load_query_sequences(project_name)
        num_queries = len(query_records)
        progress(0.25, desc=f"Loaded {num_queries} query sequences. Starting BLAST searches...")
        
        # Run BLAST searches with progress updates
        hits_by_query = {}
        seen = set()
        ordered_accessions = []
        
        for i, rec in enumerate(query_records):
            progress(0.25 + (i / num_queries) * 0.5, desc=f"BLASTing query {i+1}/{num_queries}: {rec.id} - Submitting to NCBI...")
            try:
                xml_handle = run_blastp(str(rec.seq), blast_db, evalue, num_hits)
                progress(0.25 + (i / num_queries) * 0.5 + 0.01, desc=f"BLASTing query {i+1}/{num_queries}: {rec.id} - Request submitted, waiting for results...")
                hits = parse_blast_xml(xml_handle, num_hits)
                hits_by_query[rec.id] = hits
                progress(0.25 + (i / num_queries) * 0.5 + 0.02, desc=f"BLASTing query {i+1}/{num_queries}: {rec.id} - Found {len(hits)} hits")
                for h in hits:
                    if h['accession'] not in seen:
                        seen.add(h['accession'])
                        ordered_accessions.append(h['accession'])
            except Exception as e:
                progress(0.25 + (i / num_queries) * 0.5, desc=f"BLASTing query {i+1}/{num_queries}: {rec.id} - Error: {str(e)[:50]}")
                hits_by_query[rec.id] = []
        
        # Fetch sequences
        progress(0.75, desc=f"Fetching {len(ordered_accessions)} unique sequences from NCBI...")
        try:
            hit_records = fetch_sequences_from_accessions(ordered_accessions, email, api_key)
            progress(0.85, desc=f"Successfully fetched {len(hit_records)} sequences")
        except Exception as e:
            progress(0.85, desc=f"Error fetching sequences: {str(e)[:50]}")
            hit_records = []
        
        # Write outputs
        progress(0.9, desc="Writing output files...")
        results_dir = Path("results") / "blaster" / project_name
        results_dir.mkdir(parents=True, exist_ok=True)
        
        fasta_out = results_dir / f"combined_hits_{project_name}.fasta"
        write_combined_fasta(query_records, hit_records, str(fasta_out))
        
        end_time = dt.datetime.now()
        start_time = dt.datetime.now() - dt.timedelta(seconds=1)  # Approximate
        report_out = results_dir / f"blast_report_{project_name}.txt"
        write_blast_report(
            str(report_out), start_time, end_time,
            cfg, [str(f) for f in fasta_paths], num_queries,
            ordered_accessions, hits_by_query
        )
        
        # Save input parameters
        params = {
            "project_name": project_name,
            "num_hits": num_hits,
            "blast_db": blast_db,
            "evalue": evalue,
            "email": email,
            "input_files": [os.path.basename(f) for f in fasta_files if f]
        }
        save_input_parameters("blaster", params, str(results_dir))
        
        progress(1.0, desc="BLASTER workflow completed successfully!")
        
        # Read report
        report_text = ""
        if report_out.exists():
            with open(report_out, 'r') as f:
                report_text = f.read()
        
        return (
            str(fasta_out) if fasta_out.exists() else "No output file generated",
            str(report_out) if report_out.exists() else "No report generated",
            report_text
        )
    except Exception as e:
        error_msg = f"Error in BLASTER workflow: {str(e)}"
        import traceback
        traceback.print_exc()
        return error_msg, "", error_msg

def generate_trim_histogram(project_name: str, fasta_files) -> go.Figure:
    """Generate length distribution histogram when files are uploaded"""
    try:
        # Handle different input formats from Gradio
        if not project_name:
            return None
        
        # Convert to list if needed
        if fasta_files is None:
            return None
        
        if not isinstance(fasta_files, list):
            fasta_files = [fasta_files]
        
        # Filter out None/empty values
        fasta_files = [f for f in fasta_files if f]
        
        if not fasta_files:
            return None
        
        # Create input directory and copy files
        input_dir = Path("inputs") / "trim" / project_name
        input_dir.mkdir(parents=True, exist_ok=True)
        
        # Clear existing files first to avoid conflicts
        for existing_file in input_dir.glob("*.fasta"):
            existing_file.unlink()
        
        # Copy files
        for file_path in fasta_files:
            if file_path:
                # Handle both string paths and file objects
                if isinstance(file_path, str):
                    src_path = file_path
                elif isinstance(file_path, dict):
                    # Gradio file component sometimes returns a dict
                    src_path = file_path.get('name', '') or file_path.get('path', '')
                else:
                    src_path = file_path.name if hasattr(file_path, 'name') else str(file_path)
                
                # Skip if path is empty or doesn't exist
                if not src_path or not os.path.exists(src_path):
                    continue
                
                # Copy the file
                try:
                    shutil.copy(src_path, input_dir / os.path.basename(src_path))
                except Exception as e:
                    print(f"Warning: Could not copy {src_path}: {e}")
                    continue
        
        # Load sequences and create histogram
        from uht_discovery.core.trim import load_fasta_sequences
        fasta_paths = sorted(input_dir.glob("*.fasta"))
        if not fasta_paths:
            return None
        
        records = load_fasta_sequences(fasta_paths[0])
        lengths = [len(rec.seq) for rec in records]
        
        if not lengths:
            return None
        
        first_len = lengths[0]
        n = len(lengths)  # Number of sequences
        n_bins = max(10, n // 5)  # n/5 bins, minimum 10
        
        # Calculate bin edges manually to ensure exact number of bins
        min_len = min(lengths)
        max_len = max(lengths)
        bin_width = (max_len - min_len) / n_bins if n_bins > 0 else 1
        bin_edges = [min_len + i * bin_width for i in range(n_bins + 1)]
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=lengths,
            xbins=dict(start=min_len, end=max_len, size=bin_width),
            name="Sequence Lengths",
            marker_color='#636EFA',  # Gradio theme color
            opacity=0.8,
            marker_line_color='white',
            marker_line_width=1
        ))
        fig.add_vline(
            x=first_len,
            line_dash="dash",
            line_color="#EF553B",
            annotation_text=f"First seq: {first_len}",
            annotation_position="top"
        )
        fig.update_layout(
            title=f"Length Distribution: {fasta_paths[0].name} ({n} sequences, {n_bins} bins)",
            xaxis_title="Sequence Length",
            yaxis_title="Count",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1f2937'),
            xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
        )
        return fig
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None

def run_trim_workflow(
    project_name: str,
    fasta_files: List[str],
    auto_mode: bool,
    low_threshold: Optional[int],
    high_threshold: Optional[int],
    progress=gr.Progress()
) -> Tuple[str, str, str]:
    """Run TRIM workflow (trimming only, histogram already shown)"""
    try:
        progress(0, desc="Setting up TRIM...")
        
        # Create input directory and copy files (if not already done)
        input_dir = Path("inputs") / "trim" / project_name
        input_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure files are copied
        for file_path in fasta_files:
            if file_path:
                dest = input_dir / os.path.basename(file_path)
                if not dest.exists():
                    shutil.copy(file_path, dest)
        
        # Create config
        cfg = {
            "trim_project_directory": project_name,
            "mode": "web",
            "auto_mode": auto_mode,
        }
        if not auto_mode:
            cfg["trim_low"] = low_threshold
            cfg["trim_high"] = high_threshold
        
        # Run trim
        progress(0.3, desc="Running trim...")
        result = trim_run(cfg)
        
        trimmed_fasta = ""
        qc_report = ""
        if result:
            results_dir = Path("results") / "trim" / project_name
            if isinstance(result, dict):
                trimmed_fasta = result.get("out_fasta", "")
                qc_report = result.get("report_txt", "")
            elif isinstance(result, list) and result:
                trimmed_fasta = result[0].get("out_fasta", "")
                qc_report = result[0].get("report_txt", "")
        
        # Save input parameters
        results_dir = Path("results") / "trim" / project_name
        params = {
            "project_name": project_name,
            "auto_mode": auto_mode,
            "low_threshold": low_threshold,
            "high_threshold": high_threshold,
            "input_files": [os.path.basename(f) for f in fasta_files if f]
        }
        save_input_parameters("trim", params, str(results_dir))
        
        progress(1.0, desc="Complete!")
        
        # Read QC report
        report_text = ""
        if qc_report and os.path.exists(qc_report):
            with open(qc_report, 'r') as f:
                report_text = f.read()
        
        return (
            str(trimmed_fasta) if trimmed_fasta and os.path.exists(trimmed_fasta) else "",
            str(qc_report) if qc_report and os.path.exists(qc_report) else "",
            report_text
        )
    except Exception as e:
        error_msg = f"Error in TRIM workflow: {str(e)}"
        import traceback
        traceback.print_exc()
        return error_msg, "", error_msg

def compute_embeddings_with_progress(headers, sequences, device='cpu', batch_size=1, progress_callback=None, start_progress=0.0, end_progress=0.8):
    """Wrapper around compute_embeddings_and_scores with progress tracking"""
    import time
    import torch
    import esm
    from uht_discovery.core.plmclustv2 import EmbeddingCache
    
    start_time = time.time()
    embedding_cache = EmbeddingCache()
    
    # Check cache - get both embeddings and scores
    if progress_callback:
        progress_callback(start_progress, desc="Checking embedding cache...")
    
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
    
    cached_count = len(cached_embeddings)
    missing_count = len(missing_sequences)
    total = len(sequences)
    
    # Initialize scores list with cached values
    all_scores = [0.0] * len(sequences)
    for i, header in enumerate(headers):
        if header in cached_scores:
            all_scores[i] = cached_scores[header]
    
    # Compute new embeddings and scores in one pass
    if missing_sequences:
        if progress_callback:
            progress_callback(start_progress + 0.1, desc=f"Computing {missing_count} new embeddings and scores ({cached_count} cached)...")
        
        model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
        model.eval().to(device)
        batch_converter = alphabet.get_batch_converter()
        pad_idx = batch_converter.alphabet.padding_idx
        
        new_embeddings = []
        new_scores = []
        
        for i in range(0, len(missing_sequences), batch_size):
            batch_end = min(i + batch_size, len(missing_sequences))
            batch = list(zip(missing_headers[i:batch_end], missing_sequences[i:batch_end]))
            
            if progress_callback:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                remaining = (missing_count - i) / rate if rate > 0 else 0
                progress_pct = start_progress + 0.1 + (i / missing_count) * (end_progress - start_progress - 0.1) if missing_count > 0 else start_progress + 0.1
                desc = f"Computing embeddings and scores: {i+1}/{missing_count} (est. {remaining:.0f}s remaining)"
                progress_callback(progress_pct, desc=desc)
            
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
            
            del out, reps, lps, tp, tokens
            if device == 'mps':
                torch.mps.empty_cache()
        
        # Store new embeddings and scores in cache together
        for header, embedding, score in zip(missing_headers, new_embeddings, new_scores):
            sequence = sequences[headers.index(header)]
            embedding_cache.store_embedding_and_score(sequence, embedding, score)
            cached_embeddings[header] = embedding
            idx = headers.index(header)
            all_scores[idx] = score
    
    # Build final embeddings array in correct order
    embeddings = []
    for header in headers:
        if header in cached_embeddings:
            embeddings.append(cached_embeddings[header])
        else:
            # This shouldn't happen, but handle it gracefully
            raise ValueError(f"Missing embedding for header: {header}")
    
    if progress_callback:
        progress_callback(end_progress, desc="Embeddings and scores computation complete!")
    
    return np.array(embeddings), all_scores

def run_plmclustv2_workflow(
    project_name: str,
    fasta_files: List[str],
    auto_clusters: bool,
    cluster_number: Optional[int],
    silhouette_range_min: int,
    silhouette_range_max: int,
    progress=gr.Progress()
) -> Tuple[str, str, str, str, str]:
    """Run PLMCLUSTV2 workflow with interactive t-SNE/UMAP visualization"""
    try:
        import time
        import torch
        from sklearn.cluster import KMeans
        from sklearn.decomposition import PCA
        from sklearn.manifold import TSNE
        from umap import UMAP
        from uht_discovery.core.plmclustv2 import load_sequences, cluster_embeddings, perform_silhouette_search
        
        progress(0, desc="Setting up PLMCLUSTV2...")
        
        # Create input directory and copy files
        input_dir = Path("inputs") / "plmclustv2" / project_name
        input_dir.mkdir(parents=True, exist_ok=True)
        
        progress(0.02, desc="Copying input files...")
        for i, file_path in enumerate(fasta_files):
            if file_path:
                # Handle both file objects and string paths
                if isinstance(file_path, str):
                    src_path = file_path
                elif hasattr(file_path, 'name'):
                    src_path = file_path.name
                else:
                    src_path = str(file_path)
                
                # Only copy if it's actually a file
                if os.path.isfile(src_path):
                    shutil.copy(src_path, input_dir / os.path.basename(src_path))
                elif os.path.isdir(src_path):
                    # Skip directories
                    continue
        
        # Load sequences
        progress(0.05, desc="Loading sequences...")
        fasta_paths = sorted(input_dir.glob("*.fasta"))
        headers, sequences = [], []
        for fp in fasta_paths:
            hdrs, seqs = load_sequences(str(fp))
            headers.extend(hdrs)
            sequences.extend(seqs)
        
        num_sequences = len(sequences)
        progress(0.08, desc=f"Loaded {num_sequences} sequences. Computing embeddings and scores...")
        
        # Compute embeddings with progress tracking
        device = 'mps' if torch.backends.mps.is_available() else 'cpu'
        embeddings, scores = compute_embeddings_with_progress(
            headers, sequences, device=device, batch_size=1,
            progress_callback=lambda p, desc: progress(p, desc=desc),
            start_progress=0.08, end_progress=0.75
        )
        
        if embeddings is None or scores is None:
            return "", "", None, None, "Error: Failed to compute embeddings"
        
        # Determine cluster number
        if auto_clusters:
            progress(0.75, desc="Finding optimal number of clusters (silhouette search)...")
            results_dir = Path("results") / "plmclustv2" / project_name
            results_dir.mkdir(parents=True, exist_ok=True)
            final_k, _, _, _ = perform_silhouette_search(
                embeddings, silhouette_range_min, silhouette_range_max, num_samples=10,
                results_dir=str(results_dir), target=project_name
            )
        else:
            final_k = cluster_number if cluster_number else 5
        
        progress(0.85, desc=f"Clustering into {final_k} clusters...")
        labels = cluster_embeddings(embeddings, final_k)
        
        # Create dataframes
        df = pd.DataFrame({
            'header': headers,
            'sequence': sequences,
            'cluster': labels,
            'nll_score': scores
        })
        
        # Calculate rankings (lower NLL is better)
        df['rank'] = df['nll_score'].rank(method='min').astype(int)
        df['rank_text'] = df.apply(lambda row: f"{int(row['rank'])}{'st' if int(row['rank']) % 10 == 1 and int(row['rank']) % 100 != 11 else 'nd' if int(row['rank']) % 10 == 2 and int(row['rank']) % 100 != 12 else 'rd' if int(row['rank']) % 10 == 3 and int(row['rank']) % 100 != 13 else 'th'} out of {len(df)}", axis=1)
        
        # Save metrics CSV
        results_dir = Path("results") / "plmclustv2" / project_name
        results_dir.mkdir(parents=True, exist_ok=True)
        metrics_csv = results_dir / f"pLM-clustv2_sequences_with_metrics_{project_name}.csv"
        df.to_csv(metrics_csv, index=False)
        
        # Find cluster representatives (winners) - best NLL score per cluster
        # Lower NLL is better, so we find the minimum NLL per cluster
        progress(0.86, desc="Finding cluster representatives...")
        rep = {}
        for i, (header, seq, lbl, score) in enumerate(zip(headers, sequences, labels, scores)):
            if lbl not in rep or score < rep[lbl]['score']:
                rep[lbl] = {'header': header, 'seq': seq, 'score': score}
        
        # Save winner FASTA file
        rep_fasta = results_dir / f"top_cluster_representatives_{project_name}.fasta"
        with open(rep_fasta, 'w') as wf:
            for lbl in sorted(rep):
                wf.write(f"{rep[lbl]['header']} cluster={lbl}\n{rep[lbl]['seq']}\n")
        
        # Create per-cluster FASTA files folder
        progress(0.87, desc="Creating per-cluster FASTA files...")
        cluster_dir = results_dir / f"{final_k}_clusters_{project_name}"
        cluster_dir.mkdir(exist_ok=True)
        cluster_fasta_files = []
        for cid in sorted(set(labels)):
            cluster_fasta = cluster_dir / f"cluster_{cid}.fasta"
            with open(cluster_fasta, 'w') as cf:
                for h, s, l in zip(headers, sequences, labels):
                    if l == cid:
                        cf.write(f"{h}\n{s}\n")
            cluster_fasta_files.append(str(cluster_fasta))
        
        # Create a zip file of the cluster folder for easy download
        import zipfile
        cluster_zip = results_dir / f"{final_k}_clusters_{project_name}.zip"
        with zipfile.ZipFile(cluster_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for cluster_fasta in cluster_fasta_files:
                if os.path.exists(cluster_fasta):
                    zipf.write(cluster_fasta, os.path.basename(cluster_fasta))
        
        # Create t-SNE
        progress(0.88, desc="Computing t-SNE coordinates...")
        data_2d = PCA(n_components=50).fit_transform(embeddings) if embeddings.shape[1] > 50 else embeddings
        perplexity = min(30.0, (num_sequences - 1) / 3.0)
        perplexity = max(1.0, perplexity)
        tsne_coords = TSNE(n_components=2, random_state=42, max_iter=1000, perplexity=perplexity).fit_transform(data_2d)
        
        # Mark cluster winners in the dataframe
        winner_headers = {rep[lbl]['header'] for lbl in rep}
        df['is_winner'] = df['header'].isin(winner_headers)
        
        df_tsne = df.copy()
        df_tsne['Dim1'] = tsne_coords[:, 0]
        df_tsne['Dim2'] = tsne_coords[:, 1]
        
        tsne_csv = results_dir / f"tsne_coordinates_{project_name}.csv"
        df_tsne.to_csv(tsne_csv, index=False)
        
        # Create UMAP
        progress(0.92, desc="Computing UMAP coordinates...")
        reducer = UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1)
        umap_coords = reducer.fit_transform(embeddings)
        
        df_umap = df.copy()
        df_umap['Dim1'] = umap_coords[:, 0]
        df_umap['Dim2'] = umap_coords[:, 1]
        
        # Save UMAP coordinates
        umap_csv = results_dir / f"umap_coordinates_{project_name}.csv"
        df_umap.to_csv(umap_csv, index=False)
        
        # Create visualizations
        progress(0.95, desc="Creating visualizations...")
        
        def create_plot(df_plot, title, color_by='cluster'):
            # Reset index to ensure proper alignment between plot and customdata
            df_plot = df_plot.copy().reset_index(drop=True)
            
            # Create a mapping from (Dim1, Dim2) coordinates to dataframe row
            # This ensures we can match plot points back to dataframe rows
            coord_to_idx = {}
            for idx, row in df_plot.iterrows():
                coord_to_idx[(row['Dim1'], row['Dim2'])] = idx
            
            if color_by == 'cluster':
                # Convert cluster to string to ensure discrete coloring
                df_plot['cluster_str'] = df_plot['cluster'].astype(str)
                fig = px.scatter(
                    df_plot,
                    x='Dim1',
                    y='Dim2',
                    color='cluster_str',  # Use string to force discrete
                    hover_data={},  # Don't use hover_data, we'll set customdata manually
                    title=title,
                    labels={'Dim1': 'Dimension 1', 'Dim2': 'Dimension 2', 'cluster_str': 'Cluster'},
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                hover_template = '<b>%{hovertext}</b><br>' + \
                               'Dim1: %{x:.2f}<br>' + \
                               'Dim2: %{y:.2f}<br>' + \
                               'Cluster: %{customdata[2]}<br>' + \
                               'NLL Score: %{customdata[0]:.4f}<br>' + \
                               'Rank: %{customdata[1]}<br>' + \
                               '%{customdata[3]}<extra></extra>'
            else:  # color by NLL
                fig = px.scatter(
                    df_plot,
                    x='Dim1',
                    y='Dim2',
                    color='nll_score',
                    hover_data={},  # Don't use hover_data, we'll set customdata manually
                    title=title + " (colored by NLL)",
                    labels={'Dim1': 'Dimension 1', 'Dim2': 'Dimension 2', 'nll_score': 'NLL Score'},
                    color_continuous_scale='Viridis'
                )
                hover_template = '<b>%{hovertext}</b><br>' + \
                               'Dim1: %{x:.2f}<br>' + \
                               'Dim2: %{y:.2f}<br>' + \
                               'NLL Score: %{customdata[0]:.4f}<br>' + \
                               'Cluster: %{customdata[2]}<br>' + \
                               'Rank: %{customdata[1]}<br>' + \
                               '%{customdata[3]}<extra></extra>'
            
            # Set customdata per trace to ensure proper alignment
            # When using discrete colors, Plotly creates separate traces per color group
            for trace in fig.data:
                # Get the x and y coordinates for this trace
                x_coords = trace.x
                y_coords = trace.y
                
                # Build customdata array matching the order of points in this trace
                trace_customdata = []
                trace_hovertext = []
                
                for x, y in zip(x_coords, y_coords):
                    # Find the corresponding dataframe row
                    idx = coord_to_idx.get((x, y), None)
                    if idx is not None:
                        row = df_plot.iloc[idx]
                        # Order: [nll_score, rank_text, cluster, winner_message]
                        winner_msg = 'This protein is a cluster winner' if row.get('is_winner', False) else ''
                        trace_customdata.append([row['nll_score'], row['rank_text'], row['cluster'], winner_msg])
                        trace_hovertext.append(row['header'])
                    else:
                        # Fallback if coordinate not found
                        trace_customdata.append([0.0, 'N/A', 0, ''])
                        trace_hovertext.append('Unknown')
                
                # Update this trace with the correct customdata
                trace.customdata = trace_customdata
                trace.hovertemplate = hover_template
                trace.hovertext = trace_hovertext
                # Update marker size and opacity, preserving colorbar
                if hasattr(trace, 'marker'):
                    if trace.marker is None:
                        trace.marker = dict(size=6, opacity=0.7, line=dict(width=0.5, color='white'))
                    else:
                        # Use update_traces to preserve colorbar
                        pass  # We'll update via update_traces after the loop
                else:
                    trace.marker = dict(size=6, opacity=0.7, line=dict(width=0.5, color='white'))
            
            # Update marker properties - use stars for winners, dots for others
            # First, identify winners and non-winners
            winner_indices = df_plot[df_plot.get('is_winner', False)].index.tolist() if 'is_winner' in df_plot.columns else []
            
            # Update all traces with base properties
            fig.update_traces(
                marker_size=6,
                marker_opacity=0.7,
                marker_line_width=0.5,
                marker_line_color='white',
                selector=dict(type='scatter')
            )
            
            # For each trace, update markers to stars for winners
            # We need to check which points in each trace are winners
            for trace_idx, trace in enumerate(fig.data):
                # Get the indices of points in this trace that are winners
                trace_winner_mask = []
                for i, (x, y) in enumerate(zip(trace.x, trace.y)):
                    idx = coord_to_idx.get((x, y), None)
                    if idx is not None and idx in winner_indices:
                        trace_winner_mask.append(True)
                    else:
                        trace_winner_mask.append(False)
                
                # Create marker symbol array: 'star' for winners, 'circle' for others
                if any(trace_winner_mask):
                    marker_symbols = ['star' if is_winner else 'circle' for is_winner in trace_winner_mask]
                    # Update marker size for stars (make them slightly larger)
                    marker_sizes = [10 if is_winner else 6 for is_winner in trace_winner_mask]
                    trace.marker.symbol = marker_symbols
                    trace.marker.size = marker_sizes
            
            # Set transparent hover background via layout with light text for dark background
            layout_dict = {
                'height': 700,  # Taller for full-width display
                'width': None,  # Full width
                'showlegend': True,
                'hovermode': 'closest',
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'font': dict(color='#ffffff', size=12),  # White text for dark background
                'title_font': dict(color='#ffffff', size=16),
                'xaxis': dict(
                    gridcolor='rgba(255,255,255,0.2)',
                    title_font=dict(color='#ffffff'),
                    tickfont=dict(color='#ffffff')
                ),
                'yaxis': dict(
                    gridcolor='rgba(255,255,255,0.2)',
                    title_font=dict(color='#ffffff'),
                    tickfont=dict(color='#ffffff')
                ),
                'legend': dict(
                    font=dict(color='#ffffff'),
                    bgcolor='rgba(0,0,0,0.5)',
                    bordercolor='rgba(255,255,255,0.3)',
                    x=1,  # Right side
                    y=0,  # Bottom
                    xanchor='right',
                    yanchor='bottom'
                ),
                'hoverlabel': dict(
                    bgcolor='rgba(255,255,255,0.85)',
                    bordercolor='rgba(0,0,0,0.3)',
                    font_size=12,
                    font_color='#000000'  # Dark text on light hover background
                )
            }
            
            fig.update_layout(**layout_dict)
            
            # Add colorbar configuration for NLL coloring
            # For Plotly Express continuous color scales, the colorbar is automatically created
            # We need to update it via the layout's coloraxis_colorbar
            if color_by == 'nll_score':
                # Update colorbar styling - Plotly Express automatically creates coloraxis
                fig.update_layout(
                    coloraxis_colorbar=dict(
                        title=dict(text='NLL Score', font=dict(color='#ffffff')),
                        tickfont=dict(color='#ffffff'),
                        bgcolor='rgba(0,0,0,0.7)',
                        bordercolor='rgba(255,255,255,0.3)',
                        borderwidth=1
                    )
                )
            return fig
        
        # Save input parameters
        # Handle file paths properly (could be file objects or strings)
        file_names = []
        for f in fasta_files:
            if f:
                if isinstance(f, str):
                    file_names.append(os.path.basename(f))
                elif hasattr(f, 'name'):
                    file_names.append(os.path.basename(f.name))
                else:
                    file_names.append(str(f))
        
        params = {
            "project_name": project_name,
            "auto_clusters": auto_clusters,
            "cluster_number": cluster_number,
            "silhouette_range": [silhouette_range_min, silhouette_range_max],
            "final_k": final_k,
            "input_files": file_names
        }
        save_input_parameters("plmclustv2", params, str(results_dir))
        
        progress(1.0, desc="Complete!")
        
        return (
            str(metrics_csv) if metrics_csv.exists() else "",
            str(tsne_csv) if tsne_csv.exists() else "",
            str(rep_fasta) if rep_fasta.exists() else "",
            str(cluster_zip) if cluster_zip.exists() else "",
            f"Results saved to: {results_dir}. Use buttons above to view visualizations."
        )
    except Exception as e:
        error_msg = f"Error in PLMCLUSTV2 workflow: {str(e)}"
        import traceback
        traceback.print_exc()
        return "", "", "", "", error_msg

def create_umap_visualization(tsne_csv_path: str, project_name: str) -> go.Figure:
    """Create UMAP visualization - requires recomputing from embeddings"""
    try:
        from umap import UMAP
        import torch
        import esm
        from uht_discovery.core.plmclustv2 import load_sequences, compute_embeddings_and_scores
        
        # Load the sequences to recompute embeddings
        results_dir = Path("results") / "plmclustv2" / project_name
        input_dir = Path("inputs") / "plmclustv2" / project_name
        
        # Find FASTA files
        fasta_paths = sorted(input_dir.glob("*.fasta"))
        if not fasta_paths:
            return None
        
        # Load sequences
        headers, sequences = [], []
        for fp in fasta_paths:
            hdrs, seqs = load_sequences(str(fp))
            headers.extend(hdrs)
            sequences.extend(seqs)
        
        # Compute embeddings
        device = 'mps' if torch.backends.mps.is_available() else 'cpu'
        embeddings, scores = compute_embeddings_and_scores(headers, sequences, device=device)
        
        if embeddings is None:
            return None
        
        # Create UMAP
        reducer = UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1)
        coords_2d = reducer.fit_transform(embeddings)
        
        # Load cluster labels from CSV
        df = pd.read_csv(tsne_csv_path)
        
        df_umap = df.copy()
        df_umap['UMAP1'] = coords_2d[:, 0]
        df_umap['UMAP2'] = coords_2d[:, 1]
        
        fig = px.scatter(
            df_umap,
            x='UMAP1',
            y='UMAP2',
            color='cluster',
            hover_data=['header', 'nll_score'],
            title='UMAP Clustering Visualization',
            labels={'UMAP1': 'UMAP Dimension 1', 'UMAP2': 'UMAP Dimension 2'},
            color_continuous_scale='Viridis'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>' +
                        'UMAP1: %{x:.2f}<br>' +
                        'UMAP2: %{y:.2f}<br>' +
                        'Cluster: %{marker.color}<br>' +
                        'NLL Score: %{customdata[1]:.4f}<extra></extra>',
            hovertext=df_umap['header'],
            customdata=df_umap[['header', 'nll_score']].values
        )
        
        fig.update_layout(height=600, showlegend=True, hovermode='closest')
        
        return fig
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None

# Create Gradio interface
def create_interface():
    """Create the main Gradio interface"""
    
    with gr.Blocks(theme=gr.themes.Soft(), title="UHT Discovery") as app:
        gr.Markdown(
            """
            # UHT Discovery Pipeline
            Interactive workflow for protein sequence analysis: BLASTER → TRIM → PLMCLUSTV2
            """
        )
        
        with gr.Tabs(selected=0) as tabs:
            # BLASTER Tab
            with gr.Tab("BLASTER", id=0):
                gr.Markdown("### BLAST Sequence Search")
                with gr.Row():
                    with gr.Column():
                        blaster_project = gr.Textbox(
                            label="Project Name",
                            placeholder="e.g., my_project",
                            value=""
                        )
                        blaster_files = gr.File(
                            label="Input FASTA Files",
                            file_count="multiple",
                            file_types=[".fasta", ".fa"]
                        )
                        blaster_num_hits = gr.Number(
                            label="Number of Hits",
                            value=100,
                            minimum=1,
                            maximum=1000
                        )
                        blaster_db = gr.Dropdown(
                            label="BLAST Database",
                            choices=["nr", "swissprot", "refseq_protein"],
                            value="nr"
                        )
                        blaster_evalue = gr.Number(
                            label="E-value Cutoff",
                            value=1e-5,
                            minimum=1e-10,
                            maximum=1.0
                        )
                        blaster_email = gr.Textbox(
                            label="Email (required for NCBI)",
                            placeholder="your.email@example.com"
                        )
                        blaster_api_key = gr.Textbox(
                            label="NCBI API Key (optional)",
                            type="password",
                            placeholder="Optional"
                        )
                        blaster_btn = gr.Button("Run BLASTER", variant="primary")
                    
                    with gr.Column():
                        blaster_output_fasta = gr.File(label="Output FASTA")
                        blaster_output_report = gr.File(label="BLAST Report")
                        blaster_report_text = gr.Textbox(
                            label="Preview Report Contents",
                            lines=20,
                            max_lines=30
                        )
                        blaster_to_trim_btn = gr.Button(
                            "Transfer to TRIM →",
                            variant="secondary"
                        )
            
            # TRIM Tab
            with gr.Tab("TRIM", id=1):
                gr.Markdown("### Sequence Quality Control & Trimming")
                with gr.Row():
                    with gr.Column():
                        trim_project = gr.Textbox(
                            label="Project Name",
                            placeholder="e.g., my_project",
                            value=""
                        )
                        trim_files = gr.File(
                            label="Input FASTA Files",
                            file_count="multiple",
                            file_types=[".fasta", ".fa"]
                        )
                        trim_auto = gr.Checkbox(
                            label="Auto-calculate thresholds",
                            value=False
                        )
                        with gr.Row():
                            trim_low = gr.Number(
                                label="Lower Threshold",
                                value=None,
                                minimum=1,
                                precision=0
                            )
                            trim_high = gr.Number(
                                label="Upper Threshold",
                                value=None,
                                minimum=1,
                                precision=0
                            )
                        trim_btn = gr.Button("Run TRIM", variant="primary")
                    
                    with gr.Column():
                        trim_histogram = gr.Plot(label="Length Distribution")
                        trim_output_fasta = gr.File(label="Trimmed FASTA")
                        trim_output_report = gr.File(label="QC Report")
                        trim_report_text = gr.Textbox(
                            label="Preview Report Contents",
                            lines=20,
                            max_lines=30
                        )
                        trim_to_plm_btn = gr.Button(
                            "Transfer to PLMCLUSTV2 →",
                            variant="secondary"
                        )
            
            # PLMCLUSTV2 Tab
            with gr.Tab("PLMCLUSTV2", id=2):
                gr.Markdown("### Protein Language Model Clustering")
                with gr.Row():
                    with gr.Column():
                        plm_project = gr.Textbox(
                            label="Project Name",
                            placeholder="e.g., my_project",
                            value=""
                        )
                        plm_files = gr.File(
                            label="Input FASTA Files",
                            file_count="multiple",
                            file_types=[".fasta", ".fa"]
                        )
                        plm_auto_clusters = gr.Checkbox(
                            label="Auto-determine number of clusters",
                            value=True
                        )
                        plm_cluster_num = gr.Number(
                            label="Number of Clusters",
                            value=5,
                            minimum=2,
                            precision=0,
                            visible=False
                        )
                        with gr.Row() as plm_sil_row:
                            plm_sil_min = gr.Number(
                                label="Lower Search Bound",
                                value=2,
                                minimum=2,
                                precision=0
                            )
                            plm_sil_max = gr.Number(
                                label="Upper Search Bound",
                                value=10,
                                minimum=2,
                                precision=0
                            )
                        plm_btn = gr.Button("Run PLMCLUSTV2", variant="primary")
                    
                    with gr.Column():
                        plm_metrics_csv = gr.File(label="Metrics CSV")
                        plm_tsne_csv = gr.File(label="t-SNE Coordinates CSV")
                        plm_winners_fasta = gr.File(label="Cluster Winners FASTA")
                        plm_clusters_zip = gr.File(label="Per-Cluster FASTA Files (ZIP)")
                        plm_color_by = gr.Radio(
                            label="Color by",
                            choices=["Cluster", "NLL Score"],
                            value="Cluster"
                        )
                        plm_tsne_fullscreen = gr.Button("View t-SNE Visualization (Full Screen)", variant="primary")
                        plm_umap_fullscreen = gr.Button("View UMAP Visualization (Full Screen)", variant="primary")
                        plm_status = gr.Textbox(label="Status")
                        
                        def toggle_cluster_inputs(auto):
                            return gr.update(visible=not auto), gr.update(visible=auto)
                        
                        plm_auto_clusters.change(
                            fn=toggle_cluster_inputs,
                            inputs=[plm_auto_clusters],
                            outputs=[plm_cluster_num, plm_sil_row]
                        )
        
        # Transfer functions
        def transfer_blaster_to_trim(blaster_fasta, blaster_proj):
            """Transfer BLASTER output to TRIM input and switch to TRIM tab"""
            if blaster_fasta:
                # Get the file path - Gradio File component returns a dict or string
                if isinstance(blaster_fasta, dict):
                    file_path = blaster_fasta.get('name', '') or blaster_fasta.get('path', '')
                elif isinstance(blaster_fasta, str):
                    file_path = blaster_fasta
                elif hasattr(blaster_fasta, 'name'):
                    file_path = blaster_fasta.name
                else:
                    file_path = str(blaster_fasta)
                
                # Ensure file exists
                if not file_path or not os.path.exists(file_path):
                    return [], "", None, gr.update(selected=1)
                
                # Copy project name if available
                project_update = blaster_proj if blaster_proj else ""
                
                # Return updates: file as a list (trim_files expects a list), project name, histogram, and switch tab
                # Also trigger histogram update by returning the histogram
                histogram = generate_trim_histogram(project_update, [file_path])
                return [file_path], project_update, histogram, gr.update(selected=1)
            return [], "", None, gr.update(selected=1)
        
        def transfer_trim_to_plm(trim_fasta, trim_proj):
            """Transfer TRIM output to PLMCLUSTV2 input and switch to PLMCLUSTV2 tab"""
            if trim_fasta:
                # Get the file path - Gradio File component returns a dict or string
                if isinstance(trim_fasta, dict):
                    file_path = trim_fasta.get('name', '') or trim_fasta.get('path', '')
                elif isinstance(trim_fasta, str):
                    file_path = trim_fasta
                elif hasattr(trim_fasta, 'name'):
                    file_path = trim_fasta.name
                else:
                    file_path = str(trim_fasta)
                
                # Ensure file exists
                if not file_path or not os.path.exists(file_path):
                    return [], "", gr.update(selected=2)
                
                # Copy project name if available
                project_update = trim_proj if trim_proj else ""
                
                # Return updates: file as a list (plm_files expects a list), project name, and switch tab
                return [file_path], project_update, gr.update(selected=2)
            return [], "", gr.update(selected=2)
        
        # Wire up events
        blaster_btn.click(
            fn=run_blaster_workflow,
            inputs=[
                blaster_project,
                blaster_files,
                blaster_num_hits,
                blaster_db,
                blaster_evalue,
                blaster_email,
                blaster_api_key
            ],
            outputs=[blaster_output_fasta, blaster_output_report, blaster_report_text]
        )
        
        # Wire up transfer buttons
        blaster_to_trim_btn.click(
            fn=transfer_blaster_to_trim,
            inputs=[blaster_output_fasta, blaster_project],
            outputs=[trim_files, trim_project, trim_histogram, tabs]
        )
        
        trim_to_plm_btn.click(
            fn=transfer_trim_to_plm,
            inputs=[trim_output_fasta, trim_project],
            outputs=[plm_files, plm_project, tabs]
        )
        
        # Generate histogram when files are uploaded
        def update_histogram(project, files):
            """Wrapper to handle file uploads properly"""
            return generate_trim_histogram(project, files)
        
        trim_files.change(
            fn=update_histogram,
            inputs=[trim_project, trim_files],
            outputs=[trim_histogram]
        )
        
        # Also update when project name changes (if files are already uploaded)
        trim_project.change(
            fn=update_histogram,
            inputs=[trim_project, trim_files],
            outputs=[trim_histogram]
        )
        
        # Run trim when button is clicked
        trim_btn.click(
            fn=run_trim_workflow,
            inputs=[
                trim_project,
                trim_files,
                trim_auto,
                trim_low,
                trim_high
            ],
            outputs=[trim_output_fasta, trim_output_report, trim_report_text]
        )
        
        def update_plm_plots(color_by, tsne_csv_path, project_name):
            """Update plots with different coloring without re-running"""
            if not tsne_csv_path or not os.path.exists(tsne_csv_path):
                return None, None
            
            try:
                results_dir = Path("results") / "plmclustv2" / project_name
                umap_csv = results_dir / f"umap_coordinates_{project_name}.csv"
                
                df_tsne = pd.read_csv(tsne_csv_path)
                if umap_csv.exists():
                    df_umap = pd.read_csv(umap_csv)
                else:
                    df_umap = df_tsne.copy()  # Fallback
                
                # Add ranking and winner status if not present
                for df in [df_tsne, df_umap]:
                    if 'rank_text' not in df.columns:
                        df['rank'] = df['nll_score'].rank(method='min').astype(int)
                        df['rank_text'] = df.apply(lambda row: f"{int(row['rank'])}{'st' if int(row['rank']) % 10 == 1 and int(row['rank']) % 100 != 11 else 'nd' if int(row['rank']) % 10 == 2 and int(row['rank']) % 100 != 12 else 'rd' if int(row['rank']) % 10 == 3 and int(row['rank']) % 100 != 13 else 'th'} out of {len(df)}", axis=1)
                    # Ensure is_winner column exists (default to False if not present)
                    if 'is_winner' not in df.columns:
                        df['is_winner'] = False
                
                # Reset indices to ensure proper alignment
                df_tsne = df_tsne.reset_index(drop=True)
                df_umap = df_umap.reset_index(drop=True)
                
                # Create coordinate mappings for both dataframes
                tsne_coord_to_idx = {}
                for idx, row in df_tsne.iterrows():
                    tsne_coord_to_idx[(row['Dim1'], row['Dim2'])] = idx
                
                umap_coord_to_idx = {}
                for idx, row in df_umap.iterrows():
                    umap_coord_to_idx[(row['Dim1'], row['Dim2'])] = idx
                
                # Recreate plots with correct coloring
                if color_by == "NLL Score":
                    tsne_plot = px.scatter(df_tsne, x='Dim1', y='Dim2', color='nll_score', 
                                         hover_data={},  # Don't use hover_data, we'll set customdata manually
                                         title='t-SNE Clustering Visualization (colored by NLL)',
                                         color_continuous_scale='Viridis')
                    umap_plot = px.scatter(df_umap, x='Dim1', y='Dim2', color='nll_score',
                                         hover_data={},  # Don't use hover_data, we'll set customdata manually
                                         title='UMAP Clustering Visualization (colored by NLL)',
                                         color_continuous_scale='Viridis')
                    hover_template = '<b>%{hovertext}</b><br>Dim1: %{x:.2f}<br>Dim2: %{y:.2f}<br>' + \
                                   'NLL Score: %{customdata[0]:.4f}<br>' + \
                                   'Cluster: %{customdata[2]}<br>' + \
                                   'Rank: %{customdata[1]}<br>' + \
                                   '%{customdata[3]}<extra></extra>'
                    plot_dataframes = [(tsne_plot, df_tsne, tsne_coord_to_idx), (umap_plot, df_umap, umap_coord_to_idx)]
                else:
                    # Use string conversion to ensure discrete coloring
                    df_tsne_str = df_tsne.copy()
                    df_tsne_str['cluster_str'] = df_tsne_str['cluster'].astype(str)
                    df_umap_str = df_umap.copy()
                    df_umap_str['cluster_str'] = df_umap_str['cluster'].astype(str)
                    
                    tsne_plot = px.scatter(df_tsne_str, x='Dim1', y='Dim2', color='cluster_str',
                                         hover_data={},  # Don't use hover_data, we'll set customdata manually
                                         title='t-SNE Clustering Visualization',
                                         labels={'cluster_str': 'Cluster'},
                                         color_discrete_sequence=px.colors.qualitative.Set3)
                    umap_plot = px.scatter(df_umap_str, x='Dim1', y='Dim2', color='cluster_str',
                                         hover_data={},  # Don't use hover_data, we'll set customdata manually
                                         title='UMAP Clustering Visualization',
                                         labels={'cluster_str': 'Cluster'},
                                         color_discrete_sequence=px.colors.qualitative.Set3)
                    hover_template = '<b>%{hovertext}</b><br>Dim1: %{x:.2f}<br>Dim2: %{y:.2f}<br>' + \
                                   'Cluster: %{customdata[2]}<br>' + \
                                   'NLL Score: %{customdata[0]:.4f}<br>' + \
                                   'Rank: %{customdata[1]}<br>' + \
                                   '%{customdata[3]}<extra></extra>'
                    plot_dataframes = [(tsne_plot, df_tsne, tsne_coord_to_idx), (umap_plot, df_umap, umap_coord_to_idx)]
                
                # Apply hover styling with light text for dark background
                # Set customdata per trace to ensure proper alignment
                for fig, df, coord_to_idx in plot_dataframes:
                    for trace in fig.data:
                        # Get the x and y coordinates for this trace
                        x_coords = trace.x
                        y_coords = trace.y
                        
                        # Build customdata array matching the order of points in this trace
                        trace_customdata = []
                        trace_hovertext = []
                        
                        for x, y in zip(x_coords, y_coords):
                            # Find the corresponding dataframe row
                            idx = coord_to_idx.get((x, y), None)
                            if idx is not None:
                                row = df.iloc[idx]
                                # Order: [nll_score, rank_text, cluster, winner_message]
                                winner_msg = 'This protein is a cluster winner' if row.get('is_winner', False) else ''
                                trace_customdata.append([row['nll_score'], row['rank_text'], row['cluster'], winner_msg])
                                trace_hovertext.append(row['header'])
                            else:
                                # Fallback if coordinate not found
                                trace_customdata.append([0.0, 'N/A', 0, ''])
                                trace_hovertext.append('Unknown')
                        
                        # Update this trace with the correct customdata
                        trace.customdata = trace_customdata
                        trace.hovertemplate = hover_template
                        trace.hovertext = trace_hovertext
                    
                    # Update marker properties - use stars for winners, dots for others
                    # First, identify winners
                    winner_indices = df[df.get('is_winner', False)].index.tolist() if 'is_winner' in df.columns else []
                    
                    # Update all traces with base properties
                    fig.update_traces(
                        marker_size=6,
                        marker_opacity=0.7,
                        marker_line_width=0.5,
                        marker_line_color='white',
                        selector=dict(type='scatter')
                    )
                    
                    # For each trace, update markers to stars for winners
                    for trace in fig.data:
                        # Get the indices of points in this trace that are winners
                        trace_winner_mask = []
                        for i, (x, y) in enumerate(zip(trace.x, trace.y)):
                            idx = coord_to_idx.get((x, y), None)
                            if idx is not None and idx in winner_indices:
                                trace_winner_mask.append(True)
                            else:
                                trace_winner_mask.append(False)
                        
                        # Create marker symbol array: 'star' for winners, 'circle' for others
                        if any(trace_winner_mask):
                            marker_symbols = ['star' if is_winner else 'circle' for is_winner in trace_winner_mask]
                            # Update marker size for stars (make them slightly larger)
                            marker_sizes = [10 if is_winner else 6 for is_winner in trace_winner_mask]
                            trace.marker.symbol = marker_symbols
                            trace.marker.size = marker_sizes
                    layout_dict = {
                        'height': 700,
                        'width': None,
                        'showlegend': True,
                        'hovermode': 'closest',
                        'plot_bgcolor': 'rgba(0,0,0,0)',
                        'paper_bgcolor': 'rgba(0,0,0,0)',
                        'font': dict(color='#ffffff', size=12),
                        'title_font': dict(color='#ffffff', size=16),
                        'xaxis': dict(
                            gridcolor='rgba(255,255,255,0.2)',
                            title_font=dict(color='#ffffff'),
                            tickfont=dict(color='#ffffff')
                        ),
                        'yaxis': dict(
                            gridcolor='rgba(255,255,255,0.2)',
                            title_font=dict(color='#ffffff'),
                            tickfont=dict(color='#ffffff')
                        ),
                        'legend': dict(
                            font=dict(color='#ffffff'),
                            bgcolor='rgba(0,0,0,0.5)',
                            bordercolor='rgba(255,255,255,0.3)',
                            x=1,  # Right side
                            y=0,  # Bottom
                            xanchor='right',
                            yanchor='bottom'
                        ),
                        'hoverlabel': dict(
                            bgcolor='rgba(255,255,255,0.85)',
                            bordercolor='rgba(0,0,0,0.3)',
                            font_size=12,
                            font_color='#000000'
                        )
                    }
                    
                    fig.update_layout(**layout_dict)
                    
                    # Add colorbar configuration for NLL coloring
                    # For Plotly Express continuous color scales, the colorbar is automatically created
                    # We need to update it via the layout's coloraxis_colorbar
                    if color_by == "NLL Score":
                        # Update colorbar styling - Plotly Express automatically creates coloraxis
                        fig.update_layout(
                            coloraxis_colorbar=dict(
                                title=dict(text='NLL Score', font=dict(color='#ffffff')),
                                tickfont=dict(color='#ffffff'),
                                bgcolor='rgba(0,0,0,0.7)',
                                bordercolor='rgba(255,255,255,0.3)',
                                borderwidth=1
                            )
                        )
                
                return tsne_plot, umap_plot
            except Exception as e:
                import traceback
                traceback.print_exc()
                return None, None
        
        plm_btn.click(
            fn=run_plmclustv2_workflow,
            inputs=[
                plm_project,
                plm_files,
                plm_auto_clusters,
                plm_cluster_num,
                plm_sil_min,
                plm_sil_max
            ],
            outputs=[plm_metrics_csv, plm_tsne_csv, plm_winners_fasta, plm_clusters_zip, plm_status]
        )
        
        # Full-screen modals for plots
        with gr.Row(visible=False) as plm_tsne_modal:
            with gr.Column(scale=1):
                plm_tsne_fullscreen_plot = gr.Plot(label="t-SNE Visualization (Full Screen)")
                gr.Button("Close", variant="stop").click(
                    fn=lambda: gr.update(visible=False),
                    outputs=[plm_tsne_modal]
                )
        
        with gr.Row(visible=False) as plm_umap_modal:
            with gr.Column(scale=1):
                plm_umap_fullscreen_plot = gr.Plot(label="UMAP Visualization (Full Screen)")
                gr.Button("Close", variant="stop").click(
                    fn=lambda: gr.update(visible=False),
                    outputs=[plm_umap_modal]
                )
        
        def generate_and_show_tsne(color_by, tsne_csv, project):
            """Generate t-SNE plot and show in fullscreen"""
            if tsne_csv:
                csv_path = tsne_csv if isinstance(tsne_csv, str) else (tsne_csv.name if hasattr(tsne_csv, 'name') else str(tsne_csv))
                if os.path.exists(csv_path) and os.path.isfile(csv_path):
                    tsne_plot, _ = update_plm_plots(color_by, csv_path, project)
                    if tsne_plot:
                        # Increase height for fullscreen
                        tsne_plot.update_layout(height=900)
                        return gr.update(visible=True), tsne_plot
            return gr.update(visible=False), None
        
        def generate_and_show_umap(color_by, tsne_csv, project):
            """Generate UMAP plot and show in fullscreen"""
            if tsne_csv:
                csv_path = tsne_csv if isinstance(tsne_csv, str) else (tsne_csv.name if hasattr(tsne_csv, 'name') else str(tsne_csv))
                if os.path.exists(csv_path) and os.path.isfile(csv_path):
                    _, umap_plot = update_plm_plots(color_by, csv_path, project)
                    if umap_plot:
                        # Increase height for fullscreen
                        umap_plot.update_layout(height=900)
                        return gr.update(visible=True), umap_plot
            return gr.update(visible=False), None
        
        plm_tsne_fullscreen.click(
            fn=generate_and_show_tsne,
            inputs=[plm_color_by, plm_tsne_csv, plm_project],
            outputs=[plm_tsne_modal, plm_tsne_fullscreen_plot]
        )
        
        plm_umap_fullscreen.click(
            fn=generate_and_show_umap,
            inputs=[plm_color_by, plm_tsne_csv, plm_project],
            outputs=[plm_umap_modal, plm_umap_fullscreen_plot]
        )
    
    return app

def main():
    """Main entry point for GUI"""
    app = create_interface()
    app.launch(share=False, server_name="127.0.0.1", server_port=7860)

if __name__ == "__main__":
    main()

