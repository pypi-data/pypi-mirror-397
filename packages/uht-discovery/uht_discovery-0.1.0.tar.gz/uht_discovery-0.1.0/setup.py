#!/usr/bin/env python3
"""
Setup script for UHT Discovery package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read version from package
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from uht_discovery import __version__
    version = __version__
except ImportError:
    version = "0.1.0"

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="uht-discovery",
    version=version,
    description="Semi-automated protein discovery pipeline using BLAST, quality control, and language model clustering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Matthew Penner",
    author_email="mp957@cam.ac.uk",
    url="https://github.com/Matt115A/uht-discovery",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.yaml', '*.yml'],
    },
    install_requires=requirements,
    python_requires="~=3.10.0",
    entry_points={
        "console_scripts": [
            "uht-discovery=uht_discovery.cli:main",
            # Individual entry points for backward compatibility
            "uht-blast=uht_discovery.cli:blaster_cli",
            "uht-trim=uht_discovery.cli:trim_cli",
            "uht-clust=uht_discovery.cli:plmclustv2_cli",
            "uht-clust-v1=uht_discovery.cli:plmclust_cli",
            "uht-optimizer=uht_discovery.cli:optimizer_cli",
            "uht-mutation=uht_discovery.cli:mutation_tester_cli",
            "uht-comprehensive=uht_discovery.cli:comprehensive_cli",
            "uht-biophysical=uht_discovery.cli:biophysical_cli",
            "uht-sequence=uht_discovery.cli:sequence_similarity_cli",
            "uht-phylo=uht_discovery.cli:phylo_cli",
            "uht-tsne=uht_discovery.cli:tsne_cli",
            "uht-kmeans=uht_discovery.cli:kmeansbenchmark_cli",
            "uht-gui=uht_discovery.gui:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="bioinformatics protein discovery BLAST clustering language models ESM2",
    project_urls={
        "Bug Reports": "https://github.com/Matt115A/uht-discovery/issues",
        "Source": "https://github.com/Matt115A/uht-discovery",
        "Documentation": "https://github.com/Matt115A/uht-discovery#readme",
    },
)

