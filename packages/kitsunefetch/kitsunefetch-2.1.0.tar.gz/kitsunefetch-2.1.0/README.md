# 🦊 KitsuneFetch : Multi-Database Protein Query Tool

<p align="center">
  <img src="Logo_KitsuneFetch.png" alt="KitsuneFetch Logo" width="250">
</p>
 
<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-purple.svg" alt="Version 2.0.0">
  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="Python 3.7+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License MIT">
  <img src="https://img.shields.io/badge/PDB-GraphQL%20API-orange.svg" alt="PDB GraphQL">
  <img src="https://img.shields.io/badge/AlphaFold-DB-red.svg" alt="AlphaFold">
  <img src="https://img.shields.io/badge/ModelArchive-supported-yellow.svg" alt="ModelArchive">
</p>

<p align="center">
🦊 KitsuneFetch 🦊    Fetch me if you can!
</p> 

<p align="center">
  <b>A powerful command-line tool to query multiple protein structure databases with advanced filtering options</b>
</p>

---

## ✨ Features

- 🔍 **Smart Search** — Query by protein name, gene symbol, common aliases, or FASTA sequence
- 🌐 **Multi-Database** — Search PDB, AlphaFold Database, and ModelArchive
- 🎯 **Advanced Filtering** — Filter by species, date, technique, oligomeric state, mutations, ligands, pLDDT, and more
- 📊 **Automated Statistics** — Generates summary statistics and publication-ready pie charts
- 📥 **Bulk Download** — Download all matching structure files (PDB/mmCIF)
- ⚡ **Efficient** — Uses RCSB Search API and GraphQL for fast, batched data retrieval
- 🛠️ **Configurable** — Customize ligand exclusions and protein name mappings

---

## 📦 Installation

### Requirements

- Python 3.7+
- `requests`
- `matplotlib`
- `numpy`

### Quick Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install kitsunefetch
```

---

## 🚀 Quick Start

```bash
# Basic search (all databases)
kitsunefetch HSP90

# Search specific database
kitsunefetch HSP90 human --database=pdb
kitsunefetch HSP90 human --database=alphafold
kitsunefetch HSP90 human --database=all

# FASTA sequence search
kitsunefetch my_sequence.fasta --database=all

# Advanced filtering with pLDDT
kitsunefetch HSP90 human --database=all --min-plddt=70
```

---

## 📖 Usage

```
kitsunefetch <protein_name|fasta_file> [species] [date_range] [options]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `protein_name` | ✅ | Protein name, nickname, or gene symbol |
| `fasta_file` | ✅ | Path to FASTA file (.fasta, .fa, .faa, .txt) |
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

## 🗄️ Database Options

| Option | Description |
|--------|-------------|
| `--database=pdb` | Search PDB only (experimental structures) |
| `--database=alphafold` | Search AlphaFold DB only (AI-predicted) |
| `--database=modelarchive` | Search ModelArchive only (computational models) |
| `--database=all` | Search all databases (default) |

---

## 🧬 FASTA Sequence Search

Search for structures by sequence similarity using a FASTA file:

```bash
# Basic sequence search
kitsunefetch my_protein.fasta

# With identity threshold
kitsunefetch my_protein.fasta --identity=0.95

# With E-value threshold
kitsunefetch my_protein.fasta --evalue=0.01

# Combined with other filters
kitsunefetch my_protein.fasta human --database=pdb --identity=0.9
```

### FASTA Search Options

| Option | Default | Description |
|--------|---------|-------------|
| `--identity=N` | 0.9 | Minimum sequence identity (0.0-1.0) |
| `--evalue=N` | 0.1 | Maximum E-value threshold |

---

## ⚙️ Filter Options

### Complex Filters

| Option | Description |
|--------|-------------|
| `--no-complex` | Exclude structures in complex with other proteins |
| `--only-complex` | Keep only protein complexes |
| `--complex-with=X` | Keep only complexes with specific partner |

### Structure Filters

| Option | Description |
|--------|-------------|
| `--no-mutation` | Wild-type structures only (PDB) |
| `--no-ligand` | Apo structures only (PDB) |
| `--ligand=X` | Keep only structures with specific ligand |
| `--no-integrative` | Exclude integrative/hybrid structures |
| `--max-missing=N` | Exclude structures with >N missing residues |

### AI-Predicted Structure Filters

| Option | Description |
|--------|-------------|
| `--min-plddt=N` | Minimum pLDDT confidence score (0-100) |

### Oligomeric State

| Option | Description |
|--------|-------------|
| `--oligomer=1` | Monomers only |
| `--oligomer=2` | Dimers only |
| `--oligomer=N` | N-mers only |

### Experimental Technique

| Option | Description |
|--------|-------------|
| `--technique=xray` | X-ray diffraction |
| `--technique=nmr` | NMR spectroscopy |
| `--technique=em` | Electron microscopy (cryo-EM) |
| `--technique=predicted` | AI predictions (AlphaFold/ModelArchive) |
| `--technique=alphafold` | AlphaFold predictions only |
| `--technique=modelarchive` | ModelArchive models only |
| `--technique=other` | Other techniques |

### Download & Performance

| Option | Description |
|--------|-------------|
| `--download` | Download structure files (PDB/mmCIF) |
| `--batch-size=N` | Structures per batch (default: 5) |

---

## 💡 Examples

### Multi-Database Queries

```bash
# Search all databases for human HSP90
kitsunefetch HSP90 human --database=all

# AlphaFold predictions only
kitsunefetch HSP90 human --database=alphafold

# PDB experimental structures only
kitsunefetch HSP90 human --database=pdb

# High-confidence AlphaFold structures
kitsunefetch HSP90 human --database=alphafold --min-plddt=90
```

### FASTA Sequence Search

```bash
# Find similar structures across all databases
kitsunefetch query.fasta --database=all

# High identity matches only
kitsunefetch query.fasta --identity=0.95 --evalue=0.001

# Find AlphaFold predictions for similar sequences
kitsunefetch query.fasta human --database=alphafold
```

### Filtering by Complex State

```bash
# HSP90 alone (no complexes)
kitsunefetch HSP90 human --no-complex

# HSP90-CDC37 complexes specifically
kitsunefetch HSP90 human --complex-with=CDC37
```

### Filtering by Structure Properties

```bash
# Wild-type dimers only
kitsunefetch HSP90 human --no-mutation --oligomer=2

# Apo structures (no ligands)
kitsunefetch HSP90 human --no-ligand

# Structures with ATP bound
kitsunefetch HSP90 human --ligand=ATP
```

### Combined Filters

```bash
# X-ray tetrameric p53 without complexes
kitsunefetch p53 human --no-complex --technique=xray

# High-quality structures with few missing residues
kitsunefetch HSP90 human --max-missing=10 --no-integrative

# All databases, high confidence only
kitsunefetch HSP90 human --database=all --min-plddt=70 --no-mutation
```

### Download Structures

```bash
# Download from all databases
kitsunefetch HSP90 human --database=all --download

# Download only AlphaFold structures
kitsunefetch HSP90 human --database=alphafold --download
```

---

## 📁 Output

The tool creates a timestamped directory with all results:

```
ALL_HSP90_human_19-12-2025_14-30-45/
├── KitsuneFetch.log              # Command, version, execution time
├── results.csv                   # Main data table
├── filtered_out.csv              # Excluded structures with reasons
├── statistics.txt                # Summary statistics
├── statistics_figures.png        # Pie charts visualization
├── query_sequence.fasta          # Query sequence (FASTA mode only)
├── PDB_structures/               # Downloaded PDB files
│   ├── 1AM1.cif
│   └── ...
├── AlphaFold_structures/         # Downloaded AlphaFold files
│   ├── AF_AFP12345F1.cif
│   └── ...
└── ModelArchive_structures/      # Downloaded ModelArchive files
    ├── MA_MA12345.cif
    └── ...
```

### Directory Naming Convention

| Database | Directory Name Example |
|----------|------------------------|
| PDB only | `PDB_HSP90_human_19-12-2025_14-30-00/` |
| AlphaFold only | `AlphaFold_HSP90_human_19-12-2025_14-30-00/` |
| ModelArchive only | `ModelArchive_HSP90_human_19-12-2025_14-30-00/` |
| All databases | `ALL_HSP90_human_19-12-2025_14-30-00/` |
| FASTA search | `ALL_FASTA_QueryName_19-12-2025_14-30-00/` |

### Results Table Columns

| Column | Description |
|--------|-------------|
| `Structure_ID` | PDB code or AlphaFold/ModelArchive ID |
| `Source` | Database source (PDB, AlphaFold, ModelArchive) |
| `Title` | Structure title |
| `DOI` | Publication DOI or PMID (PDB only) |
| `Release_Date` | Release date |
| `Species` | Source organism(s) |
| `Mutation` | Mutation status (PDB only) |
| `Exp_Technique` | Experimental method or "AI Prediction" |
| `Oligomeric_State` | Number of chains in assembly |
| `Mol_Weight` | Molecular weight (kDa) |
| `Missing_Residues` | Count of unmodeled residues (PDB only) |
| `Ligands` | Bound ligands (PDB only) |
| `pLDDT` | Confidence score (AlphaFold/ModelArchive only) |
| `UniProt_ID` | UniProt accession (AlphaFold/ModelArchive only) |
| `Seq_Score` | Sequence similarity score (FASTA mode only) |
| `Seq_Rank` | Ranking by sequence similarity (FASTA mode only) |

---

## 🔧 Configuration

Create a `DATA/` folder next to the script with optional configuration files:

### `SKIP_LIGANDS.txt`

Ligands to exclude from the ligand list:

```
"HOH", "WAT", "GOL", "EDO", "PEG", "SO4", "PO4", "CL", "NA", "MG", "CA", "ZN"
```

### `PROTEIN_NAME_MAPPINGS.txt`

Aliases for protein names:

```
"hsp90": ["Heat shock protein 90", "HSP90AA1", "HSP90AB1"]
"p53": ["Tumor protein p53", "TP53"]
```

### `SPECIES_MAPPINGS.txt`

Common names to scientific names:

```
"human": "Homo sapiens"
"mouse": "Mus musculus"
"yeast": "Saccharomyces cerevisiae"
```

---

## 📊 Sample Output

### Console Output

```
============================================================
🦊 KitsuneFetch v2.0.0 : MULTI-DATABASE QUERY TOOL
============================================================
Protein: HSP90
Database: ALL
Species: human
Filters: no-mutation, min-plddt=70
============================================================

Searching databases...
Search terms used: ['HSP90', 'Heat shock protein 90', 'HSP90AA1']
Species 'human' converted to 'Homo sapiens'

Found 350 structures:
  - PDB: 245
  - AlphaFold: 98
  - ModelArchive: 7

Fetching details via GraphQL...
  Fetching 245 PDB entries...
  Fetching 105 CSM entries (AlphaFold/ModelArchive)...

Parsing 350 entries...
  Filtered out 120 entries (230 remaining)

Created output directory: ALL_HSP90_human_19-12-2025_14-30-45/
  -> results.csv
  -> filtered_out.csv (120 entries)
  -> statistics.txt
  -> statistics_figures.png

============================================================
DONE!
  Fetched: 350 structures
  After filters: 230 structures
  Final output: 230 entries
    - PDB: 156
    - AlphaFold: 70
    - ModelArchive: 4
  Execution time: 2 min 15.32 sec
Output directory: ALL_HSP90_human_19-12-2025_14-30-45/
============================================================

 🦊 KitsuneFetch 🦊    Fetch me if you can!
```

---

## 🧪 Post-Installation Tests

### Test 1: Multi-database search

```bash
kitsunefetch HSP90 human --database=all
```
✅ **Expected:** Results from PDB + AlphaFold + ModelArchive

### Test 2: AlphaFold with pLDDT filter

```bash
kitsunefetch HSP90 human --database=alphafold --min-plddt=90
```
✅ **Expected:** Only high-confidence AlphaFold predictions

### Test 3: FASTA sequence search

```bash
kitsunefetch test_sequence.fasta --database=all --identity=0.9
```
✅ **Expected:** Structures with ≥90% sequence identity

### Test 4: Download from multiple databases

```bash
kitsunefetch HSP90 human 2024 --database=all --download
```
✅ **Expected:** Separate folders for PDB, AlphaFold, and ModelArchive structures

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [RCSB Protein Data Bank](https://www.rcsb.org/) for providing the Search and GraphQL APIs
- [AlphaFold Database](https://alphafold.ebi.ac.uk/) by DeepMind and EMBL-EBI
- [ModelArchive](https://www.modelarchive.org/) for computational models
- The structural biology community for depositing structures
- This work was supported by RIKEN through the Special Postdoctoral Researcher (SPDR) Program.

<p align="center">
  <img src="Logo_Program_Funding.jpg" alt="RIKEN Programs Logo" width="150">
</p>

---

## 📈 Changelog

### v2.0.0 (December 2025)
- ✨ Added multi-database support (PDB, AlphaFold, ModelArchive)
- ✨ Added FASTA sequence search functionality
- ✨ Added pLDDT filtering for AI-predicted structures
- ✨ Added `--database` option for database selection
- ✨ Added `--identity` and `--evalue` options for sequence search
- ✨ Added `--min-plddt` option for confidence filtering
- ✨ Added unified download for all databases
- 🔄 Changed `--download-pdb` to `--download`
- 📊 Updated statistics to include source distribution and pLDDT ranges

### v1.0.2
- PDB-only support

---

<p align="center">
  Made with ❤️ for structural biologists
</p>

<p align="center">
  🦊 <i>Fetch me if you can!</i> 🦊
</p>
