# UHT-Discovery: a workspace for pLM-clust

This codebase is designed for semi-automated protein discovery, using BLAST tools for sequence collection, quality-control filtering, clustering using language models and in silico candidate selection. It is built around the plm-clust pipeline for enzyme discovery. See the preprint for more details.

## Installation

### From PyPI

```bash
pip install uht-discovery
```

## Quick Start

### Interactive GUI (Recommended)

Launch the interactive web interface:

```bash
uht-gui
```

Or as a Python module:

```bash
python -m uht_discovery.gui
```

The GUI will open in your browser at `http://127.0.0.1:7860` and provides:
- **BLASTER**: Interactive BLAST sequence search with progress tracking
- **TRIM**: Visual length distribution and quality control
- **PLMCLUSTV2**: Interactive clustering with t-SNE/UMAP visualizations

### Command-Line Interface (CLI)

All tools are available as command-line utilities:

#### BLAST Sequence Search
```bash
uht-blast --project my_project --email your@email.com --hits 500
```

#### Sequence Trimming
```bash
uht-trim --project my_project --min-length 100 --max-length 500
```

#### Protein Clustering (PLMCLUSTV2 - Recommended)
```bash
uht-clust --project my_project --clusters 6
```

#### Legacy Clustering (PLMCLUST v1)
```bash
uht-clust-v1 --project my_project --clusters auto
```

#### Other Tools
```bash
uht-optimizer --project my_project
uht-mutation --project my_project
uht-comprehensive --project my_project
uht-biophysical --project my_project
uht-sequence --project my_project
uht-phylo --project my_project
uht-tsne --project my_project
uht-kmeans --project my_project
```

For detailed help on any command:
```bash
uht-blast --help
uht-trim --help
uht-clust --help
# etc.
```

### Unified CLI Entry Point

You can also use the main entry point:

```bash
uht-discovery [command] [options]
```

Available commands: `blast`, `trim`, `clust`, `clust-v1`, `optimizer`, `mutation`, `comprehensive`, `biophysical`, `sequence`, `phylo`, `tsne`, `kmeans`, `gui`

## General Structure

This code is set up so that configs and data are found in `inputs/.../`, where `...` depends on the script that you care to run. Likewise, results are saved to `results/.../`

The currently available commands are: 
	
- `uht-blast` / `uht-discovery blast` - BLAST sequence search
- `uht-trim` / `uht-discovery trim` - Sequence quality control
- `uht-clust` / `uht-discovery clust` - PLMCLUSTV2 clustering (recommended)
- `uht-clust-v1` / `uht-discovery clust-v1` - Legacy PLMCLUST clustering
- `uht-optimizer` / `uht-discovery optimizer` - Mutation optimization
- `uht-mutation` / `uht-discovery mutation` - Mutation testing
- `uht-comprehensive` / `uht-discovery comprehensive` - Comprehensive benchmarking
- `uht-biophysical` / `uht-discovery biophysical` - Biophysical signals analysis
- `uht-sequence` / `uht-discovery sequence` - Sequence similarity analysis
- `uht-phylo` / `uht-discovery phylo` - Phylogenetic analysis
- `uht-tsne` / `uht-discovery tsne` - t-SNE visualization
- `uht-kmeans` / `uht-discovery kmeans` - K-means benchmarking
- `uht-gui` / `uht-discovery gui` - Launch interactive GUI

-----------------------------------------------------

### blaster

Retrieve sequences using NCBI's API

Very simply, place one or more .fasta sequences in inputs/blaster/PROJECT/

Where PROJECT is the name of your project. These sequences can be one, or multiple entries and/or fasta files. 

You have several parameters to play with in config.yaml: 

blaster_project_directory: PROJECT <- This is the name of the PROJECT to focus on. This allows you to hold multiple projects in inputs/ without BLASTing all of them. 

blaster_num_hits: 500 <- Number of sequences to retrieve from NCBI

blaster_blast_db: nr <- database to search

blaster_evalue: 1e-5 <- e value cutoff

blaster_email: example@example.ac.uk <- your email (required to access NCBI's API)

You may then run using the CLI:

	uht-blast --project PROJECT --email your@email.com

The results will be saved in /results/blaster/PROJECT/... and they will be both the fasta file of hits, with the queries at the top of the list, and a BLAST report .txt file for traceability.

Hits are automatically de-duplicated.

-----------------------------------------------------

### trim_blaster

Perform basic (but important) quality control on the outputs of blaster. 

After placing the BLASTer output (or indeed, any .fasta file), in `inputs/trim/PROJECT/` where PROJECT is defined with `trim_project_directory:` in the config, simply run:

	uht-trim --project PROJECT --min-length 100 --max-length 500

You will be presented with a histogram of gene lengths with the length of the top member of the .fasta (your first input sequence) indicated with a red line. Use this to select a sensible length cutoff range, which you then enter into the terminal after closing the plot. A trimmed output will be saved in results/trim_blaster/PROJECT/, with all non-amino acid entries (e.g. X) removed as well as any sequence failing the length criteria. A detailed report of the process and your selected thresholds will also be saved. 

-----------------------------------------------------

### plm-clust

Cluster and rank the metagenome using ESM2

Place your .fasta files in inputs/PROJECT/...

Where you can name PROJECT anything you like. Specify the name PROJECT in plmclust_target_directory: PROJECT_NAME in config.yaml. 

You can also set the number of clusters (plmclust_cluster_number) to any integer, or 'auto', which will automatically find an optimal number of clusters using silhouette scoring.

The perplexity scores contain a degree of randomness due to the random masking procedure - to account for this, you can set a number of replicates for this process, defined by plm_clust_replicates. You can set this to 0 if you are only interested in clustering and not scoring. If you elect to plm_clust_replicates >=3, you will also receive a standard deviation for the perplexity scores for each sequence. 

Then, you can simply run using the CLI:

	uht-clust-v1 --project PROJECT_NAME --clusters auto

Results will be found in /results/PROJECT/

These include a sub-directory containing a fasta file of each of the clusters, a .csv file pLM-clust_sequences_with_metrics_PROJECT.csv containing sequences, cluster identities, perplexities, and standard deviations.

The silhouette search will also be saved, along with coordinates to replicate the tSNE as a .csv file. 

The top representative from each cluster is saved as top_cluster_representatives_PROJECT.fasta

-----------------------------------------------------

### plmclustv2

An improved version of plm-clust that uses single-pass scoring instead of masking-based scoring for better efficiency and consistency.

#### Key Improvements
- **Single-pass scoring**: Uses direct NLL computation instead of random masking
- **Efficient execution**: Computes embeddings and scores in one model pass
- **Consistent results**: No randomness from masking procedures
- **Same interface**: Maintains compatibility with plmclust v1

#### Setup
Place your .fasta files in `inputs/plmclustv2/PROJECT/...` where PROJECT is your project name.

Configure in `config.yaml`:
```yaml
plmclustv2_project_directory: PROJECT_NAME
plmclustv2_cluster_number: 6  # or 'auto' for automatic selection
```

#### Usage

**Using CLI (recommended):**
```bash
uht-clust --project PROJECT_NAME --clusters 6
```

#### Outputs
Results are saved in `results/plmclustv2/PROJECT/`:
- `pLM-clustv2_sequences_with_metrics_PROJECT.csv`: Sequences with cluster assignments and NLL scores
- `top_cluster_representatives_PROJECT.fasta`: Best representative from each cluster
- `tsne_coordinates_PROJECT.csv`: t-SNE coordinates for visualization
- `tsne_clusters_PROJECT.png`: t-SNE visualization plot
- `6_clusters_PROJECT/`: Individual cluster FASTA files
- `run_log_PROJECT.txt`: Detailed run log

#### Scoring Method
Unlike plmclust v1 which uses random masking, plmclustv2:
1. Computes embeddings and scores in a single model pass
2. Uses direct negative log-likelihood (NLL) scoring
3. Provides consistent, non-random results
4. Is significantly faster than the masking approach

#### When to Use
- **Use plmclustv2** for: Faster execution, consistent results, single-pass efficiency
- **Use plmclust v1** for: Legacy compatibility, masking-based scoring if specifically needed

-----------------------------------------------------

### optimizer

Leverage the outputs of plm-clust to probe a local fitness landscape, predicting mutants that will be improving when tested against many backgrounds in the cluster.

Optimise works by taking a .fasta file, then assessing each member for its average NLL according to ESM2. Taking the best sequence, we then build an MSA using ClustalO, and identify all single mutants present in the cluster relative to the reference. We then evaluate each single mutant in the context of a large number of homologues, taking the average effect of the mutation in the backgrounds as the fitness of the mutation. This is compared against the predicted effect of the mutation in the reference background. Improving mutations are then combined, and tested in the same way, up to a max_order. 

Simply place a .fasta file in /inputs/optimizer/PROJECT/ and state the PROJECT in optimizer_project_directory. 

Also set the max_sequences_to_de_denoise as the number of randomly-selected homologues to test each mutation in - a higher number will lead to better performance but slower speed. If you care about a specific reference sequence and don't want it auto-detected, set selected_sequence: to the fasta header of your sequence of interest. 

Then run 

	./run.py optimizer

-----------------------------------------------------

### comprehensive_clustering

Perform comprehensive analysis of clustering results using PCA visualization and statistical comparison.

This module analyzes clustering results by comparing ESM2+kmeans clustering with MMseqs2 clustering, providing detailed visualizations and statistical insights into protein properties and clustering quality.

#### Setup
Place your cluster FASTA files in `inputs/comprehensive_clustering/PROJECT/clusters/` where each file is named `cluster_X_of_Y_PROJECT.fasta` (e.g., `cluster_0_of_6_bsgh11.fasta`).

Configure the project in `config.yaml`:
```yaml
comprehensive_clustering_project_directory: PROJECT_NAME
```

#### Usage
```bash
./run.py comprehensive_clustering
```

#### Outputs
The analysis generates comprehensive outputs in `results/comprehensive_clustering/PROJECT/`:

**Figures:**
- `figures/pca_plots/`: PCA visualizations comparing clustering methods
- `figures/violin_plots/`: Distribution analysis for 16 protein properties by cluster
- `figures/summary_plots/`: Summary comparison plots

**Data:**
- `data/pca_results.csv`: PCA coordinates and cluster assignments

**Reports:**
- `reports/comprehensive_analysis_report.md`: Detailed analysis report

#### Analysis Components
1. **PCA Analysis**: Dimensionality reduction using 16 protein properties
2. **Cluster-Specific Violin Plots**: Distribution analysis for each metric by cluster
3. **Feature Importance**: Understanding which properties drive clustering
4. **Statistical Comparison**: Quantitative comparison of clustering methods
5. **PCA-Clustering Agreement**: Analysis of how well each method aligns with PCA structure

#### Key Metrics Analyzed
- Protein length, molecular weight, GRAVY score, isoelectric point
- Secondary structure content (helix, sheet, turn fractions)
- Amino acid composition patterns (hydrophobic, hydrophilic, charged, etc.)
- Charge at pH 7

#### Example Results
The analysis provides insights such as:
- Which clustering method better aligns with protein property structure
- Cluster-specific property distributions
- Feature importance in driving clustering decisions
- Statistical evidence of clustering quality differences

-----------------------------------------------------

### mask-free-nllvsperplexity

This is a member of the *_vsperplexity suite, designed to test the method chosen for estimating perplexity in the plm-cluster method.

The other metric calculated here, mask-free-nll, runs a single-pass of the sequence through the model, and extracts the negative log liklihoods of each token, reporting the average.

This is compared against the 'perplexity' metric used by plm-clust, which masks 15% of the sequence at random and calculates the average NLL of the masked sequences. This process is repeated N times and the outputs averaged per sequence. 

The output is a grid, with increasing replicates of masking from top to bottom and left to right, with the diagonal carrying the comparison to the mask-free-nll of each number of replicates. The numbers in the boxes represent the pearson R.

After setting up plm-clust inputs as normal, run 

	make mask-free-nllvsperplexity

-----------------------------------------------------

### saturationvsperplexity

This is a member of the *_vsperplexity suite, designed to test the method chosen for estimating perplexity in the plm-cluster method.

The other metric calculated here, 'saturation', is the canonical way of calculating pseudo-NLL, carried out by masking each token sequentially and calculating the average NLL over each mask. 

After setting up plm-clust inputs as normal, run 

	make saturationvsperplexity

-----------------------------------------------------

### singleinferencevsperplexity

This is a member of the *_vsperplexity suite, designed to test the method chosen for estimating perplexity in the plm-cluster method.

The other metric calculated here, 'singleinference', is a sinlge-pass method developed by Gordon et al. that is designed to account explicitly for biases in the training process when extracting log likehoods. 

After setting up plm-clust inputs as normal, run 

	make singleinferencevsperplexity

---

## Biophysical Signals Analysis

Analyze biophysical signals that drive protein clustering to understand what factors influence clustering decisions.

### Features
- **25 biophysical signals** tested across 6 categories
- **Statistical rigor** with ANOVA, effect sizes, and multiple validation metrics
- **Publication-quality visualizations** (30+ figures generated)
- **Modular design** for easy addition of new signals
- **Integration** with uht-discovery project conventions

### Key Findings
- **Primary discovery**: The clustering primarily captures evolutionary relationships rather than functional characteristics
- **Top signals**: N-glycosylation sites (η² = 0.659), signal peptide presence (η² = 0.635), isoelectric point (η² = 0.620)
- **Charge properties** are the strongest drivers (η² = 0.620 average)

### Usage

#### 1. Prepare input data
Place your cluster FASTA files in `inputs/biophysical_signals/clusters/`:
```
inputs/biophysical_signals/
└── clusters/
    ├── cluster_0_of_6_bsgh11.fasta
    ├── cluster_1_of_6_bsgh11.fasta
    ├── cluster_2_of_6_bsgh11.fasta
    ├── cluster_3_of_6_bsgh11.fasta
    ├── cluster_4_of_6_bsgh11.fasta
    └── cluster_5_of_6_bsgh11.fasta
```

#### 2. Run analysis
```bash
python run.py biophysical_signals
```

#### 3. View results
Results are saved to `results/biophysical_signals/`:
- **Reports**: `reports/biophysical_signals_report.md`
- **Figures**: `figures/biophysical_plots/`, `figures/statistical_plots/`, etc.
- **Data**: `data/` (processed data files)

### Configuration
Configure in `config.yaml`:
```yaml
### biophysical_signals ###
biophysical_signals_project_directory: inputs/biophysical_signals/clusters
```

Or use environment variables:
```bash
export BIOPHYSICAL_SIGNALS_PROJECT_ID=/path/to/your/clusters
python run.py biophysical_signals
```

### Adding New Signals
1. Create a new signal class inheriting from `BiophysicalSignal`
2. Implement the `calculate` method
3. Add to the framework in `core/biophysical_signals_analysis.py`
4. Run analysis: `python run.py biophysical_signals`

For detailed documentation, see `BIOPHYSICAL_SIGNALS_README.md`.

---

## Sequence Classifier Module (iteration0classifier)

This module provides a fast, CNN+attention-based classifier for protein sequences, allowing rapid assignment of new sequences to clusters based on primary sequence alone. It is designed for high-throughput screening and is much faster than ESM2+clustering.

### Features
- Input: Primary sequence (padded/truncated to 1024, with start/end tokens)
- Output: Cluster assignment + confidence score (softmax probability)
- Special "unrelated" class populated by random sequences
- QC: Removes non-amino-acid characters, truncates to 1024
- Professional-grade: Publication-ready metrics, plots, and robust code
- Dummy data/test script included

### Directory Structure
```
training/iteration0classifier/
    dummy_training_data.csv      # Example training data
    dummy_headers.txt           # Example headers file
    dummy_test_sequences.fasta  # Example FASTA for prediction
    sequence_classifier.pth     # Trained model
    sequence_classifier_metadata.pkl # Model metadata
    evaluation_results.json     # Metrics/results
    training_history.png        # Training/validation loss/accuracy
    confusion_matrix.png        # Confusion matrix
    predictions.csv             # Predictions on new FASTA
```

### Input Formats
- **Training CSV**: Must have columns `sequence` and `cluster`, plus any experimental columns (optional)
- **Headers file**: List of experimental column names (one per line)
- **FASTA**: For prediction, standard FASTA format

### Usage

#### 1. Train the classifier
```bash
python -c "from core.classifier import run_classifier_training; run_classifier_training('training/iteration0classifier/dummy_training_data.csv', 'training/iteration0classifier/dummy_headers.txt')"
```

#### 2. Predict on new sequences
```bash
python -c "from core.classifier import predict_from_fasta; predict_from_fasta('training/iteration0classifier/dummy_test_sequences.fasta')"
```

#### 3. Run the test suite (dummy data)
```bash
python test_classifier.py
```

### Notes
- The model is a 1D CNN with attention, trained with early stopping and cross-validation.
- The "unrelated" class is generated automatically from random sequences.
- All results and plots are saved in `training/iteration0classifier/`.
- For real data, place your CSV and headers file in the same directory and follow the same commands.

---

## Phylogenetic Analysis

Perform comprehensive phylogenetic analysis comparing evolutionary relationships with protein language model embeddings.

### Features
- **Multiple sequence alignment** using MAFFT
- **Phylogenetic tree construction** with distance matrix computation
- **ESM2 embedding analysis** with cosine and dot product similarities
- **Correlation analysis** between phylogenetic and embedding distances
- **Independent processing** of multiple FASTA files with `keepseparate` mode

### Usage

#### Setup
Place your FASTA files in `inputs/phylo/PROJECT/`:
```
inputs/phylo/cazy/
├── GH16_18_sequences_trimmed.fasta
├── GH43_19_sequences_trimmed.fasta
└── GH47_sequences_trimmed.fasta
```

#### Configuration
Configure in `config.yaml`:
```yaml
### phylo ###
phylo_project_directory: cazy
phylo_keepseparate: true  # Process each FASTA independently
```

#### Run Analysis
```bash
./run.py phylo
```

#### Outputs
Results saved in `results/phylo/PROJECT/`:

**Separate mode** (when `phylo_keepseparate: true`):
- Individual directories for each FASTA file
- `summary_log_PROJECT.txt` with correlation metrics for all files
- Per-file phylogenetic trees, distance matrices, and visualizations

**Merged mode** (when `phylo_keepseparate: false`):
- Single analysis combining all FASTA files
- Unified phylogenetic tree and analysis

### Key Metrics
- **Pearson correlation** between phylogenetic and embedding distances
- **R-squared values** for correlation strength
- **Spearman correlation** for non-linear relationships
- **P-values** for statistical significance
- **Sample sizes** for each comparison

---

## Sequence Similarity Analysis

Comprehensive analysis of sequence similarity patterns using multiple metrics and visualization approaches.

### Features
- **Multiple similarity metrics**: Identity, BLOSUM62, PAM250, and more
- **Statistical analysis**: Distribution analysis and clustering evaluation
- **Heatmap visualizations** for similarity matrices
- **Unit-based processing** for organized analysis of multiple sequence groups

### Usage

#### Setup
Place your FASTA files in unit directories under `inputs/sequence_similarity/PROJECT/`:
```
inputs/sequence_similarity/cazy/
├── 10_clusters_GH16_18_sequences_trimmed/
│   ├── cluster_0.fasta
│   └── cluster_1.fasta
└── 8_clusters_GH90_sequences_trimmed/
    ├── cluster_0.fasta
    └── cluster_1.fasta
```

#### Configuration
```yaml
### sequence_similarity ###
sequence_similarity_project_directory: cazy
```

#### Run Analysis
```bash
./run.py sequence_similarity
```

#### Outputs
Results in `results/sequence_similarity/PROJECT/`:
- Individual unit directories with similarity matrices
- Comprehensive heatmaps and distribution plots
- Statistical summaries and CSV data files
- Summary log with per-unit results

---

## K-means Benchmarking

Rigorous assessment of k-means clustering reproducibility with statistical controls and algorithm comparisons.

### Features
- **Reproducibility assessment** across multiple k values and runs
- **Statistical controls**: Random permutation and random data baselines
- **Algorithm comparison**: K-means vs Spectral clustering
- **Publication-ready visualizations** with proper 0-1 scaling
- **Independent processing** with `keepseparate` mode

### Usage

#### Setup
Place FASTA files in `inputs/kmeansbenchmark/PROJECT/`:
```
inputs/kmeansbenchmark/cazy/
├── GH16_18_sequences_trimmed.fasta
├── GH43_19_sequences_trimmed.fasta
└── GH47_sequences_trimmed.fasta
```

#### Configuration
```yaml
### kmeansbenchmark ###
kmeansbenchmark_project_directory: cazy
kmeansbenchmark_k_range: [2, 10]
kmeansbenchmark_n_runs: 10
kmeansbenchmark_keepseparate: true  # Process each FASTA independently
kmeansbenchmark_run_controls: true
kmeansbenchmark_compare_algorithms: true
```

#### Run Analysis
```bash
./run.py kmeansbenchmark
```

#### Outputs
Results in `results/kmeansbenchmark/PROJECT/`:

**Per FASTA file** (when `keepseparate: true`):
- Stability metrics and reproducibility heatmaps
- Algorithm comparison plots (K-means vs Spectral)
- Control experiment results
- Comprehensive analysis reports

**Key Visualizations**:
- **Stability plots**: ARI/NMI stability across k values (0-1 scaled)
- **Algorithm comparison**: Performance comparison excluding deterministic hierarchical
- **Control baselines**: Random permutation and random data controls
- **Reproducibility heatmaps**: Pairwise clustering agreement matrices

### Scientific Rigor
- **Fair controls**: Random permutation control uses different permutations per replicate
- **Statistical validation**: Multiple metrics (ARI, NMI, Jaccard) with significance testing
- **Reproducible results**: Seeded random number generation for consistent results
- **Publication quality**: Professional visualizations with proper scaling and clean layouts

---

## Enhanced Module Features

### Universal `keepseparate` Functionality
Multiple modules now support independent processing of FASTA files:

- **plmclustv2**: Process each FASTA file separately with individual clustering results
- **phylogenetic_analysis**: Independent phylogenetic analysis per FASTA file
- **kmeansbenchmark**: Separate reproducibility assessment for each FASTA file
- **biophysical_signals**: Unit-based analysis with aggregated feature importance
- **sequence_similarity**: Unit-based similarity analysis

### Auto-trimming in Trim Module
The trim module now supports automatic length threshold selection:

```yaml
trim_project_directory: cazy
auto_mode: true  # Automatically determine length thresholds
```

**Auto-trimming logic**:
1. Finds most common sequence length (or average if tied)
2. Calculates standard deviation of lengths
3. Sets thresholds as reference_length ± 1 standard deviation
4. Provides detailed reporting of the automatic selection process

### Enhanced Biophysical Signals
- **Aggregated feature importance** plots across all processed units
- **Skip violin plots** option for faster execution
- **Error bar visualization** showing feature importance variability
- **CSV export** of aggregated results for further analysis

---
