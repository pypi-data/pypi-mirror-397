#!/usr/bin/env python3
"""
Biophysical Signals Analysis
Core module for analyzing biophysical signals that drive protein clustering
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from collections import defaultdict, Counter
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from scipy.stats import f_oneway, kruskal, chi2_contingency, pearsonr, spearmanr, mannwhitneyu
from scipy.spatial.distance import pdist, squareform
from tqdm import tqdm
import warnings
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

class BiophysicalSignal:
    """Base class for biophysical signals."""
    
    def __init__(self, name, description, category):
        self.name = name
        self.description = description
        self.category = category
    
    def calculate(self, sequence):
        """Calculate the signal value for a given sequence."""
        raise NotImplementedError("Subclasses must implement calculate method")

class LengthSignal(BiophysicalSignal):
    """Protein length signal."""
    
    def __init__(self):
        super().__init__("length", "Protein sequence length", "basic_properties")
    
    def calculate(self, sequence):
        return len(sequence)

class MolecularWeightSignal(BiophysicalSignal):
    """Molecular weight signal."""
    
    def __init__(self):
        super().__init__("molecular_weight", "Protein molecular weight", "basic_properties")
    
    def calculate(self, sequence):
        try:
            analysis = ProteinAnalysis(sequence)
            return analysis.molecular_weight()
        except:
            return None

class IsoelectricPointSignal(BiophysicalSignal):
    """Isoelectric point signal."""
    
    def __init__(self):
        super().__init__("isoelectric_point", "Protein isoelectric point", "charge_properties")
    
    def calculate(self, sequence):
        try:
            analysis = ProteinAnalysis(sequence)
            return analysis.isoelectric_point()
        except:
            return None

class ChargeAtpH7Signal(BiophysicalSignal):
    """Charge at pH 7 signal."""
    
    def __init__(self):
        super().__init__("charge_at_pH7", "Protein charge at pH 7", "charge_properties")
    
    def calculate(self, sequence):
        try:
            analysis = ProteinAnalysis(sequence)
            return analysis.charge_at_pH(7.0)
        except:
            return None

class GRAVYSignal(BiophysicalSignal):
    """GRAVY (Grand Average of Hydropathy) signal."""
    
    def __init__(self):
        super().__init__("gravy", "Grand Average of Hydropathy", "thermodynamic_properties")
    
    def calculate(self, sequence):
        try:
            analysis = ProteinAnalysis(sequence)
            return analysis.gravy()
        except:
            return None

class AromaticitySignal(BiophysicalSignal):
    """Aromaticity signal."""
    
    def __init__(self):
        super().__init__("aromaticity", "Protein aromaticity", "thermodynamic_properties")
    
    def calculate(self, sequence):
        try:
            analysis = ProteinAnalysis(sequence)
            return analysis.aromaticity()
        except:
            return None

class HelixFractionSignal(BiophysicalSignal):
    """Alpha helix fraction signal."""
    
    def __init__(self):
        super().__init__("helix_fraction", "Alpha helix fraction", "structural_properties")
    
    def calculate(self, sequence):
        try:
            analysis = ProteinAnalysis(sequence)
            return analysis.secondary_structure_fraction()[0]
        except:
            return None

class SheetFractionSignal(BiophysicalSignal):
    """Beta sheet fraction signal."""
    
    def __init__(self):
        super().__init__("sheet_fraction", "Beta sheet fraction", "structural_properties")
    
    def calculate(self, sequence):
        try:
            analysis = ProteinAnalysis(sequence)
            return analysis.secondary_structure_fraction()[2]
        except:
            return None

class TurnFractionSignal(BiophysicalSignal):
    """Beta turn fraction signal."""
    
    def __init__(self):
        super().__init__("turn_fraction", "Beta turn fraction", "structural_properties")
    
    def calculate(self, sequence):
        try:
            analysis = ProteinAnalysis(sequence)
            return analysis.secondary_structure_fraction()[1]
        except:
            return None

class FlexibilitySignal(BiophysicalSignal):
    """Protein flexibility signal."""
    
    def __init__(self):
        super().__init__("flexibility", "Protein flexibility", "structural_properties")
    
    def calculate(self, sequence):
        try:
            analysis = ProteinAnalysis(sequence)
            return np.mean(analysis.flexibility())
        except:
            return None

class InstabilityIndexSignal(BiophysicalSignal):
    """Instability index signal."""
    
    def __init__(self):
        super().__init__("instability_index", "Protein instability index", "thermodynamic_properties")
    
    def calculate(self, sequence):
        try:
            analysis = ProteinAnalysis(sequence)
            return analysis.instability_index()
        except:
            return None

class HydrophobicAASignal(BiophysicalSignal):
    """Hydrophobic amino acid ratio signal."""
    
    def __init__(self):
        super().__init__("hydrophobic_aa", "Hydrophobic amino acid ratio", "amino_acid_composition")
    
    def calculate(self, sequence):
        hydrophobic_aas = 'ACFILMPVWY'
        hydrophobic_count = sum(1 for aa in sequence if aa in hydrophobic_aas)
        return hydrophobic_count / len(sequence)

class HydrophilicAASignal(BiophysicalSignal):
    """Hydrophilic amino acid ratio signal."""
    
    def __init__(self):
        super().__init__("hydrophilic_aa", "Hydrophilic amino acid ratio", "amino_acid_composition")
    
    def calculate(self, sequence):
        hydrophilic_aas = 'DEHKNQRST'
        hydrophilic_count = sum(1 for aa in sequence if aa in hydrophilic_aas)
        return hydrophilic_count / len(sequence)

class ChargedAASignal(BiophysicalSignal):
    """Charged amino acid ratio signal."""
    
    def __init__(self):
        super().__init__("charged_aa", "Charged amino acid ratio", "amino_acid_composition")
    
    def calculate(self, sequence):
        charged_aas = 'DEHKR'
        charged_count = sum(1 for aa in sequence if aa in charged_aas)
        return charged_count / len(sequence)

class AcidicAASignal(BiophysicalSignal):
    """Acidic amino acid ratio signal."""
    
    def __init__(self):
        super().__init__("acidic_aa", "Acidic amino acid ratio", "charge_properties")
    
    def calculate(self, sequence):
        acidic_aas = 'DE'
        acidic_count = sum(1 for aa in sequence if aa in acidic_aas)
        return acidic_count / len(sequence)

class BasicAASignal(BiophysicalSignal):
    """Basic amino acid ratio signal."""
    
    def __init__(self):
        super().__init__("basic_aa", "Basic amino acid ratio", "charge_properties")
    
    def calculate(self, sequence):
        basic_aas = 'HKR'
        basic_count = sum(1 for aa in sequence if aa in basic_aas)
        return basic_count / len(sequence)

class GlycineRatioSignal(BiophysicalSignal):
    """Glycine ratio signal."""
    
    def __init__(self):
        super().__init__("glycine_ratio", "Glycine ratio", "amino_acid_composition")
    
    def calculate(self, sequence):
        glycine_count = sequence.count('G')
        return glycine_count / len(sequence)

class ProlineRatioSignal(BiophysicalSignal):
    """Proline ratio signal."""
    
    def __init__(self):
        super().__init__("proline_ratio", "Proline ratio", "amino_acid_composition")
    
    def calculate(self, sequence):
        proline_count = sequence.count('P')
        return proline_count / len(sequence)

class CysteineRatioSignal(BiophysicalSignal):
    """Cysteine ratio signal."""
    
    def __init__(self):
        super().__init__("cysteine_ratio", "Cysteine ratio", "amino_acid_composition")
    
    def calculate(self, sequence):
        cysteine_count = sequence.count('C')
        return cysteine_count / len(sequence)

class SignalPeptideSignal(BiophysicalSignal):
    """Signal peptide prediction using SignalP 6.0."""
    
    def __init__(self):
        super().__init__("signal_peptide_score", "Signal peptide probability", "sequence_patterns")
        
        # Check if SignalP is available
        self.signalp_available = self._check_signalp()
        self._signalp_cache = {}  # Cache results
        
        if not self.signalp_available:
            print("  SignalP not found - using fallback heuristic method")
            print("   For better accuracy, install SignalP 6.0:")
            print("   https://services.healthtech.dtu.dk/services/SignalP-6.0/")
            
            # Fallback heuristic properties
            self.hydrophobic = set('AILMFVWP')
            self.positive = set('KR')
            self.negative = set('DE')
    
    def _check_signalp(self):
        """Check if SignalP is available."""
        import shutil
        return shutil.which('signalp6') is not None or shutil.which('signalp') is not None
    
    def calculate(self, sequence):
        """
        Predict signal peptide using SignalP if available,
        otherwise use heuristic method.
        """
        if self.signalp_available:
            return self._calculate_signalp(sequence)
        else:
            return self._calculate_heuristic(sequence)
    
    def _calculate_signalp(self, sequence):
        """Use real SignalP for prediction (called per-sequence)."""
        # Check cache first
        if sequence in self._signalp_cache:
            return self._signalp_cache[sequence]
        
        import tempfile
        import subprocess
        import os
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as fasta_f:
                fasta_file = fasta_f.name
                fasta_f.write(f">temp_seq\n{sequence}\n")
            
            temp_dir = tempfile.mkdtemp()
            
            # Run SignalP
            cmd = ['signalp6' if shutil.which('signalp6') else 'signalp',
                   '--fastafile', fasta_file,
                   '--output_dir', temp_dir,
                   '--format', 'none',  # Only text output
                   '--organism', 'eukarya',  # Can be made configurable
                   '--mode', 'fast']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Parse output
            output_file = os.path.join(temp_dir, 'prediction_results.txt')
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    for line in f:
                        if line.startswith('temp_seq'):
                            # Parse SignalP output format
                            # Format: ID Prediction Probability ...
                            parts = line.strip().split('\t')
                            if len(parts) >= 3:
                                prediction = parts[1]  # SP or NO_SP
                                if prediction == 'SP':
                                    # Extract probability if available
                                    try:
                                        prob = float(parts[2])
                                        score = prob
                                    except:
                                        score = 1.0  # High confidence if SP predicted
                                else:
                                    score = 0.0
                                
                                # Cache and return
                                self._signalp_cache[sequence] = score
                                return score
            
            # Cleanup
            os.unlink(fasta_file)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # If parsing failed, return 0
            return 0.0
            
        except Exception as e:
            # If SignalP fails, fall back to heuristic
            print(f"  SignalP failed: {e}, using heuristic")
            return self._calculate_heuristic(sequence)
    
    def _calculate_heuristic(self, sequence):
        """
        Fallback heuristic method (simplified version of previous implementation).
        Returns score 0.0-1.0 based on signal peptide characteristics.
        """
        if len(sequence) < 20:
            return 0.0
        
        score = 0.0
        
        # N-region positive charge
        n_region = sequence[0:5]
        net_charge = sum(1 for aa in n_region if aa in self.positive) - \
                    sum(1 for aa in n_region if aa in self.negative)
        if net_charge > 0:
            score += 0.25
        
        # H-region hydrophobic core
        h_region = sequence[5:min(20, len(sequence))]
        hydrophobic_frac = sum(1 for aa in h_region if aa in self.hydrophobic) / len(h_region)
        if hydrophobic_frac > 0.6:
            score += 0.4
        elif hydrophobic_frac > 0.4:
            score += 0.2
        
        # C-region cleavage site
        if len(sequence) >= 25:
            c_region = sequence[15:25]
            small_polar = sum(1 for aa in c_region if aa in 'AGSC')
            if small_polar >= 3:
                score += 0.25
        
        # Canonical start
        if sequence[0] == 'M':
            score += 0.1
        
        return min(score, 1.0)

class NTerminalChargeSignal(BiophysicalSignal):
    """N-terminal charge signal."""
    
    def __init__(self):
        super().__init__("n_terminal_charge", "N-terminal charge", "sequence_patterns")
    
    def calculate(self, sequence, length=20):
        n_term = sequence[:min(length, len(sequence))]
        charge = 0
        for aa in n_term:
            if aa in 'DE':
                charge -= 1
            elif aa in 'HKR':
                charge += 1
        return charge

class CTerminalChargeSignal(BiophysicalSignal):
    """C-terminal charge signal."""
    
    def __init__(self):
        super().__init__("c_terminal_charge", "C-terminal charge", "sequence_patterns")
    
    def calculate(self, sequence, length=20):
        c_term = sequence[-min(length, len(sequence)):]
        charge = 0
        for aa in c_term:
            if aa in 'DE':
                charge -= 1
            elif aa in 'HKR':
                charge += 1
        return charge

class GlycosylationSitesSignal(BiophysicalSignal):
    """N-glycosylation sites signal."""
    
    def __init__(self):
        super().__init__("glycosylation_sites", "N-glycosylation sites", "sequence_patterns")
    
    def calculate(self, sequence):
        return len(re.findall(r'N[^P][ST]', sequence))

class PhosphorylationSitesSignal(BiophysicalSignal):
    """Phosphorylation sites prediction using kinase consensus motifs."""
    
    def __init__(self):
        super().__init__("phosphorylation_sites", "Predicted phosphorylation sites", "sequence_patterns")
        
        # Well-established kinase consensus motifs from literature
        # Format: (pattern, description)
        self.motifs = [
            # PKA (Protein Kinase A): R-R/K-X-S/T (basophilic)
            (r'[RK][RK].([ST])', 'PKA'),
            # PKC (Protein Kinase C): S/T-X-R/K (basophilic)
            (r'([ST]).[RK]', 'PKC'),
            # CK2 (Casein Kinase 2): S/T-X-X-D/E (acidophilic)
            (r'([ST])..[DE]', 'CK2'),
            # CDK (Cyclin-Dependent Kinase): S/T-P (proline-directed)
            (r'([ST])P', 'CDK'),
            # MAPK (MAP Kinase): P-X-S/T-P (proline-directed)
            (r'P.([ST])P', 'MAPK'),
            # GSK3 (Glycogen Synthase Kinase 3): S/T-X-X-X-S/T (phospho-primed)
            (r'([ST])...[ST]', 'GSK3'),
            # ATM/ATR (DNA damage kinases): S/T-Q
            (r'([ST])Q', 'ATM_ATR'),
            # Tyrosine kinases: Y in various contexts
            # Src family: acidic residues nearby
            (r'[DE].{0,3}(Y)', 'Tyr_acidic'),
            (r'(Y).{0,3}[DE]', 'Tyr_acidic2'),
        ]
    
    def calculate(self, sequence):
        """Count predicted phosphorylation sites based on kinase motifs."""
        sites = set()  # Use set to avoid counting same position twice
        
        for pattern, kinase_type in self.motifs:
            for match in re.finditer(pattern, sequence):
                # Get the position of the phosphorylatable residue (S/T/Y)
                for group_idx in range(1, len(match.groups()) + 1):
                    if match.group(group_idx):
                        sites.add(match.start(group_idx))
        
        return len(sites)

def create_output_directories(results_dir):
    """Create the output directory structure."""
    directories = [
        os.path.join(results_dir, 'figures', 'biophysical_plots'),
        os.path.join(results_dir, 'figures', 'statistical_plots'),
        os.path.join(results_dir, 'figures', 'summary_plots'),
        os.path.join(results_dir, 'figures', 'correlation_plots'),
        os.path.join(results_dir, 'figures', 'comparison_plots'),
        os.path.join(results_dir, 'reports'),
        os.path.join(results_dir, 'data')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("Created output directory structure")

def extract_organism_info(header):
    """Extract organism name from FASTA header"""
    organism_match = re.search(r'\[([^\]]+)\]', header)
    if organism_match:
        organism = organism_match.group(1)
        genus = organism.split()[0] if organism else "Unknown"
        return genus
    return "Unknown"

class BiophysicalSignalsAnalyzer:
    """Comprehensive analyzer for biophysical signals in protein clustering."""
    
    def __init__(self, cluster_dir, results_dir, create_violin_plots=False):
        self.cluster_dir = cluster_dir
        self.results_dir = results_dir
        self.create_violin_plots = create_violin_plots
        self.proteins = []
        self.clusters = {}
        self.signals = {}
        self.statistical_results = {}
        
        # Create output directories
        create_output_directories(results_dir)
        
        # Initialize signals
        self._initialize_signals()
    
    def _initialize_signals(self):
        """Initialize all biophysical signals."""
        self.signals = {
            'length': LengthSignal(),
            'molecular_weight': MolecularWeightSignal(),
            'isoelectric_point': IsoelectricPointSignal(),
            'charge_at_pH7': ChargeAtpH7Signal(),
            'gravy': GRAVYSignal(),
            'aromaticity': AromaticitySignal(),
            'helix_fraction': HelixFractionSignal(),
            'sheet_fraction': SheetFractionSignal(),
            'turn_fraction': TurnFractionSignal(),
            'flexibility': FlexibilitySignal(),
            'instability_index': InstabilityIndexSignal(),
            'hydrophobic_aa': HydrophobicAASignal(),
            'hydrophilic_aa': HydrophilicAASignal(),
            'charged_aa': ChargedAASignal(),
            'acidic_aa': AcidicAASignal(),
            'basic_aa': BasicAASignal(),
            'glycine_ratio': GlycineRatioSignal(),
            'proline_ratio': ProlineRatioSignal(),
            'cysteine_ratio': CysteineRatioSignal(),
            'signal_peptide': SignalPeptideSignal(),
            'n_terminal_charge': NTerminalChargeSignal(),
            'c_terminal_charge': CTerminalChargeSignal(),
            'glycosylation_sites': GlycosylationSitesSignal(),
            'phosphorylation_sites': PhosphorylationSitesSignal()
        }
    
    def load_clusters(self):
        """Load protein clusters from FASTA files."""
        print("Loading protein clusters...")
        
        for filename in os.listdir(self.cluster_dir):
            if filename.endswith('.fasta'):
                cluster_name = filename.replace('.fasta', '')
                cluster_path = os.path.join(self.cluster_dir, filename)
                
                cluster_proteins = []
                for record in SeqIO.parse(cluster_path, 'fasta'):
                    protein = {
                        'id': record.id,
                        'sequence': str(record.seq),
                        'cluster': cluster_name,
                        'signals': {}
                    }
                    cluster_proteins.append(protein)
                    self.proteins.append(protein)
                
                self.clusters[cluster_name] = cluster_proteins
        
        print(f"Loaded {len(self.proteins)} proteins across {len(self.clusters)} clusters")
    
    def calculate_all_signals(self):
        """Calculate all biophysical signals for all proteins."""
        print("Calculating all biophysical signals...")
        
        for protein in tqdm(self.proteins, desc="Calculating signals"):
            for signal_name, signal in self.signals.items():
                try:
                    value = signal.calculate(protein['sequence'])
                    protein['signals'][signal_name] = value
                except Exception as e:
                    protein['signals'][signal_name] = None
    
    def run_statistical_analysis(self):
        """Run statistical analysis on all signals with multiple hypothesis testing corrections."""
        print("Running statistical analysis with multiple hypothesis testing corrections...")
        
        # Collect all p-values for multiple testing corrections
        all_p_values = []
        signal_names = []
        
        for signal_name, signal in tqdm(self.signals.items(), desc="Analyzing signals"):
            # Extract signal values
            values = []
            valid_clusters = []
            
            for protein in self.proteins:
                if signal_name in protein.get('signals', {}) and protein['signals'][signal_name] is not None:
                    values.append(protein['signals'][signal_name])
                    valid_clusters.append(protein['cluster'])
            
            if len(values) == 0:
                continue
            
            # Run statistical tests
            results = self._run_signal_statistical_tests(values, valid_clusters, signal_name)
            self.statistical_results[signal_name] = results
            
            # Collect p-values for multiple testing corrections
            if results.get('anova', {}).get('p_value') is not None:
                all_p_values.append(results['anova']['p_value'])
                signal_names.append(signal_name)
        
        # Apply multiple hypothesis testing corrections
        if all_p_values:
            self._apply_multiple_testing_corrections(all_p_values, signal_names)
    
    def _apply_multiple_testing_corrections(self, p_values, signal_names):
        """Apply multiple hypothesis testing corrections to p-values."""
        print("Applying multiple hypothesis testing corrections...")
        
        p_values = np.array(p_values)
        n_tests = len(p_values)
        
        # Sort p-values and get indices
        sorted_indices = np.argsort(p_values)
        sorted_p_values = p_values[sorted_indices]
        
        # Bonferroni correction (Family-wise Error Rate control)
        bonferroni_p_values = np.minimum(sorted_p_values * n_tests, 1.0)
        
        # Benjamini-Hochberg correction (False Discovery Rate control)
        bh_p_values = np.zeros_like(sorted_p_values)
        for i, p_val in enumerate(sorted_p_values):
            bh_p_values[i] = min(p_val * n_tests / (i + 1), 1.0)
        
        # Apply step-down procedure for Benjamini-Hochberg
        for i in range(len(bh_p_values) - 2, -1, -1):
            bh_p_values[i] = min(bh_p_values[i], bh_p_values[i + 1])
        
        # Update statistical results with corrected p-values
        for i, original_idx in enumerate(sorted_indices):
            signal_name = signal_names[original_idx]
            if signal_name in self.statistical_results:
                self.statistical_results[signal_name]['bonferroni_p_value'] = bonferroni_p_values[i]
                self.statistical_results[signal_name]['bh_p_value'] = bh_p_values[i]
                self.statistical_results[signal_name]['bonferroni_significant'] = bonferroni_p_values[i] < 0.05
                self.statistical_results[signal_name]['bh_significant'] = bh_p_values[i] < 0.05
        
        # Print summary of corrections
        bonferroni_significant = sum(1 for p in bonferroni_p_values if p < 0.05)
        bh_significant = sum(1 for p in bh_p_values if p < 0.05)
        original_significant = sum(1 for p in p_values if p < 0.05)
        
        print(f"Multiple testing correction summary:")
        print(f"  Original significant tests (p < 0.05): {original_significant}/{n_tests}")
        print(f"  Bonferroni significant tests (p < 0.05): {bonferroni_significant}/{n_tests}")
        print(f"  Benjamini-Hochberg significant tests (FDR < 0.05): {bh_significant}/{n_tests}")
    
    def _run_signal_statistical_tests(self, values, clusters, signal_name):
        """Run statistical tests for a specific signal."""
        results = {}
        
        # Convert to numpy arrays
        values = np.array(values)
        clusters = np.array(clusters)
        
        # Get unique clusters
        unique_clusters = np.unique(clusters)
        
        if len(unique_clusters) < 2:
            return results
        
        # Group values by cluster
        cluster_values = [values[clusters == cluster] for cluster in unique_clusters]
        
        # ANOVA test
        try:
            f_stat, p_value = f_oneway(*cluster_values)
            results['anova'] = {
                'f_statistic': f_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
        except:
            results['anova'] = {'f_statistic': None, 'p_value': None, 'significant': False}
        
        # Kruskal-Wallis test (non-parametric)
        try:
            h_stat, p_value = kruskal(*cluster_values)
            results['kruskal_wallis'] = {
                'h_statistic': h_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
        except:
            results['kruskal_wallis'] = {'h_statistic': None, 'p_value': None, 'significant': False}
        
        # Effect size (eta-squared)
        try:
            grand_mean = np.mean(values)
            ss_between = sum(len(group) * (np.mean(group) - grand_mean) ** 2 for group in cluster_values)
            ss_total = sum((val - grand_mean) ** 2 for val in values)
            eta_squared = ss_between / ss_total if ss_total > 0 else 0
            results['effect_size'] = {
                'eta_squared': eta_squared,
                'interpretation': self._interpret_effect_size(eta_squared)
            }
        except:
            results['effect_size'] = {'eta_squared': None, 'interpretation': 'Unknown'}
        
        # Descriptive statistics
        results['descriptive'] = {}
        for i, cluster in enumerate(unique_clusters):
            cluster_data = cluster_values[i]
            results['descriptive'][cluster] = {
                'n': len(cluster_data),
                'mean': np.mean(cluster_data),
                'std': np.std(cluster_data),
                'median': np.median(cluster_data),
                'min': np.min(cluster_data),
                'max': np.max(cluster_data)
            }
        
        return results
    
    def _interpret_effect_size(self, eta_squared):
        """Interpret effect size based on eta-squared."""
        if eta_squared < 0.01:
            return "Negligible"
        elif eta_squared < 0.06:
            return "Small"
        elif eta_squared < 0.14:
            return "Medium"
        else:
            return "Large"
    
    def create_visualizations(self):
        """Create all visualizations."""
        print("Creating visualizations...")
        
        if self.create_violin_plots:
            self._create_violin_plots()
        else:
            print("Skipping violin plots (disabled in configuration)")
        
        self._create_statistical_summary_plots()
        self._create_correlation_heatmaps()
        self._create_signal_importance_plot()
    
    def _create_violin_plots(self):
        """Create violin plots for each signal."""
        print("Creating violin plots...")
        
        for signal_name, signal in tqdm(self.signals.items(), desc="Creating violin plots"):
            # Extract signal values
            values = []
            clusters = []
            
            for protein in self.proteins:
                if signal_name in protein.get('signals', {}) and protein['signals'][signal_name] is not None:
                    values.append(protein['signals'][signal_name])
                    clusters.append(protein['cluster'])
            
            if len(values) == 0:
                continue
            
            # Create violin plot
            plt.figure(figsize=(10, 6))
            
            # Create DataFrame for seaborn
            df = pd.DataFrame({
                'value': values,
                'cluster': clusters
            })
            
            # Create violin plot
            sns.violinplot(data=df, x='cluster', y='value', palette='husl')
            plt.title(f'{signal.description} by Cluster')
            plt.xlabel('Cluster')
            plt.ylabel(signal.description)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save plot
            plot_path = os.path.join(self.results_dir, 'figures', 'biophysical_plots', f'cluster_violin_{signal_name}.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
    
    def _create_statistical_summary_plots(self):
        """Create statistical summary plots."""
        print("Creating statistical summary plots...")
        
        # Create p-value summary plot
        p_values = []
        signal_names = []
        test_types = []
        
        for signal_name, results in self.statistical_results.items():
            if 'anova' in results and results['anova']['p_value'] is not None:
                p_values.append(results['anova']['p_value'])
                signal_names.append(signal_name)
                test_types.append('ANOVA')
            
            if 'kruskal_wallis' in results and results['kruskal_wallis']['p_value'] is not None:
                p_values.append(results['kruskal_wallis']['p_value'])
                signal_names.append(signal_name)
                test_types.append('Kruskal-Wallis')
        
        if p_values:
            plt.figure(figsize=(12, 8))
            
            # Create DataFrame
            df = pd.DataFrame({
                'signal': signal_names,
                'p_value': p_values,
                'test_type': test_types
            })
            
            # Create scatter plot
            plt.subplot(2, 2, 1)
            sns.scatterplot(data=df, x='signal', y='p_value', hue='test_type')
            plt.axhline(y=0.05, color='red', linestyle='--', alpha=0.7)
            plt.title('P-values by Signal')
            plt.xticks(rotation=45)
            
            # Create histogram
            plt.subplot(2, 2, 2)
            plt.hist(p_values, bins=20, alpha=0.7, edgecolor='black')
            plt.axvline(x=0.05, color='red', linestyle='--', alpha=0.7)
            plt.title('Distribution of P-values')
            plt.xlabel('P-value')
            plt.ylabel('Frequency')
            
            # Create effect size plot
            plt.subplot(2, 2, 3)
            effect_sizes = []
            effect_signals = []
            
            for signal_name, results in self.statistical_results.items():
                if 'effect_size' in results and results['effect_size']['eta_squared'] is not None:
                    effect_sizes.append(results['effect_size']['eta_squared'])
                    effect_signals.append(signal_name)
            
            if effect_sizes:
                plt.bar(effect_signals, effect_sizes)
                plt.title('Effect Sizes (η²) by Signal')
                plt.xlabel('Signal')
                plt.ylabel('η²')
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Save plot
            plot_path = os.path.join(self.results_dir, 'figures', 'statistical_plots', 'statistical_summary.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
    
    def _create_correlation_heatmaps(self):
        """Create correlation heatmaps between signals."""
        print("Creating correlation heatmaps...")
        
        # Create signal matrix
        signal_data = {}
        for signal_name in self.signals.keys():
            values = []
            for protein in self.proteins:
                if signal_name in protein.get('signals', {}) and protein['signals'][signal_name] is not None:
                    values.append(protein['signals'][signal_name])
                else:
                    values.append(np.nan)
            signal_data[signal_name] = values
        
        # Convert to DataFrame
        df = pd.DataFrame(signal_data)
        
        # Calculate correlations
        correlation_matrix = df.corr()
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, fmt='.2f', cbar_kws={'shrink': 0.8})
        plt.title('Correlation Matrix of Biophysical Signals')
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(self.results_dir, 'figures', 'correlation_plots', 'signal_correlations.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_signal_importance_plot(self):
        """Create signal importance plot based on effect size (eta-squared)."""
        print("Creating signal importance plot...")
        
        # Calculate importance scores using effect size
        importance_scores = []
        signal_names = []
        p_values = []
        
        for signal_name, results in self.statistical_results.items():
            if 'effect_size' in results and results['effect_size']['eta_squared'] is not None:
                # Use eta-squared (effect size) as importance score
                eta_squared = results['effect_size']['eta_squared']
                importance_scores.append(eta_squared)
                signal_names.append(signal_name)
                
                # Also track p-value for significance marking
                p_val = results.get('anova', {}).get('p_value', 1.0)
                p_values.append(p_val if p_val is not None else 1.0)
        
        if importance_scores:
            # Sort by importance (effect size)
            sorted_indices = np.argsort(importance_scores)[::-1]
            sorted_scores = [importance_scores[i] for i in sorted_indices]
            sorted_names = [signal_names[i] for i in sorted_indices]
            sorted_pvals = [p_values[i] for i in sorted_indices]
            
            # Create bar plot
            plt.figure(figsize=(12, 8))
            
            # Color bars by statistical significance
            colors = ['darkgreen' if p < 0.05 else 'lightcoral' for p in sorted_pvals]
            bars = plt.bar(range(len(sorted_scores)), sorted_scores, color=colors, alpha=0.7, 
                          edgecolor='black', linewidth=0.8)
            
            # Add effect size threshold lines
            plt.axhline(y=0.01, color='gray', linestyle=':', alpha=0.5, label='Small effect (η²=0.01)')
            plt.axhline(y=0.06, color='orange', linestyle='--', alpha=0.7, label='Medium effect (η²=0.06)')
            plt.axhline(y=0.14, color='red', linestyle='-', alpha=0.7, label='Large effect (η²=0.14)')
            
            # Customize plot
            plt.title('Feature Importance Based on Effect Size (η²)\nProportion of Variance Explained')
            plt.xlabel('Biophysical Signals')
            plt.ylabel('Effect Size (η² - Eta Squared)')
            plt.xticks(range(len(sorted_names)), sorted_names, rotation=45, ha='right')
            
            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='darkgreen', alpha=0.7, label='Significant (p < 0.05)'),
                Patch(facecolor='lightcoral', alpha=0.7, label='Not significant (p ≥ 0.05)'),
            ]
            plt.legend(handles=legend_elements, loc='upper right')
            
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            
            # Save plot
            plot_path = os.path.join(self.results_dir, 'figures', 'summary_plots', 'signal_importance.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
    
    def generate_report(self):
        """Generate comprehensive report of findings."""
        print("Generating comprehensive report...")
        
        report = []
        report.append("# Biophysical Signals Analysis Report")
        report.append("")
        report.append(f"**Analysis Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Proteins**: {len(self.proteins)}")
        report.append(f"**Total Clusters**: {len(self.clusters)}")
        report.append(f"**Total Signals**: {len(self.signals)}")
        report.append("")
        
        # Multiple testing correction summary
        bonferroni_significant = sum(1 for results in self.statistical_results.values() 
                                   if results.get('bonferroni_significant', False))
        bh_significant = sum(1 for results in self.statistical_results.values() 
                           if results.get('bh_significant', False))
        original_significant = sum(1 for results in self.statistical_results.values() 
                                 if results.get('anova', {}).get('significant', False))
        
        report.append("## Multiple Hypothesis Testing Corrections")
        report.append("")
        report.append(f"- **Original significant tests (p < 0.05)**: {original_significant}/{len(self.signals)}")
        report.append(f"- **Bonferroni significant tests (p < 0.05)**: {bonferroni_significant}/{len(self.signals)}")
        report.append(f"- **Benjamini-Hochberg significant tests (FDR < 0.05)**: {bh_significant}/{len(self.signals)}")
        report.append("")
        report.append("**Note**: Bonferroni correction controls Family-wise Error Rate (FWER), while Benjamini-Hochberg controls False Discovery Rate (FDR).")
        report.append("")
        
        # Top significant signals (using BH correction as primary)
        significant_signals = bh_significant if bh_significant else bonferroni_significant if bonferroni_significant else original_significant
        
        if significant_signals > 0:
            report.append("## Top Significant Signals")
            report.append("")
            
            # Sort signals by significance
            sorted_signals = sorted(self.statistical_results.items(), 
                                  key=lambda x: x[1].get('bh_p_value', x[1].get('bonferroni_p_value', x[1].get('anova', {}).get('p_value', 1))))
            
            for signal_name, results in sorted_signals[:10]:  # Top 10
                signal = self.signals[signal_name]
                p_value = results.get('anova', {}).get('p_value', 'N/A')
                bh_p_value = results.get('bh_p_value', 'N/A')
                bonferroni_p_value = results.get('bonferroni_p_value', 'N/A')
                effect_size = results.get('effect_size', {}).get('eta_squared', 'N/A')
                
                report.append(f"### {signal.description}")
                report.append(f"- **Category**: {signal.category}")
                report.append(f"- **Original p-value**: {p_value:.2e}")
                report.append(f"- **BH-corrected p-value**: {bh_p_value:.2e}")
                report.append(f"- **Bonferroni-corrected p-value**: {bonferroni_p_value:.2e}")
                report.append(f"- **Effect size (η²)**: {effect_size:.3f}")
                report.append("")
        
        report.append("")
        report.append("## Detailed Statistical Results")
        report.append("")
        
        for signal_name, results in self.statistical_results.items():
            signal = self.signals[signal_name]
            report.append(f"### {signal.description}")
            report.append(f"- **Category**: {signal.category}")
            
            if 'anova' in results:
                anova = results['anova']
                report.append(f"- **ANOVA F-statistic**: {anova.get('f_statistic', 'N/A'):.3f}")
                report.append(f"- **ANOVA p-value**: {anova.get('p_value', 'N/A'):.2e}")
                report.append(f"- **ANOVA significant**: {anova.get('significant', 'N/A')}")
            
            if 'kruskal_wallis' in results:
                kw = results['kruskal_wallis']
                report.append(f"- **Kruskal-Wallis H-statistic**: {kw.get('h_statistic', 'N/A'):.3f}")
                report.append(f"- **Kruskal-Wallis p-value**: {kw.get('p_value', 'N/A'):.2e}")
                report.append(f"- **Kruskal-Wallis significant**: {kw.get('significant', 'N/A')}")
            
            if 'effect_size' in results:
                effect = results['effect_size']
                report.append(f"- **Effect size (η²)**: {effect.get('eta_squared', 'N/A'):.3f}")
                report.append(f"- **Effect size interpretation**: {effect.get('interpretation', 'N/A')}")
            
            report.append("")
        
        # Save report
        report_path = os.path.join(self.results_dir, 'reports', 'biophysical_signals_report.md')
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Report saved to: {report_path}")
    
    def run_complete_analysis(self):
        """Run the complete biophysical signals analysis."""
        print("Starting biophysical signals analysis...")
        
        # Load data
        self.load_clusters()
        
        # Calculate all signals
        self.calculate_all_signals()
        
        # Run statistical analysis
        self.run_statistical_analysis()
        
        # Create visualizations
        self.create_visualizations()
        
        # Generate report
        self.generate_report()
        
        print("Analysis complete!")
        return self.statistical_results

def process_single_unit(unit_name, unit_path, results_base_dir, create_violin_plots=False):
    """
    Process a single unit independently.
    
    Args:
        unit_name: Name of the unit
        unit_path: Path to the unit directory containing FASTA files
        results_base_dir: Base results directory
        create_violin_plots: Whether to create violin plots
    
    Returns:
        dict with processing results
    """
    import glob
    
    print(f"\nProcessing unit: {unit_name}")
    
    # Create subdirectory for this unit's results
    unit_results_dir = os.path.join(results_base_dir, unit_name)
    
    # Find all FASTA files in the unit directory
    fasta_files = glob.glob(os.path.join(unit_path, '*.fasta'))
    
    if not fasta_files:
        print(f"  Warning: No FASTA files found in {unit_path}")
        return None
    
    print(f"  Found {len(fasta_files)} cluster files")
    
    try:
        # Create analyzer for this unit
        analyzer = BiophysicalSignalsAnalyzer(unit_path, unit_results_dir, create_violin_plots)
        results = analyzer.run_complete_analysis()
        
        # Count significant signals
        significant_count = sum(1 for r in results.values() 
                              if r.get('bh_significant', False))
        
        # Extract feature importance data using effect size (eta-squared)
        feature_importance = {}
        for signal_name, result in results.items():
            if 'effect_size' in result and result['effect_size']['eta_squared'] is not None:
                # Use eta-squared as importance score (proportion of variance explained)
                eta_squared = result['effect_size']['eta_squared']
                feature_importance[signal_name] = eta_squared
        
        print(f"  → Results saved to: {unit_results_dir}")
        print(f"  → Clusters: {len(analyzer.clusters)}")
        print(f"  → Proteins: {len(analyzer.proteins)}")
        print(f"  → Significant signals: {significant_count}/{len(results)}")
        
        return {
            'unit_name': unit_name,
            'unit_path': unit_path,
            'results_dir': unit_results_dir,
            'num_clusters': len(analyzer.clusters),
            'num_proteins': len(analyzer.proteins),
            'num_signals': len(results),
            'significant_signals': significant_count,
            'statistical_results': results,
            'feature_importance': feature_importance,
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
        log_f.write("Biophysical Signals Analysis Summary\n")
        log_f.write("===================================\n\n")
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
            total_proteins = sum(r['num_proteins'] for r in successful_results)
            total_significant = sum(r['significant_signals'] for r in successful_results)
            total_signals = sum(r['num_signals'] for r in successful_results)
            
            log_f.write(f"Total clusters across all units: {total_clusters}\n")
            log_f.write(f"Total proteins across all units: {total_proteins}\n")
            log_f.write(f"Total significant signals: {total_significant}/{total_signals}\n\n")
            
            log_f.write("Successful unit-by-unit results:\n")
            for result in successful_results:
                log_f.write(f"\n  Unit: {result['unit_name']}\n")
                log_f.write(f"    Clusters: {result['num_clusters']}\n")
                log_f.write(f"    Proteins: {result['num_proteins']}\n")
                log_f.write(f"    Signals analyzed: {result['num_signals']}\n")
                log_f.write(f"    Significant signals: {result['significant_signals']}\n")
                log_f.write(f"    Results directory: {result['results_dir']}\n")
        
        if failed_results:
            log_f.write(f"\nFailed units:\n")
            for result in failed_results:
                log_f.write(f"\n  Unit: {result['unit_name']}\n")
                log_f.write(f"    Error: {result['error']}\n")
        
        log_f.write(f"\nAll results saved under: {results_dir}\n")
        log_f.write("Each successful unit has its own subdirectory with complete biophysical analysis.\n")
    
    print(f"Summary log saved to: {summary_log_path}")

def aggregate_feature_importance(successful_results):
    """
    Aggregate feature importance across all successful units by:
    1. Ranking features by effect size (η²) within each unit
    2. Counting how often each feature ranks as most important
    3. Calculating mean effect sizes across units
    
    Args:
        successful_results: List of successful unit results containing feature_importance (η²)
    
    Returns:
        dict: Aggregated importance data with ranking frequencies and mean effect sizes
    """
    import pandas as pd
    from collections import defaultdict
    
    # Collect all feature importance data
    all_importance_data = []
    
    for result in successful_results:
        if 'feature_importance' in result and result['feature_importance']:
            unit_data = result['feature_importance'].copy()
            unit_data['unit_name'] = result['unit_name']
            all_importance_data.append(unit_data)
    
    if not all_importance_data:
        return None
    
    # Track rankings and effect sizes for each feature
    ranking_counts = defaultdict(lambda: {
        'rank_1_count': 0,      # Highest effect size
        'rank_2_count': 0,      # 2nd highest
        'rank_3_count': 0,      # 3rd highest
        'top_5_count': 0,       # In top 5
        'total_units': 0,       # Appeared in how many units
        'mean_rank': [],        # All ranks for averaging
        'effect_sizes': []      # All effect sizes for averaging
    })
    
    total_units = len(all_importance_data)
    
    # For each unit, rank the features by effect size
    for unit_data in all_importance_data:
        unit_name = unit_data.pop('unit_name')
        
        # Clean data (effect sizes should be 0-1, but check for issues)
        clean_data = {}
        for signal_name, effect_size in unit_data.items():
            if np.isnan(effect_size) or effect_size < 0:
                effect_size = 0.0
            elif effect_size > 1.0:  # Shouldn't happen, but cap at 1
                effect_size = 1.0
            clean_data[signal_name] = effect_size
        
        # Sort features by effect size (descending) - higher η² = more important
        sorted_features = sorted(clean_data.items(), key=lambda x: x[1], reverse=True)
        
        # Count rankings and store effect sizes
        for rank, (signal_name, effect_size) in enumerate(sorted_features, start=1):
            ranking_counts[signal_name]['total_units'] += 1
            ranking_counts[signal_name]['mean_rank'].append(rank)
            ranking_counts[signal_name]['effect_sizes'].append(effect_size)
            
            if rank == 1:
                ranking_counts[signal_name]['rank_1_count'] += 1
            if rank == 2:
                ranking_counts[signal_name]['rank_2_count'] += 1
            if rank == 3:
                ranking_counts[signal_name]['rank_3_count'] += 1
            if rank <= 5:
                ranking_counts[signal_name]['top_5_count'] += 1
    
    # Convert to final format with calculated statistics
    aggregated_dict = {}
    for signal_name, stats in ranking_counts.items():
        mean_rank = np.mean(stats['mean_rank']) if stats['mean_rank'] else 0
        mean_effect_size = np.mean(stats['effect_sizes']) if stats['effect_sizes'] else 0
        std_effect_size = np.std(stats['effect_sizes']) if stats['effect_sizes'] else 0
        
        aggregated_dict[signal_name] = {
            'rank_1_count': stats['rank_1_count'],
            'rank_2_count': stats['rank_2_count'],
            'rank_3_count': stats['rank_3_count'],
            'top_5_count': stats['top_5_count'],
            'total_units': stats['total_units'],
            'mean_rank': mean_rank,
            'rank_1_percentage': 100 * stats['rank_1_count'] / total_units,
            'top_5_percentage': 100 * stats['top_5_count'] / total_units,
            'mean_effect_size': mean_effect_size,
            'std_effect_size': std_effect_size
        }
    
    return aggregated_dict

def create_aggregated_importance_plot(aggregated_importance, results_dir, project_name):
    """
    Create aggregated feature importance plot showing mean effect sizes across units.
    
    Args:
        aggregated_importance: Dictionary of aggregated importance statistics
        results_dir: Base results directory
        project_name: Project name for file naming
    """
    if not aggregated_importance:
        print("No feature importance data to aggregate")
        return
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    print("Creating aggregated feature importance plot...")
    
    # Extract data for plotting
    signal_names = list(aggregated_importance.keys())
    mean_effects = [aggregated_importance[name]['mean_effect_size'] for name in signal_names]
    std_effects = [aggregated_importance[name]['std_effect_size'] for name in signal_names]
    rank_1_counts = [aggregated_importance[name]['rank_1_count'] for name in signal_names]
    rank_1_percentages = [aggregated_importance[name]['rank_1_percentage'] for name in signal_names]
    total_units = aggregated_importance[signal_names[0]]['total_units']  # Same for all
    
    # Sort by mean effect size (descending)
    sorted_indices = sorted(range(len(signal_names)), 
                           key=lambda i: -mean_effects[i])
    sorted_names = [signal_names[i] for i in sorted_indices]
    sorted_effects = [mean_effects[i] for i in sorted_indices]
    sorted_stds = [std_effects[i] for i in sorted_indices]
    sorted_rank_1 = [rank_1_counts[i] for i in sorted_indices]
    sorted_rank_1_pct = [rank_1_percentages[i] for i in sorted_indices]
    
    # Create the plot with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # --- Subplot 1: Mean Effect Size with Error Bars ---
    x_pos = np.arange(len(sorted_names))
    bars1 = ax1.bar(x_pos, sorted_effects, yerr=sorted_stds, capsize=5,
                    color='steelblue', alpha=0.7, edgecolor='black', linewidth=0.8,
                    error_kw={'linewidth': 1.5, 'ecolor': 'darkblue', 'alpha': 0.6})
    
    # Color bars by effect size magnitude
    for i, (bar, effect) in enumerate(zip(bars1, sorted_effects)):
        if effect >= 0.14:  # Large effect
            bar.set_color('darkgreen')
            bar.set_alpha(0.8)
        elif effect >= 0.06:  # Medium effect
            bar.set_color('goldenrod')
            bar.set_alpha(0.7)
        elif effect >= 0.01:  # Small effect
            bar.set_color('orange')
            bar.set_alpha(0.6)
        else:  # Negligible effect
            bar.set_color('lightcoral')
            bar.set_alpha(0.5)
    
    # Add effect size threshold lines
    ax1.axhline(y=0.01, color='gray', linestyle=':', alpha=0.5, linewidth=1.5)
    ax1.axhline(y=0.06, color='orange', linestyle='--', alpha=0.7, linewidth=2)
    ax1.axhline(y=0.14, color='red', linestyle='-', alpha=0.7, linewidth=2)
    
    # Add percentage annotations
    for i, (bar, pct) in enumerate(zip(bars1, sorted_rank_1_pct)):
        height = bar.get_height() + sorted_stds[i]
        if pct > 0:
            ax1.annotate(f'{pct:.0f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3), textcoords='offset points',
                        ha='center', va='bottom', fontsize=7, alpha=0.8)
    
    ax1.set_title(f'Mean Effect Size (η²) Across Units\n({project_name} dataset, n={total_units} units)\nError bars = ±1 SD, percentages = times ranked #1', 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.set_xlabel('Biophysical Signals', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Mean Effect Size (η² - Proportion of Variance)', fontsize=11, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(sorted_names, rotation=45, ha='right', fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add legend for colors
    from matplotlib.patches import Patch
    legend_elements1 = [
        Patch(facecolor='darkgreen', alpha=0.8, label='Large (η² ≥ 0.14)'),
        Patch(facecolor='goldenrod', alpha=0.7, label='Medium (0.06 ≤ η² < 0.14)'),
        Patch(facecolor='orange', alpha=0.6, label='Small (0.01 ≤ η² < 0.06)'),
        Patch(facecolor='lightcoral', alpha=0.5, label='Negligible (η² < 0.01)')
    ]
    ax1.legend(handles=legend_elements1, loc='upper right', fontsize=9)
    
    # --- Subplot 2: Ranking Frequency ---
    bars2 = ax2.bar(x_pos, sorted_rank_1, color='steelblue', alpha=0.7,
                    edgecolor='black', linewidth=0.8)
    
    # Color bars by frequency
    max_rank_1 = max(sorted_rank_1) if sorted_rank_1 else 1
    for i, (bar, count) in enumerate(zip(bars2, sorted_rank_1)):
        if count >= max_rank_1 * 0.5:  # Top tier
            bar.set_color('darkgreen')
            bar.set_alpha(0.8)
        elif count > 0:  # At least once
            bar.set_color('goldenrod')
            bar.set_alpha(0.7)
        else:  # Never ranked #1
            bar.set_color('lightcoral')
            bar.set_alpha(0.6)
    
    # Add annotations
    for i, (bar, pct) in enumerate(zip(bars2, sorted_rank_1_pct)):
        height = bar.get_height()
        if height > 0:
            ax2.annotate(f'{pct:.0f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3), textcoords='offset points',
                        ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    ax2.set_title('Ranking Frequency: Times Ranked #1 by Effect Size', 
                  fontsize=13, fontweight='bold', pad=15)
    ax2.set_xlabel('Biophysical Signals', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Times Ranked #1 (Highest η²)', fontsize=11, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(sorted_names, rotation=45, ha='right', fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add legend
    legend_elements2 = [
        Patch(facecolor='darkgreen', alpha=0.8, label='Frequently #1'),
        Patch(facecolor='goldenrod', alpha=0.7, label='Sometimes #1'),
        Patch(facecolor='lightcoral', alpha=0.6, label='Never #1')
    ]
    ax2.legend(handles=legend_elements2, loc='upper right', fontsize=9)
    
    plt.tight_layout()
    
    # Save plot
    os.makedirs(results_dir, exist_ok=True)
    plot_path = os.path.join(results_dir, f'aggregated_feature_importance_{project_name}.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Aggregated feature importance plot saved to: {plot_path}")
    
    # Also save the aggregated data as CSV
    csv_path = os.path.join(results_dir, f'aggregated_feature_importance_{project_name}.csv')
    import pandas as pd
    
    df_export = pd.DataFrame([
        {
            'signal_name': name,
            'mean_effect_size': stats['mean_effect_size'],
            'std_effect_size': stats['std_effect_size'],
            'rank_1_count': stats['rank_1_count'],
            'rank_1_percentage': stats['rank_1_percentage'],
            'rank_2_count': stats['rank_2_count'],
            'rank_3_count': stats['rank_3_count'],
            'top_5_count': stats['top_5_count'],
            'top_5_percentage': stats['top_5_percentage'],
            'mean_rank': stats['mean_rank'],
            'total_units': stats['total_units']
        }
        for name, stats in aggregated_importance.items()
    ])
    
    # Sort by mean effect size (descending)
    df_export = df_export.sort_values('mean_effect_size', ascending=False)
    df_export.to_csv(csv_path, index=False)
    print(f"Aggregated feature importance data saved to: {csv_path}")

def run(cfg):
    """Main entry point for biophysical signals analysis."""
    import glob
    import datetime
    
    # Get project directory from config
    project_key = 'biophysical_signals'
    project_name = cfg.get(f'{project_key}_project_directory', 'biophysical_signals')
    create_violin_plots = cfg.get(f'{project_key}_create_violin_plots', False)
    
    # Construct paths
    input_dir = os.path.join('inputs', project_key, project_name)
    results_dir = os.path.join('results', project_key, project_name)
    
    print(f"Biophysical Signals Analysis")
    print(f"Project: {project_name}")
    print(f"Input directory: {input_dir}")
    print(f"Results directory: {results_dir}")
    print(f"Create violin plots: {create_violin_plots}")
    print()
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return
    
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
        result = process_single_unit(unit_name, unit_path, results_dir, create_violin_plots)
        if result:
            all_results.append(result)
    
    # Create summary log
    end_time = datetime.datetime.now()
    create_summary_log(all_results, results_dir, project_name, start_time, end_time)
    
    # Create aggregated feature importance plot
    successful_results = [r for r in all_results if r.get('success', False)]
    if len(successful_results) > 1:  # Only create aggregated plot if we have multiple successful units
        print("\n--- Creating Aggregated Feature Importance Plot ---")
        aggregated_importance = aggregate_feature_importance(successful_results)
        if aggregated_importance:
            create_aggregated_importance_plot(aggregated_importance, results_dir, project_name)
        else:
            print("No feature importance data available for aggregation")
    else:
        print("\nSkipping aggregated plot (need at least 2 successful units for meaningful aggregation)")
    
    print(f"\n=== SUMMARY ===")
    print(f"Processed {len(successful_results)}/{len(all_results)} units successfully")
    if successful_results:
        total_clusters = sum(r['num_clusters'] for r in successful_results)
        total_proteins = sum(r['num_proteins'] for r in successful_results)
        print(f"Total clusters: {total_clusters}")
        print(f"Total proteins: {total_proteins}")
    print(f"Results directory: {results_dir}")
    print(f"Duration: {end_time - start_time}")
    
    return {
        'units_processed': len(all_results),
        'results': all_results,
        'results_dir': results_dir,
        'duration': end_time - start_time
    } 