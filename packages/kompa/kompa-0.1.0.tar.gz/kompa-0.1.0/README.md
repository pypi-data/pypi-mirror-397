kompa
============

A lightweight (it runs on my potato 🥔) and fast compression-based k-nearest neighbors (k-NN) classifier using Normalized Compression Distance (NCD) for nucleotide (and maybe AA too?) sequence classification. The implementation is based on the [Less is More: Parameter-Free Text Classification with Gzip arXiv.2212.09410](https://doi.org/10.48550/arXiv.2212.09410), introducing an alternative approach for resource hungry methods like DNNs and other algorithms, like Naive-Bayes.

It compares query sequences against reference FASTA datasets; during tests, the [Silva S16 rDNA datasets](https://www.arb-silva.de/) were used.

## Table of Contents

- [Why it can work?](#why-it-can-work)
  - [Theoretical Foundation](#theoretical-foundation)
  - [Why It Works for Biological Sequences](#why-it-works-for-biological-sequences)
  - [Limitations and Extent](#limitations-and-extent)
- [Performance](#performance)
  - [Benchmark Dataset](#benchmark-dataset)
  - [Execution Metrics](#execution-metrics)
  - [Performance Features](#performance-features)
- [Installation](#installation)
  - [From PyPI](#from-pypi)
  - [From Source](#from-source)
  - [Development Installation](#development-installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Examples](#examples)
  - [Key Concepts](#key-concepts)
  - [Output Format](#output-format)
- [Requirements](#requirements)
- [License](#license)
- [Citations / Acknowledgments](#citations--acknowledgments)

## Why it can work?

Kompa leverages **compression-based similarity** as a universal measure of sequence relatedness, rooted in information theory and Kolmogorov complexity. Here's why this approach is probably effective and efficient for biological sequence classification than the currently popular k-mer based methods:

### Theoretical Foundation

**Kolmogorov Complexity Approximation**: The Kolmogorov complexity of a string is the length of the shortest program that can produce it. While theoretically uncomputable, practical compression algorithms (like LZ4) approximate this by finding patterns and redundancies. The **Normalized Compression Distance (NCD)** uses compression to measure similarity:

```
NCD(x, y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
```

Where similar sequences share common patterns, leading to better compression of their concatenation `C(xy)` relative to their individual compressed sizes.

### Why It Works for Biological Sequences

1. **Pattern Recognition Without Feature Engineering**: DNA/RNA sequences contain inherent patterns (repeats, motifs, conserved regions). Compression algorithms automatically detect these patterns without requiring manual feature extraction or domain knowledge.

2. **Universal Similarity Metric**: Unlike alignment-based methods that require scoring matrices or gap penalties, compression-based distance works universally across different sequence types (nucleotide, protein, text) without parameter tuning.

3. **Conserved Region Detection**: Related biological sequences (e.g., 16S rRNA from similar species) share conserved regions. When concatenated, these shared patterns compress efficiently, yielding low NCD scores and indicating similarity.

4. **Parameter-Free Classification**: The method requires no pre-training (like k-mer based Naive Bayes), or fine-tuning. This makes it ideal for:
   - Low-resource scenarios (limited labeled data)
   - Quick exploratory analysis

5. **Robustness to Noise**: Compression naturally filters out random noise while preserving signal. Small sequencing errors or variations don't drastically affect the overall compression ratio, making the method relatively robust (But the general audience will decide if this method is useful or utterly useless...).

### Limitations and Extent

**Works Well For:**
- ✅ **Highly conserved sequences** (16S/18S rRNA, housekeeping genes)
- ✅ **Taxonomic classification** at genus/family level
- ✅ **Few-shot learning** scenarios with limited examples
- ✅ **Quick screening** of large sequence databases

**Limitations:**
- ⚠️ **Short sequences** (< 500 bp) may lack sufficient information for reliable compression patterns
- ⚠️ **Fine-grained classification** (strain/species level) may require alignment-based approaches for better resolution
- ⚠️ **Highly divergent sequences** with low overall similarity benefit less from compression-based methods
- ⚠️ **Horizontal gene transfer** or recombination events may confound classification

**Optimal Use Cases:**
- Classifying environmental samples against known taxonomic databases
- Rapid metagenomic profiling
- Exploratory analysis before more computationally intensive methods

The approach can be a **fast, parameter-free, universal classifier** alternative for many practical biological sequence classification tasks, particularly when labeled data is scarce or computational resources are limited.

## Performance

Here are some minimal benchmark results (could not do bigger, I have a potato machine 🥔):
The used datasets you can find in the [test_data](https://github.com/heloint/kompa/tree/main/test_data) directory.

### Benchmark Dataset
- **Reference sequences**: 213,119 sequences (Silva S16 rRNA v132)
- **Reference avg length**: 1,474 bp
- **Query sequences**: 2 sequences
- **Query avg length**: 1,379 bp

### Execution Metrics
- **Average execution time**: ~8.4 seconds (over 10 runs)
- **Fastest run**: 6.80 seconds
- **Memory usage**: ~332 MB RAM
- **CPU cores used**: 6 workers (75% of 8 cores)
- **Test system**: 8-core CPU

*Benchmark command: `kompa test_data/query.fa test_data/silva_nr_v132_train_set.fa.gz`*

### Performance Features
- **LZ4 Compression**: Ultra-fast compression (10x faster than zlib)
- **Parallel Processing**: Multi-process execution across all CPU cores (Multi-threading is out of question, the tasks are CPU bound, so Python's GIL is a problem)
- **Memory Efficient**: Streaming architecture with Iterators / Generator, and temporary disk cache storage used to minimize the overhead during the argument pickling for child processes.
- **I/O Optimized**: Memory-mapped files and 8MB buffers

## Installation

### From PyPI

```bash
pip install kompa
```

### From Source

```bash
git clone https://github.com/heloint/kompa.git
cd kompa
pip install .
```

### Development Installation

```bash
git clone https://github.com/heloint/kompa.git
cd kompa
pip install -e .
```

## Usage

### Command Line Interface

After installation, you can use the `kompa` command:

```bash
kompa [OPTIONS] queries_file reference_files [reference_files ...]
```

Alternatively, you can run it as a Python module:

```bash
python3 -m kompa [OPTIONS] queries_file reference_files [reference_files ...]
```

**Positional Arguments:**
- `queries_file` - Path to the input queries file (FASTA format, can be gzipped)
- `reference_files` - One or more paths to reference database files (FASTA format, can be gzipped)

**Optional Arguments:**
- `--max-workers N` - Maximum number of worker processes for parallel processing (default: dynamically calculated as 75% of available CPU cores)
- `--no-cpu-limit` - Use all available CPU cores (100%) instead of the default 75%. Overrides `--max-workers`
- `-o, --output PATH` - Path to output file. If not specified, results are printed to console
- `--json` - Output results in JSON format instead of TSV
- `--cache-file-path PATH` - Path to cache file for storing processed reference sequences. If not specified, a temporary file is used and deleted after execution
- `--k-nearest N` - Number of nearest neighbors to consider for classification. Must be a positive integer. Default: 5
- `--spreading-limit FLOAT` - Maximum spreading threshold for NCD values among k-nearest neighbors. Must be non-negative. Default: 0.05

### Examples

**Basic usage with default settings:**
```bash
kompa queries.fasta silva_nr_v132_train_set.fa.gz
```

**With custom worker count:**
```bash
kompa queries.fasta silva_nr_v132_train_set.fa.gz --max-workers 8
```

**Max out CPU usage (use all cores):**
```bash
kompa queries.fasta silva_nr_v132_train_set.fa.gz --no-cpu-limit
```

**Save results to TSV file:**
```bash
kompa queries.fasta silva_nr_v132_train_set.fa.gz -o results.tsv
```

**Save results to JSON file:**
```bash
kompa queries.fasta silva_nr_v132_train_set.fa.gz -o results.json --json
```

**With persistent cache file:**
```bash
kompa queries.fasta silva_nr_v132_train_set.fa.gz --cache-file-path ./my_cache.txt
```

**With custom k-nearest and spreading limit:**
```bash
kompa queries.fasta silva_nr_v132_train_set.fa.gz --k-nearest 10 --spreading-limit 0.1
```

**Multiple reference files with all options:**
```bash
kompa queries.fasta ref1.fa.gz ref2.fa.gz ref3.fa.gz --max-workers 8 --cache-file-path ./cache.txt --k-nearest 5 --spreading-limit 0.05
```

**Display help:**
```bash
kompa --help
```

### Key Concepts

**Normalized Compression Distance (NCD)**: The implementation uses NCD as a similarity metric between sequences. NCD is calculated as:

```
NCD(x, y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
```

where `C(x)` is the compressed size of sequence `x`, `C(y)` is the compressed size of sequence `y`, and `C(xy)` is the compressed size of the concatenation of both sequences.

**Compression-based Classification**: The approach leverages the insight that similar sequences compress better together than dissimilar ones. By using the ultra-fast LZ4 compression algorithm, the classifier can measure semantic similarity without requiring explicit feature engineering.

**k-NN Classification**: For each query sequence, the tool:
1. Computes the NCD between the query and all reference sequences in the reference FASTA dataset
2. Selects the k nearest neighbors (sequences with smallest NCD values)
3. Classifies the query based on the most common taxonomic label among the neighbors

**Spreading Limit**: The spreading limit parameter controls classification confidence. When the spread (difference between max and min NCD values) among k-nearest neighbors exceeds this threshold, the classifier selects the single best match instead of voting among neighbors. This helps handle ambiguous cases where neighbors are not tightly clustered.

### Output Format

Kompa supports two output formats: **TSV** (default) and **JSON** (with `--json` flag).

#### Fields

| Field | Description |
|--------|-------------|
| `query_header` | Header/name of the query sequence |
| `best_reference_header` | Header of the best matching reference sequence |
| `normalized_compression_distance` | NCD score (lower is more similar) |
| `frequency` | Number of times the best reference appears in k-nearest neighbors |
| `max_k_nearest` | The k value used for classification |
| `spreading_limit` | The spreading limit threshold used |

#### TSV Format (default)

Tab-separated values with header row:

```
query_header	best_reference_header	normalized_compression_distance	frequency	max_k_nearest	spreading_limit
should-be-Candidatus_Regiella	Bacteria;Proteobacteria;Gammaproteobacteria;Enterobacteriales;Enterobacteriaceae;Candidatus_Regiella;	0.4934086629001883	3	5	0.05
should-be-Gloeotrichia_PYH6	Bacteria;Cyanobacteria;Oxyphotobacteria;Nostocales;Nostocaceae;Gloeotrichia_PYH6;	0.6254826254826255	2	5	0.05
```

#### JSON Format (with `--json`)

Array of result objects:

```json
[
  {
    "query_header": "should-be-Candidatus_Regiella",
    "best_reference_header": "Bacteria;Proteobacteria;Gammaproteobacteria;Enterobacteriales;Enterobacteriaceae;Candidatus_Regiella;",
    "normalized_compression_distance": 0.4934086629001883,
    "frequency": 3,
    "max_k_nearest": 5,
    "spreading_limit": 0.05
  },
  {
    "query_header": "should-be-Gloeotrichia_PYH6",
    "best_reference_header": "Bacteria;Cyanobacteria;Oxyphotobacteria;Nostocales;Nostocaceae;Gloeotrichia_PYH6;",
    "normalized_compression_distance": 0.6254826254826255,
    "frequency": 2,
    "max_k_nearest": 5,
    "spreading_limit": 0.05
  }
]
```

## Requirements

- Python 3.9+
- lz4 >= 4.0.0 (automatically installed)

## License

- MIT: See LICENSE file for details.

## Citations / Acknowledgments

### [Less is More: Parameter-Free Text Classification with Gzip; arXiv.2212.09410](https://doi.org/10.48550/arXiv.2212.09410)

### [Chuvochina M, Gerken J, Frentrup M, Sandikci Y, Goldmann R, Freese HM, Göker M, Sikorski J, Yarza P, Quast C, Peplies J, Glöckner FO, Reimer LC (2026) SILVA in 2026: a global core biodata resource for rRNA within the DSMZ digital diversity. Nucleic Acids Research, gkaf1247.] (https://academic.oup.com/nar/advance-article/doi/10.1093/nar/gkaf1247/8326456)

### [LZ4 - Extremely fast compression](https://github.com/lz4/lz4)

