# gdc-rnaseq-tool
Tool to download / merge individual RNASeq files from the [GDC Portal](https://portal.gdc.cancer.gov) into a matrices identified by [TCGA barcode](https://wiki.nci.nih.gov/display/TCGA/TCGA+barcode).

![Image](https://raw.githubusercontent.com/cpreid2/gdc-rnaseq-tool/master/Images/TCGA%20Barcode.png)

__Inputs and Outputs__:

| I/O | File |
|---|---|
| Input | [GDC Manifest File](https://docs.gdc.cancer.gov/Data_Transfer_Tool/Users_Guide/Preparing_for_Data_Download_and_Upload/#obtaining-a-manifest-file-for-data-download) |
| Output | Merged_Counts.tsv ([HTSeq - Counts](https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/#upper-quartile-fpkm)) |
|  | Merged_FPKM.tsv ([HTSeq - FPKM](https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/#fpkm)) |
|  | Merged_FPKM-UQ.tsv ([HTSeq - FPKM-UQ](https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/#upper-quartile-fpkm)) |
|  | Merged_miRNA_Counts.tsv |
|  | Merged_miRNA_rpmm.tsv |

__Bioinformatics Pipeline Information__:

[RNA-Seq Pipeline](https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/)

[miRNA-Seq Pipeline](https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/miRNA_Pipeline/)

__Requirements__:

- Python 3+
- pandas ( https://pandas.pydata.org/pandas-docs/stable/install.html ): `pip3 install pandas`

__Quick Start__:

1. Download `gdc-rnaseq-tool.py` python script
2. Download manifest containing RNA/miRNA expression files from https://portal.gdc.cancer.gov/
3. `python3 gdc-rnaseq-tool.py <manifest_file>`
---

The GDC RNASeq tool produces matrices of merged RNA/MiRNA expression data given a manifest file.

Usage: `python3 gdc-rnaseq-tool.py <manifest_file>`

Notes:
* A test manifest is provided for troubleshooting:  `python3 gdc-rnaseq-tool.py Test_Manifest.txt`
* Files are by default downloaded to the same folder as the manifest file that was provided

**Release Notes:**

Version 1.0: Feb 8, 2018

* Initial release

Known Issues:
N/A
