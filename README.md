# gdc-rnaseq-tool
Tool to merge RNA Seq Data from the GDC Portal

__Requirements__:

- Python 3
- pandas: `pip3 install pandas`

__Quick Start__:

1. Download manifest containing RNA/miRNA expression files from https://portal.gdc.cancer.gov/
2. `python3 gdc-rnaseq-tool.py <manifest_file>`
---

The GDC RNA Seq tool produces matrices of merged RNA/MiRNA expression data given a manifest file.

Usage: `python gdc-rnaseq-tool.py <manifest_file>`

Notes:
* A test manifest is provided for troubleshooting:  `python gdc-tsv-tool.py Test_Manifest.txt`

**Release Notes:**

Version 1.0: Feb 8, 2018

* Initial release

Known Issues:
N/A
