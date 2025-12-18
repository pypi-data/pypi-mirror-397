#!/usr/bin/env python3
"""
Phylogenetic Analysis Module
Generates phylogenetic trees and compares phylogenetic distances with embedding space distances
"""

import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from Bio import SeqIO, AlignIO, Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Phylo.Consensus import bootstrap_trees, get_support
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr, spearmanr
import warnings
from tqdm import tqdm
import pickle
import json
import sqlite3
import hashlib
from .common import project_dir

warnings.filterwarnings('ignore')

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

class EmbeddingCache:
    """Efficient caching system for ESM2 embeddings using SQLite."""
    
    def __init__(self, cache_dir="embeddings/esm2"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.db_path = os.path.join(cache_dir, "embeddings.db")
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database."""
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
        
        with sqlite3.connect(self.db_path) as conn:
            if needs_migration:
                # Drop old table and recreate with new schema
                conn.execute("DROP TABLE IF EXISTS embeddings")
            
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
        """Create a hash of the sequence for efficient lookup."""
        return hashlib.sha256(sequence.encode()).hexdigest()
    
    def get_embedding_and_score(self, sequence):
        """Get both embedding and NLL score from cache if they exist."""
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
        sequence_hash = self._hash_sequence(sequence)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM embeddings WHERE sequence_hash = ?",
                (sequence_hash,)
            )
    
    def store_embedding_and_score(self, sequence, embedding, nll_score):
        """Store both embedding and NLL score in cache."""
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
        # Store with a placeholder NLL score - this is for backward compatibility only
        # New code should use store_embedding_and_score
        self.store_embedding_and_score(sequence, embedding, 0.0)
    
    def get_cached_embeddings(self, sequences):
        """Get cached embeddings for multiple sequences."""
        cached = {}
        missing = []
        
        for seq_id, sequence in sequences.items():
            embedding = self.get_embedding(sequence)
            if embedding is not None:
                cached[seq_id] = embedding
            else:
                missing.append((seq_id, sequence))
        
        return cached, missing

def create_output_directories(results_dir):
    """Create the output directory structure."""
    directories = [
        os.path.join(results_dir, 'figures'),
        os.path.join(results_dir, 'data'),
        os.path.join(results_dir, 'trees'),
        os.path.join(results_dir, 'reports')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("Created output directory structure")

class PhylogeneticAnalyzer:
    """Analyzer for phylogenetic trees and embedding space comparisons."""
    
    def __init__(self, fasta_file, results_dir):
        self.fasta_file = fasta_file
        self.results_dir = results_dir
        self.sequences = {}
        self.alignment = None
        self.tree = None
        self.distance_matrix = None
        self.embeddings = None
        self.embedding_distances = {}
        self.embedding_cache = EmbeddingCache()
        
        # Create output directories
        create_output_directories(results_dir)
    
    def load_sequences(self):
        """Load sequences from FASTA file."""
        print("Loading sequences from FASTA file...")
        
        for record in SeqIO.parse(self.fasta_file, 'fasta'):
            self.sequences[record.id] = str(record.seq)
        
        print(f"Loaded {len(self.sequences)} sequences")
        return self.sequences
    
    def create_alignment(self):
        """Create multiple sequence alignment using MAFFT."""
        print("Creating multiple sequence alignment using MAFFT...")
        
        import tempfile
        import subprocess
        
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = os.path.join(temp_dir, "input.fasta")
            output_file = os.path.join(temp_dir, "aligned.fasta")
            
            # Write sequences to temporary file
            with open(input_file, 'w') as f:
                for seq_id, sequence in self.sequences.items():
                    f.write(f">{seq_id}\n{sequence}\n")
            
            # Run MAFFT alignment
            try:
                with open(output_file, 'w') as outfile:
                    subprocess.run([
                        "mafft", "--auto", input_file
                    ], check=True, stdout=outfile, stderr=subprocess.PIPE)
                
                # Load alignment
                self.alignment = AlignIO.read(output_file, 'fasta')
                print(f"MAFFT alignment created with {len(self.alignment)} sequences")
                
            except Exception as e:
                print(f"Warning: MAFFT alignment failed: {e}")
                print("Using simple alignment approach...")
                self._create_simple_alignment()
        
        return self.alignment
    
    def _create_simple_alignment(self):
        """Create a simple alignment by padding sequences."""
        print("Creating simple alignment by padding sequences...")
        
        # Find the longest sequence
        max_length = max(len(seq) for seq in self.sequences.values())
        
        # Pad all sequences to the same length
        aligned_sequences = []
        for seq_id, sequence in self.sequences.items():
            padded_seq = sequence + '-' * (max_length - len(sequence))
            aligned_sequences.append((seq_id, padded_seq))
        
        # Create alignment object
        from Bio.Align import MultipleSeqAlignment
        from Bio.Seq import Seq
        from Bio.SeqRecord import SeqRecord
        
        alignment_records = []
        for seq_id, sequence in aligned_sequences:
            record = SeqRecord(Seq(sequence), id=seq_id, description="")
            alignment_records.append(record)
        
        self.alignment = MultipleSeqAlignment(alignment_records)
        print(f"Simple alignment created with {len(self.alignment)} sequences")
    
    def build_phylogenetic_tree(self):
        """Build phylogenetic tree using FastTree."""
        print("Building phylogenetic tree using FastTree...")
        
        if self.alignment is None:
            print("Error: No alignment available. Run create_alignment() first.")
            return None
        
        import tempfile
        import subprocess
        
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            alignment_file = os.path.join(temp_dir, "alignment.fasta")
            tree_file = os.path.join(temp_dir, "tree.newick")
            
            # Write alignment to file
            AlignIO.write(self.alignment, alignment_file, "fasta")
            
            # Run FastTree
            try:
                subprocess.run([
                    "FastTree", "-out", tree_file, alignment_file
                ], check=True, capture_output=True)
                
                # Load tree
                self.tree = Phylo.read(tree_file, 'newick')
                print("FastTree phylogenetic tree built successfully")
                
            except Exception as e:
                print(f"Warning: FastTree failed: {e}")
                print("Falling back to BioPython tree construction...")
                self._build_tree_with_biopython()
        
        return self.tree
    
    def _build_tree_with_biopython(self):
        """Fallback tree construction using BioPython."""
        print("Building tree using BioPython UPGMA method...")
        
        # Calculate distance matrix
        calculator = DistanceCalculator('identity')
        dm = calculator.get_distance(self.alignment)
        self.distance_matrix = dm
        
        # Build tree using UPGMA method
        constructor = DistanceTreeConstructor()
        self.tree = constructor.upgma(dm)
        
        print("Phylogenetic tree built successfully")
        return self.tree
    
    def get_phylogenetic_distances(self):
        """Extract pairwise phylogenetic distances from the tree."""
        print("Extracting phylogenetic distances...")
        
        if self.tree is None:
            print("Error: No tree available. Run build_phylogenetic_tree() first.")
            return None
        
        # Get all leaf names
        leaf_names = [leaf.name for leaf in self.tree.get_terminals()]
        
        # Calculate total possible pairs
        total_pairs = len(leaf_names) * (len(leaf_names) - 1) // 2
        
        # Cap to 10,000 randomly-sampled distances
        max_distances = 10000
        if total_pairs > max_distances:
            print(f"Sampling {max_distances:,} random pairs from {total_pairs:,} total pairs")
            # Generate all possible pairs and sample randomly
            all_pairs = [(leaf_names[i], leaf_names[j]) 
                         for i in range(len(leaf_names)) 
                         for j in range(i+1, len(leaf_names))]
            sampled_pairs = np.random.choice(len(all_pairs), max_distances, replace=False)
            pairs_to_calculate = [all_pairs[i] for i in sampled_pairs]
        else:
            pairs_to_calculate = [(leaf_names[i], leaf_names[j]) 
                                for i in range(len(leaf_names)) 
                                for j in range(i+1, len(leaf_names))]
        
        # Calculate pairwise distances with progress bar
        distances = {}
        
        with tqdm(total=len(pairs_to_calculate), desc="Extracting phylogenetic distances") as pbar:
            for name1, name2 in pairs_to_calculate:
                try:
                    distance = self.tree.distance(name1, name2)
                    distances[(name1, name2)] = distance
                    distances[(name2, name1)] = distance  # Symmetric
                except Exception as e:
                    print(f"Warning: Could not calculate distance between {name1} and {name2}: {e}")
                    distances[(name1, name2)] = np.nan
                    distances[(name2, name1)] = np.nan
                pbar.update(1)
        
        return distances
    
    def load_embeddings(self, embedding_file=None):
        """Load embeddings from cache or generate them."""
        print("Loading embeddings...")
        
        if embedding_file and os.path.exists(embedding_file):
            # Load pre-computed embeddings
            with open(embedding_file, 'rb') as f:
                self.embeddings = pickle.load(f)
            print(f"Loaded embeddings for {len(self.embeddings)} sequences")
        else:
            # Check cache first, then generate missing embeddings
            print("Checking embedding cache...")
            cached_embeddings, missing_sequences = self.embedding_cache.get_cached_embeddings(self.sequences)
            
            print(f"Found {len(cached_embeddings)} cached embeddings")
            if missing_sequences:
                print(f"Generating {len(missing_sequences)} new embeddings...")
                new_embeddings = self._generate_embeddings(missing_sequences)
                
                # Store new embeddings in cache
                for seq_id, embedding in new_embeddings.items():
                    self.embedding_cache.store_embedding(self.sequences[seq_id], embedding)
                
                # Combine cached and new embeddings
                self.embeddings = {**cached_embeddings, **new_embeddings}
            else:
                self.embeddings = cached_embeddings
        
        return self.embeddings
    
    def _generate_embeddings(self, sequences_to_generate):
        """Generate embeddings using plmclustv2 ESM2 strategy."""
        print("Generating embeddings using ESM2 model (plmclustv2 strategy)...")
        
        try:
            import torch
            import esm
        except ImportError:
            print("Warning: ESM2 not available. Using random embeddings for demonstration.")
            print("Please install: pip install fair-esm torch")
            return self._generate_random_embeddings(sequences_to_generate)
        
        # Check for MPS availability
        device = 'mps' if torch.backends.mps.is_available() else 'cpu'
        print(f"Using device: {device}")
        
        # Use the same strategy as plmclustv2
        model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
        model.eval().to(device)
        batch_converter = alphabet.get_batch_converter()
        pad_idx = batch_converter.alphabet.padding_idx
        
        embeddings = {}
        
        print(f"Computing ESM2 embeddings for {len(sequences_to_generate)} sequences...")
        
        # Process in batches for efficiency
        batch_size = 4  # Adjust based on memory
        sequences_list = list(sequences_to_generate)
        
        for i in tqdm(range(0, len(sequences_list), batch_size), desc="Computing embeddings"):
            batch_sequences = sequences_list[i:i+batch_size]
            
            try:
                # Prepare batch
                batch = [(seq_id, sequence) for seq_id, sequence in batch_sequences]
                labels, strs, tokens = batch_converter(batch)
                tokens = tokens.to(device)
                
                with torch.no_grad():
                    # Get representations
                    out = model(tokens, repr_layers=[33], return_contacts=False)
                    
                    # Extract embeddings (mean pooling over sequence length)
                    reps = out['representations'][33]
                    for j, (seq_id, sequence) in enumerate(batch_sequences):
                        emb = reps[j, 1:len(sequence)+1].mean(0)  # Skip CLS token, mean over sequence
                        embeddings[seq_id] = emb.cpu().numpy()
                
                # Memory cleanup
                del out, reps, tokens
                if device == 'mps':
                    torch.mps.empty_cache()
                
            except Exception as e:
                print(f"Warning: Failed to generate embeddings for batch starting with {batch_sequences[0][0]}: {e}")
                # Fallback to random embeddings for failed sequences
                for seq_id, sequence in batch_sequences:
                    embeddings[seq_id] = np.random.randn(1280)  # ESM2 embedding dimension
        
        print(f"Generated embeddings for {len(embeddings)} sequences")
        return embeddings
    
    def _generate_random_embeddings(self, sequences_to_generate):
        """Generate random embeddings as fallback."""
        print("Warning: Using random embeddings for demonstration")
        print("Please implement the actual plmclustv2 embedding strategy")
        
        embeddings = {}
        for seq_id, sequence in sequences_to_generate:
            # Generate random embedding (replace with actual plmclustv2 embedding)
            embedding = np.random.randn(1280)  # ESM2 embedding dimension
            embeddings[seq_id] = embedding
        
        return embeddings
    
    def calculate_embedding_distances(self):
        """Calculate distances in embedding space using cosine similarity and dot product."""
        print("Calculating embedding space distances...")
        
        if self.embeddings is None:
            print("Error: No embeddings available. Run load_embeddings() first.")
            return None
        
        # Get all sequence IDs
        seq_ids = list(self.embeddings.keys())
        
        # Calculate total possible pairs
        total_pairs = len(seq_ids) * (len(seq_ids) - 1) // 2
        
        # Cap to 10,000 randomly-sampled distances
        max_distances = 10000
        if total_pairs > max_distances:
            print(f"Sampling {max_distances:,} random pairs from {total_pairs:,} total pairs")
            # Generate all possible pairs and sample randomly
            all_pairs = [(seq_ids[i], seq_ids[j]) 
                         for i in range(len(seq_ids)) 
                         for j in range(i+1, len(seq_ids))]
            sampled_pairs = np.random.choice(len(all_pairs), max_distances, replace=False)
            pairs_to_calculate = [all_pairs[i] for i in sampled_pairs]
        else:
            pairs_to_calculate = [(seq_ids[i], seq_ids[j]) 
                                for i in range(len(seq_ids)) 
                                for j in range(i+1, len(seq_ids))]
        
        # Calculate cosine similarity and dot product
        cosine_distances = {}
        dot_product_distances = {}
        
        with tqdm(total=len(pairs_to_calculate), desc="Calculating embedding distances") as pbar:
            for seq_id1, seq_id2 in pairs_to_calculate:
                emb1 = self.embeddings[seq_id1]
                emb2 = self.embeddings[seq_id2]
                
                # Cosine similarity
                cosine_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                cosine_dist = 1 - cosine_sim  # Convert to distance
                cosine_distances[(seq_id1, seq_id2)] = cosine_dist
                cosine_distances[(seq_id2, seq_id1)] = cosine_dist
                
                # Dot product
                dot_prod = np.dot(emb1, emb2)
                dot_product_distances[(seq_id1, seq_id2)] = dot_prod
                dot_product_distances[(seq_id2, seq_id1)] = dot_prod
                
                pbar.update(1)
        
        self.embedding_distances = {
            'cosine': cosine_distances,
            'dot_product': dot_product_distances
        }
        
        return self.embedding_distances
    
    def compare_distances(self):
        """Compare phylogenetic distances with embedding distances."""
        print("Comparing phylogenetic and embedding distances...")
        
        # Get phylogenetic distances
        phylo_distances = self.get_phylogenetic_distances()
        if phylo_distances is None:
            return None
        
        # Get embedding distances
        if self.embedding_distances is None:
            self.calculate_embedding_distances()
        
        # Get the set of pairs that exist in both distance matrices
        phylo_pairs = set(phylo_distances.keys())
        embedding_pairs = set(self.embedding_distances['cosine'].keys())
        common_pairs = phylo_pairs.intersection(embedding_pairs)
        
        print(f"Found {len(common_pairs)} common pairs for comparison")
        
        # Prepare data for comparison
        comparison_data = []
        
        for (seq1, seq2) in common_pairs:
            if seq1 < seq2:  # Avoid duplicates
                phylo_dist = phylo_distances[(seq1, seq2)]
                cosine_dist = self.embedding_distances['cosine'].get((seq1, seq2), np.nan)
                dot_prod = self.embedding_distances['dot_product'].get((seq1, seq2), np.nan)
                
                comparison_data.append({
                    'seq1': seq1,
                    'seq2': seq2,
                    'phylogenetic_distance': phylo_dist,
                    'cosine_distance': cosine_dist,
                    'dot_product': dot_prod
                })
        
        self.comparison_data = pd.DataFrame(comparison_data)
        return self.comparison_data
    
    def calculate_correlation_metrics(self):
        """Calculate comprehensive correlation metrics between phylogenetic and embedding distances."""
        if not hasattr(self, 'comparison_data') or self.comparison_data.empty:
            return None
        
        # Clean data - remove NaN values
        phylo_clean = self.comparison_data['phylogenetic_distance'].dropna()
        cosine_clean = self.comparison_data['cosine_distance'].dropna()
        dot_clean = self.comparison_data['dot_product'].dropna()
        
        # Find common indices for pairwise comparisons
        common_phylo_cosine = self.comparison_data[['phylogenetic_distance', 'cosine_distance']].dropna()
        common_phylo_dot = self.comparison_data[['phylogenetic_distance', 'dot_product']].dropna()
        
        metrics = {}
        
        # Phylogenetic vs Cosine Distance correlations
        if len(common_phylo_cosine) > 1:
            phylo_vals = common_phylo_cosine['phylogenetic_distance']
            cosine_vals = common_phylo_cosine['cosine_distance']
            
            # Pearson correlation
            pearson_r, pearson_p = pearsonr(phylo_vals, cosine_vals)
            # Spearman correlation
            spearman_r, spearman_p = spearmanr(phylo_vals, cosine_vals)
            
            metrics['phylo_vs_cosine'] = {
                'pearson_r': pearson_r,
                'pearson_r_squared': pearson_r ** 2,
                'pearson_p_value': pearson_p,
                'spearman_r': spearman_r,
                'spearman_p_value': spearman_p,
                'n_pairs': len(common_phylo_cosine)
            }
        else:
            metrics['phylo_vs_cosine'] = {
                'pearson_r': np.nan,
                'pearson_r_squared': np.nan,
                'pearson_p_value': np.nan,
                'spearman_r': np.nan,
                'spearman_p_value': np.nan,
                'n_pairs': len(common_phylo_cosine)
            }
        
        # Phylogenetic vs Dot Product correlations
        if len(common_phylo_dot) > 1:
            phylo_vals = common_phylo_dot['phylogenetic_distance']
            dot_vals = common_phylo_dot['dot_product']
            
            # Pearson correlation
            pearson_r, pearson_p = pearsonr(phylo_vals, dot_vals)
            # Spearman correlation
            spearman_r, spearman_p = spearmanr(phylo_vals, dot_vals)
            
            metrics['phylo_vs_dot_product'] = {
                'pearson_r': pearson_r,
                'pearson_r_squared': pearson_r ** 2,
                'pearson_p_value': pearson_p,
                'spearman_r': spearman_r,
                'spearman_p_value': spearman_p,
                'n_pairs': len(common_phylo_dot)
            }
        else:
            metrics['phylo_vs_dot_product'] = {
                'pearson_r': np.nan,
                'pearson_r_squared': np.nan,
                'pearson_p_value': np.nan,
                'spearman_r': np.nan,
                'spearman_p_value': np.nan,
                'n_pairs': len(common_phylo_dot)
            }
        
        # Store metrics
        self.correlation_metrics = metrics
        return metrics
    
    def create_visualizations(self):
        """Create visualizations comparing phylogenetic and embedding distances."""
        print("Creating visualizations...")
        
        if not hasattr(self, 'comparison_data'):
            self.compare_distances()
        
        # 1. Scatter plot: Phylogenetic vs Cosine Distance
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.scatter(self.comparison_data['phylogenetic_distance'], 
                   self.comparison_data['cosine_distance'], alpha=0.6)
        plt.xlabel('Phylogenetic Distance')
        plt.ylabel('Cosine Distance')
        plt.title('Phylogenetic vs Cosine Distance')
        
        # Add correlation coefficient
        corr, p_value = pearsonr(self.comparison_data['phylogenetic_distance'].dropna(), 
                                self.comparison_data['cosine_distance'].dropna())
        plt.text(0.05, 0.95, f'r = {corr:.3f}\np = {p_value:.2e}', 
                transform=plt.gca().transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # 2. Scatter plot: Phylogenetic vs Dot Product
        plt.subplot(2, 2, 2)
        plt.scatter(self.comparison_data['phylogenetic_distance'], 
                   self.comparison_data['dot_product'], alpha=0.6)
        plt.xlabel('Phylogenetic Distance')
        plt.ylabel('Dot Product')
        plt.title('Phylogenetic vs Dot Product')
        
        # Add correlation coefficient
        corr, p_value = pearsonr(self.comparison_data['phylogenetic_distance'].dropna(), 
                                self.comparison_data['dot_product'].dropna())
        plt.text(0.05, 0.95, f'r = {corr:.3f}\np = {p_value:.2e}', 
                transform=plt.gca().transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # 3. Correlation heatmap
        plt.subplot(2, 2, 3)
        correlation_matrix = self.comparison_data[['phylogenetic_distance', 'cosine_distance', 'dot_product']].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, square=True)
        plt.title('Distance Correlation Matrix')
        
        # 4. Distribution comparison
        plt.subplot(2, 2, 4)
        plt.hist(self.comparison_data['phylogenetic_distance'], alpha=0.7, label='Phylogenetic', bins=20)
        plt.hist(self.comparison_data['cosine_distance'], alpha=0.7, label='Cosine', bins=20)
        plt.xlabel('Distance')
        plt.ylabel('Frequency')
        plt.title('Distance Distributions')
        plt.legend()
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(self.results_dir, 'figures', 'distance_comparison.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Distance comparison plot saved to: {plot_path}")
        
        # Create additional plots
        self._create_distance_heatmaps()
        self._create_tree_visualization()
    
    def _create_distance_heatmaps(self):
        """Create heatmaps of distance matrices."""
        print("Creating distance heatmaps...")
        
        # Get sequence IDs
        seq_ids = sorted(list(self.sequences.keys()))
        n_seqs = len(seq_ids)
        
        # Use the same sampling approach as the distance calculations
        total_pairs = n_seqs * (n_seqs - 1) // 2
        max_distances = 10000
        
        if total_pairs > max_distances:
            print(f"Sampling {max_distances:,} random pairs for heatmap visualization")
            # Generate all possible pairs and sample randomly
            all_pairs = [(seq_ids[i], seq_ids[j]) 
                         for i in range(len(seq_ids)) 
                         for j in range(i+1, len(seq_ids))]
            sampled_pairs = np.random.choice(len(all_pairs), max_distances, replace=False)
            pairs_to_visualize = [all_pairs[i] for i in sampled_pairs]
        else:
            pairs_to_visualize = [(seq_ids[i], seq_ids[j]) 
                                for i in range(len(seq_ids)) 
                                for j in range(i+1, len(seq_ids))]
        
        # Create phylogenetic distance matrix (sparse, only sampled pairs)
        phylo_distances = {}
        with tqdm(total=len(pairs_to_visualize), desc="Calculating phylogenetic distances for heatmap") as pbar:
            for seq1, seq2 in pairs_to_visualize:
                try:
                    distance = self.tree.distance(seq1, seq2)
                    phylo_distances[(seq1, seq2)] = distance
                    phylo_distances[(seq2, seq1)] = distance
                except Exception as e:
                    print(f"Warning: Could not calculate distance between {seq1} and {seq2}: {e}")
                    phylo_distances[(seq1, seq2)] = np.nan
                    phylo_distances[(seq2, seq1)] = np.nan
                pbar.update(1)
        
        # Create cosine distance matrix (sparse, only sampled pairs)
        cosine_distances = {}
        with tqdm(total=len(pairs_to_visualize), desc="Calculating embedding distances for heatmap") as pbar:
            for seq1, seq2 in pairs_to_visualize:
                emb1 = self.embeddings[seq1]
                emb2 = self.embeddings[seq2]
                
                # Cosine similarity
                cosine_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                cosine_dist = 1 - cosine_sim  # Convert to distance
                cosine_distances[(seq1, seq2)] = cosine_dist
                cosine_distances[(seq2, seq1)] = cosine_dist
                pbar.update(1)
        
        # Create a smaller subset for visualization (top 50 sequences by frequency)
        pair_counts = {}
        for seq1, seq2 in pairs_to_visualize:
            pair_counts[seq1] = pair_counts.get(seq1, 0) + 1
            pair_counts[seq2] = pair_counts.get(seq2, 0) + 1
        
        # Get top sequences by frequency
        top_sequences = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:50]
        top_seq_ids = [seq_id for seq_id, count in top_sequences]
        
        # Create matrices for visualization
        phylo_matrix = np.zeros((len(top_seq_ids), len(top_seq_ids)))
        cosine_matrix = np.zeros((len(top_seq_ids), len(top_seq_ids)))
        
        for i, seq1 in enumerate(top_seq_ids):
            for j, seq2 in enumerate(top_seq_ids):
                if i == j:
                    phylo_matrix[i, j] = 0
                    cosine_matrix[i, j] = 0
                else:
                    phylo_matrix[i, j] = phylo_distances.get((seq1, seq2), np.nan)
                    cosine_matrix[i, j] = cosine_distances.get((seq1, seq2), np.nan)
        
        # Create plots
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Phylogenetic distance heatmap
        sns.heatmap(phylo_matrix, xticklabels=top_seq_ids, yticklabels=top_seq_ids, 
                   cmap='viridis', ax=axes[0], square=True)
        axes[0].set_title('Phylogenetic Distance Matrix (Top 50 Sequences)')
        axes[0].set_xlabel('Sequence ID')
        axes[0].set_ylabel('Sequence ID')
        
        # Cosine distance heatmap
        sns.heatmap(cosine_matrix, xticklabels=top_seq_ids, yticklabels=top_seq_ids, 
                   cmap='viridis', ax=axes[1], square=True)
        axes[1].set_title('Cosine Distance Matrix (Top 50 Sequences)')
        axes[1].set_xlabel('Sequence ID')
        axes[1].set_ylabel('Sequence ID')
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(self.results_dir, 'figures', 'distance_matrices.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Distance matrices plot saved to: {plot_path}")
    
    def _create_tree_visualization(self):
        """Create phylogenetic tree visualization."""
        print("Creating phylogenetic tree visualization...")
        
        if self.tree is None:
            print("No tree available for visualization")
            return
        
        # Create tree plot
        plt.figure(figsize=(12, 8))
        Phylo.draw(self.tree, do_show=False)
        plt.title('Phylogenetic Tree')
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(self.results_dir, 'figures', 'phylogenetic_tree.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Phylogenetic tree plot saved to: {plot_path}")
    
    def save_data(self):
        """Save all data for later analysis."""
        print("Saving data...")
        
        # Save comparison data
        data_path = os.path.join(self.results_dir, 'data', 'distance_comparison.csv')
        self.comparison_data.to_csv(data_path, index=False)
        print(f"Comparison data saved to: {data_path}")
        
        # Save phylogenetic tree
        tree_path = os.path.join(self.results_dir, 'trees', 'phylogenetic_tree.newick')
        Phylo.write(self.tree, tree_path, 'newick')
        print(f"Phylogenetic tree saved to: {tree_path}")
        
        # Save distance matrices
        matrices_path = os.path.join(self.results_dir, 'data', 'distance_matrices.pkl')
        matrices_data = {
            'phylogenetic_distances': self.get_phylogenetic_distances(),
            'cosine_distances': self.embedding_distances['cosine'],
            'dot_product_distances': self.embedding_distances['dot_product']
        }
        with open(matrices_path, 'wb') as f:
            pickle.dump(matrices_data, f)
        print(f"Distance matrices saved to: {matrices_path}")
        
        # Save embeddings
        embeddings_path = os.path.join(self.results_dir, 'data', 'embeddings.pkl')
        with open(embeddings_path, 'wb') as f:
            pickle.dump(self.embeddings, f)
        print(f"Embeddings saved to: {embeddings_path}")
    
    def generate_report(self):
        """Generate comprehensive report."""
        print("Generating report...")
        
        report = []
        report.append("# Phylogenetic vs Embedding Distance Analysis Report")
        report.append("")
        report.append(f"**Analysis Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Input File**: {os.path.basename(self.fasta_file)}")
        report.append(f"**Number of Sequences**: {len(self.sequences)}")
        report.append("")
        
        # Correlation analysis
        if hasattr(self, 'comparison_data'):
            report.append("## Distance Correlation Analysis")
            report.append("")
            
            # Phylogenetic vs Cosine
            corr, p_value = pearsonr(self.comparison_data['phylogenetic_distance'].dropna(), 
                                    self.comparison_data['cosine_distance'].dropna())
            report.append(f"### Phylogenetic vs Cosine Distance")
            report.append(f"- **Pearson correlation**: {corr:.3f}")
            report.append(f"- **P-value**: {p_value:.2e}")
            report.append(f"- **Interpretation**: {'Strong correlation' if abs(corr) > 0.7 else 'Moderate correlation' if abs(corr) > 0.3 else 'Weak correlation'}")
            report.append("")
            
            # Phylogenetic vs Dot Product
            corr, p_value = pearsonr(self.comparison_data['phylogenetic_distance'].dropna(), 
                                    self.comparison_data['dot_product'].dropna())
            report.append(f"### Phylogenetic vs Dot Product")
            report.append(f"- **Pearson correlation**: {corr:.3f}")
            report.append(f"- **P-value**: {p_value:.2e}")
            report.append(f"- **Interpretation**: {'Strong correlation' if abs(corr) > 0.7 else 'Moderate correlation' if abs(corr) > 0.3 else 'Weak correlation'}")
            report.append("")
        
        # Save report
        report_path = os.path.join(self.results_dir, 'reports', 'phylogenetic_analysis_report.md')
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Report saved to: {report_path}")
    
    def run_complete_analysis(self):
        """Run the complete phylogenetic analysis."""
        print("Starting phylogenetic analysis...")
        
        # Load sequences
        self.load_sequences()
        
        # Create alignment
        self.create_alignment()
        
        # Build phylogenetic tree
        self.build_phylogenetic_tree()
        
        # Load embeddings
        self.load_embeddings()
        
        # Calculate embedding distances
        self.calculate_embedding_distances()
        
        # Compare distances
        self.compare_distances()
        
        # Calculate correlation metrics
        self.calculate_correlation_metrics()
        
        # Create visualizations
        self.create_visualizations()
        
        # Save data
        self.save_data()
        
        # Generate report
        self.generate_report()
        
        print("Phylogenetic analysis complete!")
        return self.comparison_data

def process_single_fasta(fasta_path, project_name, results_base_dir):
    """
    Process a single FASTA file independently.
    
    Args:
        fasta_path: Path to the FASTA file
        project_name: Project name
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
    
    # Create analyzer and run analysis
    analyzer = PhylogeneticAnalyzer(fasta_path, file_results_dir)
    
    try:
        results = analyzer.run_complete_analysis()
        
        print(f"  → Results saved to: {file_results_dir}")
        print(f"  → Sequences analyzed: {len(analyzer.sequences)}")
        
        # Get correlation metrics if available
        correlation_metrics = getattr(analyzer, 'correlation_metrics', None)
        
        return {
            'fasta_name': fasta_name,
            'file_stem': file_stem,
            'results_dir': file_results_dir,
            'num_sequences': len(analyzer.sequences),
            'results': results,
            'correlation_metrics': correlation_metrics,
            'success': True
        }
    except Exception as e:
        print(f"   Error processing {fasta_name}: {str(e)}")
        return {
            'fasta_name': fasta_name,
            'file_stem': file_stem,
            'results_dir': file_results_dir,
            'error': str(e),
            'success': False
        }

def run_merged_mode(fasta_paths, project_name, results_dir, start_time):
    """Process multiple FASTA files in merged mode (original behavior)."""
    print("Merging all FASTA files into single analysis...")
    
    # Create a temporary merged FASTA file
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_file:
        merged_fasta = temp_file.name
        
        # Merge all FASTA files
        sequence_count = 0
        for fasta_path in fasta_paths:
            print(f"  Adding sequences from: {os.path.basename(fasta_path)}")
            for record in SeqIO.parse(fasta_path, 'fasta'):
                # Add file prefix to sequence ID to avoid conflicts
                file_prefix = os.path.splitext(os.path.basename(fasta_path))[0]
                new_id = f"{file_prefix}_{record.id}"
                temp_file.write(f">{new_id}\n{str(record.seq)}\n")
                sequence_count += 1
        
        temp_file.flush()
    
    print(f"Merged {sequence_count} sequences from {len(fasta_paths)} files")
    
    try:
        # Create analyzer with merged file
        analyzer = PhylogeneticAnalyzer(merged_fasta, results_dir)
        results = analyzer.run_complete_analysis()
        
        # Clean up temporary file
        os.unlink(merged_fasta)
        
        end_time = datetime.datetime.now()
        
        print(f"\n Merged analysis complete!")
        print(f" Results saved to: {results_dir}")
        print(f" Phylogenetic tree generated")
        print(f" Distance comparisons completed")
        print(f"  Duration: {end_time - start_time}")
        
        return {
            'mode': 'merged',
            'files_processed': len(fasta_paths),
            'total_sequences': sequence_count,
            'results': results,
            'results_dir': results_dir,
            'duration': end_time - start_time
        }
        
    except Exception as e:
        # Clean up temporary file on error
        if os.path.exists(merged_fasta):
            os.unlink(merged_fasta)
        raise e

def run_separate_mode(fasta_paths, project_name, results_dir, start_time):
    """Process each FASTA file separately."""
    all_results = []
    
    # Create base results directory
    os.makedirs(results_dir, exist_ok=True)
    
    for i, fasta_path in enumerate(fasta_paths, 1):
        print(f"\n--- Processing file {i}/{len(fasta_paths)} ---")
        result = process_single_fasta(fasta_path, project_name, results_dir)
        all_results.append(result)
    
    # Create a summary log for all files
    end_time = datetime.datetime.now()
    summary_log_path = os.path.join(results_dir, f"summary_log_{project_name}.txt")
    
    successful_results = [r for r in all_results if r['success']]
    failed_results = [r for r in all_results if not r['success']]
    
    with open(summary_log_path, 'w') as log_f:
        log_f.write("Phylogenetic Analysis Separate Mode Summary\n")
        log_f.write("==========================================\n\n")
        log_f.write(f"Run start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Run end:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_f.write(f"Duration:  {end_time - start_time}\n\n")
        log_f.write("Configuration:\n")
        log_f.write(f"  PROJECT: {project_name}\n")
        log_f.write(f"  Mode: Keep Separate\n")
        log_f.write(f"  Total files processed: {len(all_results)}\n")
        log_f.write(f"  Successful: {len(successful_results)}\n")
        log_f.write(f"  Failed: {len(failed_results)}\n\n")
        
        if successful_results:
            total_sequences = sum(r['num_sequences'] for r in successful_results)
            log_f.write(f"Total sequences across successful files: {total_sequences}\n\n")
            
            log_f.write("Successful file-by-file results:\n")
            for result in successful_results:
                log_f.write(f"\n  File: {result['fasta_name']}\n")
                log_f.write(f"    Sequences: {result['num_sequences']}\n")
                log_f.write(f"    Results directory: {result['results_dir']}\n")
                
                # Add correlation metrics if available
                if result.get('correlation_metrics'):
                    metrics = result['correlation_metrics']
                    
                    log_f.write(f"    \n")
                    log_f.write(f"    Correlation Analysis:\n")
                    
                    # Phylogenetic vs Cosine Distance
                    if 'phylo_vs_cosine' in metrics:
                        cosine_metrics = metrics['phylo_vs_cosine']
                        log_f.write(f"      Phylogenetic vs Cosine Distance:\n")
                        log_f.write(f"        Pearson r: {cosine_metrics['pearson_r']:.4f}\n")
                        log_f.write(f"        Pearson r²: {cosine_metrics['pearson_r_squared']:.4f}\n")
                        log_f.write(f"        Pearson p-value: {cosine_metrics['pearson_p_value']:.2e}\n")
                        log_f.write(f"        Spearman r: {cosine_metrics['spearman_r']:.4f}\n")
                        log_f.write(f"        Spearman p-value: {cosine_metrics['spearman_p_value']:.2e}\n")
                        log_f.write(f"        N pairs: {cosine_metrics['n_pairs']}\n")
                    
                    # Phylogenetic vs Dot Product
                    if 'phylo_vs_dot_product' in metrics:
                        dot_metrics = metrics['phylo_vs_dot_product']
                        log_f.write(f"      Phylogenetic vs Dot Product:\n")
                        log_f.write(f"        Pearson r: {dot_metrics['pearson_r']:.4f}\n")
                        log_f.write(f"        Pearson r²: {dot_metrics['pearson_r_squared']:.4f}\n")
                        log_f.write(f"        Pearson p-value: {dot_metrics['pearson_p_value']:.2e}\n")
                        log_f.write(f"        Spearman r: {dot_metrics['spearman_r']:.4f}\n")
                        log_f.write(f"        Spearman p-value: {dot_metrics['spearman_p_value']:.2e}\n")
                        log_f.write(f"        N pairs: {dot_metrics['n_pairs']}\n")
        
        if failed_results:
            log_f.write(f"\nFailed files:\n")
            for result in failed_results:
                log_f.write(f"\n  File: {result['fasta_name']}\n")
                log_f.write(f"    Error: {result['error']}\n")
        
        log_f.write(f"\nAll results saved under: {results_dir}\n")
        log_f.write("Each successful file has its own subdirectory with complete phylogenetic analysis.\n")
    
    print(f"\n=== SUMMARY ===")
    print(f"Processed {len(all_results)} files")
    print(f"Successful: {len(successful_results)}")
    if failed_results:
        print(f"Failed: {len(failed_results)}")
    if successful_results:
        print(f"Total sequences: {sum(r['num_sequences'] for r in successful_results)}")
    print(f"Summary log: {summary_log_path}")
    print(f"Results directory: {results_dir}")
    print(f"Duration: {end_time - start_time}")
    
    return {
        'mode': 'separate',
        'files_processed': len(all_results),
        'successful_files': len(successful_results),
        'failed_files': len(failed_results),
        'total_sequences': sum(r['num_sequences'] for r in successful_results) if successful_results else 0,
        'results': all_results,
        'summary_log': summary_log_path,
        'results_dir': results_dir,
        'duration': end_time - start_time
    }

def run(cfg):
    """Main entry point for phylogenetic analysis."""
    import glob
    import datetime
    
    # Get project directory from config
    project_key = 'phylo'
    project_name = cfg.get(f'{project_key}_project_directory', 'phylo')
    keep_separate = cfg.get(f'{project_key}_keepseparate', False)
    
    # Construct paths
    input_dir = os.path.join('inputs', project_key, project_name)
    results_dir = os.path.join('results', project_key, project_name)
    
    print(f"Phylogenetic Analysis")
    print(f"Project: {project_name}")
    print(f"Input directory: {input_dir}")
    print(f"Results directory: {results_dir}")
    print()
    
    # Find FASTA files
    fasta_paths = sorted(glob.glob(os.path.join(input_dir, '*.fasta')))
    
    if not fasta_paths:
        print(f"Error: No FASTA files found in '{input_dir}'.")
        print(f"Please ensure your FASTA files are in: {input_dir}")
        return
    
    print(f"Found {len(fasta_paths)} FASTA file(s)")
    
    start_time = datetime.datetime.now()
    
    if keep_separate:
        print(f"Processing {len(fasta_paths)} FASTA files separately...")
        return run_separate_mode(fasta_paths, project_name, results_dir, start_time)
    else:
        print(f"Processing {len(fasta_paths)} FASTA files in merged mode...")
        return run_merged_mode(fasta_paths, project_name, results_dir, start_time) 