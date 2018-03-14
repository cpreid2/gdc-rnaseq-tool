import requests
import json
import urllib
import pandas as pd
import sys
import hashlib
import argparse
import os, fnmatch, gzip, shutil, tarfile
from pathlib import Path
import time

## -------------- JSON Filters constructor :
class Filter(object):

    def __init__(self):
        self.filter = {"op": "and","content": []}

    def add_filter(self, Field, Value, Operator):
        self.filter['content'].append({"op":Operator,"content":{"field":Field,"value":Value}})

    def create_filter(self):
        self.final_filter = json.dumps(self.filter,separators=(',',':'))
        return self.final_filter

## -------------- Function for downloading files :
def download(uuid, name, md5, ES, WF, DT, retry=0):
    try :
        fout = OFILE['data'].format(ES=ES, WF=WF, DT=DT, uuid=uuid, name=name)
        def md5_ok() :
            with open(fout, 'rb') as f :
                return (md5 == hashlib.md5(f.read()).hexdigest())

        print("Downloading (attempt {}): {}".format(retry, uuid))
        url = PARAM['url-data'].format(uuid=uuid)

        with urllib.request.urlopen(url) as response :
            data = response.read()

        os.makedirs(os.path.dirname(fout), exist_ok=True)

        with open(fout, 'wb') as f :
            f.write(data)

        if md5_ok():
            return (uuid, retry, md5_ok())
        else:
            os.remove(fout)
            raise ValueError('MD5 Sum Error on ' + uuid)
    except Exception as e :
        print("Error (attempt {}): {}".format(retry, e))
        if (retry >= PARAM['max retry']) :
            raise e
        return download(uuid, name, md5, ES, WF, DT, retry + 1)

## -------------- Function for reading manifest file :
def read_manifest(manifest_loc):
    uuid_list = []
    with open(manifest_loc,'r') as myfile:
        if myfile.readline()[0:2] != 'id': raise ValueError('Bad Manifest File')
        else:
        	for x in myfile:
        		uuid = x.split('\t')[0]
        		uuid_list.append(uuid)
    return uuid_list

## -------------- Function that unpacks gz files into another directory :
def gunzip(file_path,output_path):
    with gzip.open(file_path,"rb") as f_in, open(output_path,"wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

## -------------- Argument Parser Function :
def arg_parse():
    parser = argparse.ArgumentParser(
		description='----GDC RNA Seq File Merging Tool v0.1----',
		usage= 'python3 gdc-rnaseq-tool.py MANIFEST_FILE')
    parser.add_argument('manifest_file', action="store",help='Path to manifest file (or UUID List with -u)')
    parser.add_argument('-g','--hugo', action="store_true",help='Add Hugo Symbol Name')
    args = parser.parse_args()
    return args

## -------------- Errors when passing incorrect name :
def error_parse(code):
	'''
	Generates the error messages
	'''
	error = {
		"bad_mani":"Input must be valid GDC Manifest. " \
		"\n\tGo to https://portal.gdc.cancer.gov/ to download a manifest",
	}
	print("ERROR : " + error[code])
	sys.exit(2)

## -------------- Main function :
def main(args):
    global manifest_file
    global hugo
    manifest_file = args.manifest_file
    hugo = args.hugo

# 0. Run Program
# -------------------------------------------------------
main(arg_parse())

# Get current time
timestr = time.strftime("%Y%m%d-%H%M%S")

# 1. Read in manifest and location of folder
# -------------------------------------------------------
#Location = os.path.dirname(os.path.abspath(__file__)) + '/'
File = manifest_file
Manifest_Loc = str(File.replace('\\', '').strip())
Location = str(Path(File).parents[0]) + '/Merged_RNASeq_' + timestr + '/' # Create path object from the directory

os.makedirs(Location)

print('Reading Manifest File from: ' + Manifest_Loc)
print('Downloading Files to: ' + Location)

UUIDs = read_manifest(Manifest_Loc)

# 2. Get info about files in manifest
# -------------------------------------------------------
File_Filter = Filter()
File_Filter.add_filter("files.file_id",UUIDs,"in")
File_Filter.add_filter("files.analysis.workflow_type",["HTSeq - Counts","HTSeq - FPKM","HTSeq - FPKM-UQ","BCGSC miRNA Profiling"],"in")
File_Filter.create_filter()

EndPoint = 'files'
Fields = 'cases.samples.portions.analytes.aliquots.submitter_id,file_name,cases.samples.sample_type,file_id,md5sum,experimental_strategy,analysis.workflow_type,data_type'
Size = '10000'

Payload = {'filters':File_Filter.create_filter(),
           'format':'json',
           'fields':Fields,
           'size':Size}
r = requests.post('https://api.gdc.cancer.gov/files', json=Payload)
data = json.loads(r.text)
file_list = data['data']['hits']

Dictionary = {}
TCGA_Barcode_Dict = {}
for file in file_list:
    UUID = file['file_id']
    Barcode = file['cases'][0]['samples'][0]['portions'][0]['analytes'][0]['aliquots'][0]['submitter_id']
    File_Name = file['file_name']

    Dictionary[UUID] = {'File Name': File_Name,
    'TCGA Barcode':Barcode,
    'MD5': file['md5sum'],
    'Sample Type': file['cases'][0]['samples'][0]['sample_type'],
    'Experimental Strategy': file['experimental_strategy'],
    'Workflow Type': file['analysis']['workflow_type'],
    'Data Type': file['data_type']}

    TCGA_Barcode_Dict[File_Name] = {Barcode}

# 3. Download files
# -------------------------------------------------------

# Location to save files as they are downloaded
OFILE = {'data':Location+"{ES}/{WF}/{DT}/{uuid}/{name}"}

PARAM = {

# URL
'url-data' : "https://api.gdc.cancer.gov/data/{uuid}",

# Persistence upon error
'max retry' : 10,
}

for key, value in Dictionary.items():
    download(key,
             value['File Name'],
             value['MD5'],
             value['Experimental Strategy'],
             value['Workflow Type'],
             value['Data Type'])

# 4. Merge the RNA Seq files
# -------------------------------------------------------

RNASeq_WFs = ['HTSeq - Counts', 'HTSeq - FPKM-UQ','HTSeq - FPKM']

GZipLocs = [Location + 'RNA-Seq/' + WF for WF in RNASeq_WFs]

# Add Hugo Symbol
if hugo == True:
    url = 'https://github.com/cpreid2/gdc-rnaseq-tool/raw/master/Gene_Annotation/gencode.v22.genes.txt'
    gene_map = pd.read_csv(url,sep='\t')
    gene_map = gene_map[['gene_id','gene_name']]
    gene_map = gene_map.set_index('gene_id')

for i in range(len(RNASeq_WFs)):

    print('--------------')
    # Find all .gz files and ungzip into the folder
    pattern = '*.gz'
    Files = []

    # Create .gz directory in subfolder
    if os.path.exists(GZipLocs[i] + '/UnzippedFiles/'):
        shutil.rmtree(GZipLocs[i] + '/UnzippedFiles/')
        os.makedirs(GZipLocs[i] + '/UnzippedFiles/')
    else:
        os.makedirs(GZipLocs[i] + '/UnzippedFiles/')

    for root, dirs, files in os.walk(GZipLocs[i]):
        for filename in fnmatch.filter(files, pattern):
            OldFilePath = os.path.join(root, filename)
            NewFilePath = os.path.join(GZipLocs[i] + '/UnzippedFiles/', filename.replace(".gz",".tsv"))

            gunzip(OldFilePath, NewFilePath) # unzip to New file path

            Files.append(NewFilePath) # append file to list of files

    Matrix = {}

    for file in Files:
        p = Path(file)
        Name = str(p.name).replace('.tsv','')
        Name = Name + '.gz'
        Name = TCGA_Barcode_Dict[Name]
        Name = str(list(Name)[0])
        Counts_DataFrame = pd.read_csv(file,sep='\t',header=None,names=['GeneId', Name])
        Matrix[Name] = tuple(Counts_DataFrame[Name])

    # Merge Matrices to dataframes and write to files
    if len(Matrix) > 0:
        Merged_File_Name = 'Merged_'+ RNASeq_WFs[i].replace('HTSeq - ','') + '.tsv'
        print('Creating merged ' + RNASeq_WFs[i] + ' File... ' + '( ' + Merged_File_Name + ' )')
        Counts_Final_Df = pd.DataFrame(Matrix, index=tuple((Counts_DataFrame['GeneId'])))
        if hugo == True:
            Counts_Final_Df = gene_map.merge(Counts_Final_Df, how='outer', left_index=True, right_index=True)
        Counts_Final_Df.to_csv(str(Location) + '/' + Merged_File_Name,sep='\t',index=True)

# 5. Merge the miRNA Seq files
# -------------------------------------------------------
miRNASeq_WF = ['BCGSC miRNA Profiling']
miRNASeq_DTs = ['Isoform Expression Quantification','miRNA Expression Quantification']
miRNALocs = [Location + 'miRNA-Seq/BCGSC miRNA Profiling/' + DT for DT in miRNASeq_DTs]

print('--------------')

for i in range(len(miRNASeq_DTs)):

    # Find all .gz files and ungzip into the folder
    pattern = '*.mirnas.quantification.txt'
    Files = []

    for root, dirs, files in os.walk(miRNALocs[i]):
        for filename in fnmatch.filter(files, pattern):
            FilePath = os.path.join(root, filename)

            Files.append(FilePath) # append file to list of files

    miRNA_count_Matrix = {}
    miRNA_rpmm_Matrix = {}

    for file in Files:
        p = Path(file)
        Name = str(p.name)
        Name = TCGA_Barcode_Dict[Name]
        Name = str(list(Name)[0])

        miRNA_DataFrame = pd.read_csv(file,sep='\t')

        miRNA_count_DataFrame = miRNA_DataFrame[['miRNA_ID','read_count']]
        miRNA_count_DataFrame.columns = ['miRNA_ID',Name]

        miRNA_rpmm_DataFrame = miRNA_DataFrame[['miRNA_ID','reads_per_million_miRNA_mapped']]
        miRNA_rpmm_DataFrame.columns = ['miRNA_ID',Name]

        miRNA_count_Matrix[Name] = tuple(miRNA_count_DataFrame[Name])
        miRNA_rpmm_Matrix[Name] = tuple(miRNA_rpmm_DataFrame[Name])

    if len(miRNA_count_Matrix) > 0:
        print('Creating merged miRNASeq Counts File... ( Merged_miRNA_Counts.tsv )')
        miRNA_Count_Final_Df = pd.DataFrame(miRNA_count_Matrix, index=tuple((miRNA_count_DataFrame['miRNA_ID'])))
        miRNA_Count_Final_Df.to_csv(str(Location) + '/Merged_miRNA_Counts.tsv',sep='\t',index=True)
    if len(miRNA_rpmm_Matrix) > 0:
        print('Creating merged miRNASeq rpmm File... ( Merged_miRNA_rpmm.tsv )')
        miRNA_rpmm_Final_Df = pd.DataFrame(miRNA_rpmm_Matrix, index=tuple((miRNA_rpmm_DataFrame['miRNA_ID'])))
        miRNA_rpmm_Final_Df.to_csv(str(Location) + '/Merged_miRNA_rpmm.tsv',sep='\t',index=True)
