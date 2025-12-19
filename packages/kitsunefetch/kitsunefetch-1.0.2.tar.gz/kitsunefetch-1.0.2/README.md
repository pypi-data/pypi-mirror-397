# 🦊 KitsuneFetch : a PDB Protein Query Tool

<p align="center">
  <img src="Logo_KitsuneFetch.png" alt="KitsuneFetch Logo" width="250">
</p>
 
<p align="center">
  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="Python 3.7+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License MIT">
  <img src="https://img.shields.io/badge/PDB-GraphQL%20API-orange.svg" alt="PDB GraphQL">
</p>

<p align="center">
🦊 KitsuneFetch 🦊    Fetch me if you can !
</p> 

<p align="center">
  <b>A powerful command-line tool to query the RCSB Protein Data Bank with advanced filtering options</b>
</p>

---

## ✨ Features

- 🔍 **Smart Search** — Query by protein name, gene symbol, or common aliases
- 🎯 **Advanced Filtering** — Filter by species, date, technique, oligomeric state, mutations, ligands, and more
- 📊 **Automated Statistics** — Generates summary statistics and publication-ready pie charts
- 📥 **Bulk Download** — Download all matching PDB/mmCIF structure files
- ⚡ **Efficient** — Uses GraphQL API for fast, batched data retrieval
- 🛠️ **Configurable** — Customize ligand exclusions and protein name mappings

---

## 📦 Installation

### Requirements

- Python 3.7+
- `requests`
- `matplotlib`
- `numpy`

### Setup

```bash
# Clone the repository
git clone https://github.com/ElisaRioual/KitsuneFetch.git
cd KitsuneFetch

# Install dependencies
pip install requests matplotlib numpy
```

---

## 🚀 Quick Start

```bash
# Basic search
python KitsuneFetch.py HSP90

# Search with species filter
python KitsuneFetch.py HSP90 human

# Search with date range
python KitsuneFetch.py HSP90 human 2015-2024

# Advanced filtering
python KitsuneFetch.py HSP90 human None --no-mutation --technique=xray --oligomer=2
```

---

## 📖 Usage

```
python KitsuneFetch.py <protein_name> [species] [date_range] [options]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `protein_name` | ✅ | Protein name, nickname, or gene symbol |
| `species` | ❌ | Filter by organism (use `None` to skip) |
| `date_range` | ❌ | Filter by release date (use `None` to skip) |

### Date Range Formats

| Format | Example | Description |
|--------|---------|-------------|
| `YYYY-YYYY` | `2000-2010` | From year to year |
| `YYYY-` | `2015-` | From year onwards |
| `-YYYY` | `-2010` | Up to year |
| `YYYY` | `2020` | Specific year only |

---

## ⚙️ Options

### Complex Filters

| Option | Description |
|--------|-------------|
| `--no-complex` | Exclude structures in complex with other proteins |
| `--only-complex` | Keep only protein complexes |
| `--complex-with=X` | Keep only complexes with specific partner (e.g., `CDC37`, `p23`) |

### Structure Filters

| Option | Description |
|--------|-------------|
| `--no-mutation` | Wild-type structures only |
| `--no-ligand` | Apo structures only (no bound ligands) |
| `--ligand=X` | Keep only structures with specific ligand (e.g., `ADP`, `ATP`) |
| `--no-integrative` | Exclude integrative/hybrid structures (AI-predicted) |
| `--max-missing=N` | Exclude structures with more than N missing residues |

### Oligomeric State

| Option | Description |
|--------|-------------|
| `--oligomer=1` | Monomers only |
| `--oligomer=2` | Dimers only |
| `--oligomer=3` | Trimers only |
| `--oligomer=N` | N-mers only |

### Experimental Technique

| Option | Description |
|--------|-------------|
| `--technique=xray` | X-ray diffraction |
| `--technique=nmr` | NMR spectroscopy |
| `--technique=em` | Electron microscopy (cryo-EM) |
| `--technique=other` | Other techniques (neutron, fiber, etc.) |

### Download

| Option | Description |
|--------|-------------|
| `--batch-size=N` | Number of structures to fetch per batch (default: 5). Higher values = faster but may cause rate limiting |

### Batch size

| Option | Description |
|--------|-------------|
| `--download-pdb` | Download PDB/mmCIF files for all matching structures |


---

## 💡 Examples

### Basic Queries

```bash
# All HSP90 structures
python KitsuneFetch.py HSP90

# Human HSP90 structures
python KitsuneFetch.py HSP90 human

# Human HSP90 from 2010-2020
python KitsuneFetch.py HSP90 human 2010-2020
```

### Filtering by Complex State

```bash
# HSP90 alone (no complexes)
python KitsuneFetch.py HSP90 human None --no-complex

# HSP90 in complex with any partner
python KitsuneFetch.py HSP90 human None --only-complex

# HSP90-CDC37 complexes specifically
python KitsuneFetch.py HSP90 human None --complex-with=CDC37
```

### Filtering by Structure Properties

```bash
# Wild-type dimers only
python KitsuneFetch.py HSP90 human None --no-mutation --oligomer=2

# NMR monomeric structures
python KitsuneFetch.py HSP90 None None --oligomer=1 --technique=nmr

# Apo structures (no ligands)
python KitsuneFetch.py HSP90 human None --no-ligand

# Structures with ADP bound
python KitsuneFetch.py HSP90 human None --ligand=ADP
```

### Combined Filters

```bash
# X-ray tetrameric p53 without complexes
python KitsuneFetch.py p53 human None --no-complex --oligomer=4 --technique=xray

# High-quality structures (few missing residues)
python KitsuneFetch.py HSP90 human None --max-missing=10 --no-integrative
```

### Download Structures

```bash
# Download all matching PDB files
python KitsuneFetch.py HSP90 human 2020-2024 --download-pdb
```


### Change the batch size

```bash
# Bigger batch size (default : 5)
python KitsuneFetch.py HSP90 human 2020-2024 --batch-size=15
```

---

## 📁 Output

The tool creates a timestamped directory with all results:

```
HSP90_human_17-12-2024_14-30-45/
├── results.csv              # Main data table
├── filtered_out.csv         # Excluded structures with reasons
├── statistics.txt           # Summary statistics
├── statistics_figures.png   # Pie charts visualization
├── KitsuneFetch.log         # Commandline used and software version 
└── PDB/                     # Downloaded structures (if --download-pdb)
    ├── 1AM1.cif
    ├── 2CG9.pdb
    └── ...
```

### Results Table Columns

| Column | Description |
|--------|-------------|
| `PDB_Code` | 4-letter PDB identifier |
| `Title` | Structure title |
| `DOI` | Publication DOI or PMID |
| `Release_Date` | PDB release date |
| `Species` | Source organism(s) |
| `Mutation` | Mutation status (Yes/No) |
| `Exp_Technique` | Experimental method |
| `Oligomeric_State` | Number of chains in assembly |
| `Mol_Weight` | Molecular weight (kDa) |
| `Missing_Residues` | Count of unmodeled residues |
| `Ligands` | Bound ligands (excluding common additives) |

---

## 🔧 Configuration

Create a `DATA/` folder next to the script with optional configuration files:

### `SKIP_LIGANDS.txt`

Ligands to exclude from the ligand list (common crystallization additives):

```
"HOH", "WAT", "GOL", "EDO", "PEG", "SO4", "PO4", "CL", "NA", "MG", "CA", "ZN"
```

### `PROTEIN_NAME_MAPPINGS.txt`

Aliases for protein names to improve search:

```
"hsp90": ["Heat shock protein 90", "HSP90AA1", "HSP90AB1"]
"p53": ["Tumor protein p53", "TP53"]
"ubiquitin": ["Ubiquitin", "Polyubiquitin", "UBB", "UBC"]
```

### `SPECIES_MAPPINGS.txt`

Common names to scientific names:

```
"human": "Homo sapiens"
"mouse": "Mus musculus"
"yeast": "Saccharomyces cerevisiae"
"ecoli": "Escherichia coli"
```

---

## 📊 Sample Output

### Statistics Visualization

<p align="center">
  <i>The tool generates publication-ready pie charts showing the distribution of experimental techniques, oligomeric states, species, and ligands.</i>
</p>

### Console Output

```
============================================================
🦊 KitsuneFetch v1.0.0 : PDB QUERY TOOL
============================================================
Protein: HSP90
Species: human
Filters: no-mutation, technique=xray
============================================================

Searching PDB database...
Search terms used: ['HSP90', 'Heat shock protein 90', 'HSP90AA1', 'HSP90AB1']
Species 'human' converted to 'Homo sapiens'

Found 245 structures. Fetching details via GraphQL...

  Fetching batch 1/49 (5 structures)...
  Fetching batch 2/49 (5 structures)...
  ...

Parsing 245 entries...
  Filtered out 89 entries based on options (156 remaining)

Created output directory: HSP90_human_17-12-2024_14-30-45/
  -> KitsuneFetch.log
  -> results.csv
  -> filtered_out.csv (89 entries)
  -> statistics.txt
  -> statistics_figures.png

============================================================
DONE!
  Fetched: 245 structures
  After filters: 156 structures
  Final output: 156 entries
Output directory: HSP90_human_17-12-2024_14-30-45/
============================================================



 🦊 KitsuneFetch 🦊    Fetch me if you can !
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [RCSB Protein Data Bank](https://www.rcsb.org/) for providing the GraphQL API
- The structural biology community for depositing structures

---

<p align="center">
  Made with ❤️ for structural biologists
</p>
