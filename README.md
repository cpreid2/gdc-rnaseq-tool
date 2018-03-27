# gdc-rnaseq-tool
Tool to download / merge individual RNASeq files from the [GDC Portal](https://portal.gdc.cancer.gov) into a matrices identified by [TCGA barcode](https://wiki.nci.nih.gov/display/TCGA/TCGA+barcode).

![Image](https://raw.githubusercontent.com/cpreid2/gdc-rnaseq-tool/master/Images/TCGA%20Barcode.png)

__Description__:

The `gdc-rnaseq-tool` performs the following:

1. Downloads RNA-Seq / miRNA-Seq data files using a GDC manifest file
2. Unzips the files into separate folders identified by experimental strategy and bioinformatics workflow
3. Merges the files into separate matrix files identified in the table below

*The script will ignore any files in the manifest file that are not [Transcriptome Profiling files](https://portal.gdc.cancer.gov/repository?filters=%7B%22op%22%3A%22and%22%2C%22content%22%3A%5B%7B%22op%22%3A%22in%22%2C%22content%22%3A%7B%22field%22%3A%22files.data_category%22%2C%22value%22%3A%5B%22Transcriptome%20Profiling%22%5D%7D%7D%5D%7D) generated from the GDC RNA-Seq / miRNA-Seq bioinformatics pipelines located on the [GDC Main Portal](https://portal.gdc.cancer.gov):*

[RNA-Seq / miRNA-Seq Files](https://portal.gdc.cancer.gov/repository?filters=%7B%22op%22%3A%22and%22%2C%22content%22%3A%5B%7B%22op%22%3A%22in%22%2C%22content%22%3A%7B%22field%22%3A%22files.data_category%22%2C%22value%22%3A%5B%22Transcriptome%20Profiling%22%5D%7D%7D%5D%7D)

[RNA-Seq Bioinformatics Pipeline Documentation](https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/)

[miRNA-Seq Bioinformatics Pipeline Documentation](https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/miRNA_Pipeline/)

__Inputs and Outputs__:

| I/O | File |
|---|---|
| Input | [GDC Manifest File](https://docs.gdc.cancer.gov/Data_Transfer_Tool/Users_Guide/Preparing_for_Data_Download_and_Upload/#obtaining-a-manifest-file-for-data-download) |
| Output | Merged_Counts.tsv ([HTSeq - Counts](https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/#upper-quartile-fpkm)) |
|  | Merged_FPKM.tsv ([HTSeq - FPKM](https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/#fpkm)) |
|  | Merged_FPKM-UQ.tsv ([HTSeq - FPKM-UQ](https://docs.gdc.cancer.gov/Data/Bioinformatics_Pipelines/Expression_mRNA_Pipeline/#upper-quartile-fpkm)) |
|  | Merged_miRNA_Counts.tsv |
|  | Merged_miRNA_rpmm.tsv |


__Requirements__:

- Python 3+
- pandas ( https://pandas.pydata.org/pandas-docs/stable/install.html ): `pip3 install pandas`
- requests (http://python-requests.org): `pip3 install requests`

__Quick Start__:

1. [Download](https://github.com/cpreid2/gdc-rnaseq-tool/releases/download/1.0/gdc-rnaseq-tool.py) `gdc-rnaseq-tool.py` python script
2. Download manifest containing RNA/miRNA expression files from https://portal.gdc.cancer.gov/
3. `python3 gdc-rnaseq-tool.py <manifest_file>`

Optional: Add `--hugo` to the command to include the HUGO gene symbol as a separate column.  

`python3 gdc-rnaseq-tool.py <manifest_file> --hugo`

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
