# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from FRMmetadataQCfunctions_V3 import FRMmetadataQC, FRMisfloat, FRMcheckDATE, FRMcheckDEVICE, FRMisNotempty, FRMisNCOLdata
from FRMmainfunctions_V3 import Read_config_file, readFRMfile, getfilekey, readFRMmetadata, checkFRMmetadata
import shutil
import os

## directory for non-checked FRM4SOC files /// To be adapted ///
DIR_uploaded_files = "/home/hlavigne/Documents/FRM4SOC/fileformats/UPDATE_NOV_2022/"
valid_files_dir = "/home/hlavigne/Documents/FRM4SOC/file_QC_OK"
config_file= '/home/hlavigne/Documents/FRM4SOC/fidradDB_config.csv'

#/// To be adapted ///
file = DIR_uploaded_files+"cp_radcal_SAT0233.txt"

def check_FRM_uploaded_file(file, valid_files_dir, config_file):
    # read the file and scann all lines
    scan = readFRMfile(file)

    # recognize file keywords
    filekey = getfilekey(scan)

    # read all metadata info
    metadata = readFRMmetadata(scan)

    ## read conbfiguration file
    config = Read_config_file(config_file, filekey)

    print('check metadata validity:')
# apply QC on metadata
    metadataQC = FRMmetadataQC(metadata, scan, filekey, config, FRMisfloat, FRMcheckDATE, FRMcheckDEVICE, FRMisNotempty, FRMisNCOLdata)

    for k in metadataQC.keys():
        print(k + ': ' + metadataQC[k])
    print('------------------------')

    OK = checkFRMmetadata(filekey, metadataQC, config)

    ## directory for checked FRM4SOC files (files are copied and file names are adapted) /// To be adapted ///
    output_dir = valid_files_dir+'/'+metadata['DEVICE']+'/'+filekey+'/'
    datechar = metadata['CALDATE'][0:4]+metadata['CALDATE'][5:7]+metadata['CALDATE'][8:10]+metadata['CALDATE'][11:13]+metadata['CALDATE'][14:16]+metadata['CALDATE'][17:19]
    newfilename = 'cp_'+ filekey+'_'+metadata['DEVICE']+'_'+datechar+'.csv'

    if OK:

        if not os.path.exists(output_dir): # check if DIR need to be created
            os.makedirs(output_dir)

        shutil.copy(file ,output_dir+newfilename)

        print("uploaded file passed all QC on file format and is accepted!")

check_FRM_uploaded_file(file, valid_files_dir, config_file)