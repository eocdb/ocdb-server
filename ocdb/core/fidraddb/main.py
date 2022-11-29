# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from FRMmetadataQCfunctions import FRMmetadataQC
from FRMmainfunctions import readFRMfile, getfilekey, readFRMmetadata, checkFRMmetadata
import shutil
import os


def check_FRM_uploaded_file(file, valid_files_dir):
    # read the file and scann all lines
    scan = readFRMfile(file)

    # recognize file keywords
    filekey = getfilekey(scan)

    # read all metadata info
    metadata = readFRMmetadata(scan)

    print('check metadata validity:')
# apply QC on metadata
    metadataQC = FRMmetadataQC(metadata, scan, filekey)

    for k in metadataQC.keys():
        print(k + ': ' + metadataQC[k])
    print('------------------------')

## define dictionnary with for each file type which are mandatory and not mandatory metadata
    MANDATORY = {'RADCAL' : ['CALDATE', 'CALLAB', 'DEVICE', 'CALDATA'],
             'ANGDATA' : ['DEVICE', 'CALDATE', 'COSERROR', 'AZIMUTH_ANGLE', 'UNCERTAINTY'],
             'POLDATA' : ['CALDATE', 'CALLAB', 'DEVICE', 'CALDATA'],
             'STRAYDATA': ['CALDATE', 'CALLAB', 'DEVICE', 'LSF', 'UNCERTAINTY'],
             'TEMPDATA' : ['CALDATE', 'CALLAB', 'DEVICE', 'CALDATA', 'REFERENCE_TEMP']}

    OPTIONAL = {'RADCAL' : ['PANELDATA', 'LAMPDATA', 'LAMP_CCT', 'VERSION', 'USER', 'LAMP_ID', 'PANEL_ID', 'AMBIENT_TEMP'],
            'ANGDATA' : ['VERSION', 'USER'],
            'POLDATA': ['VERSION', 'USER', 'AMBIENT_TEMP'],
            'STRAYDATA': ['VERSION', 'USER', 'AMBIENT_TEMP'],
            'TEMPDATA' : ['VERSION', 'USER', 'AMBIENT_TEMP']}

    OK = checkFRMmetadata(filekey, metadataQC, MANDATORY, OPTIONAL)

    ## directory for checked FRM4SOC files (files are copied and file names are adapted) /// To be adapted ///
    output_dir = valid_files_dir+'/'+metadata['DEVICE']+'/'+filekey+'/'
    datechar = metadata['CALDATE'][0:4]+metadata['CALDATE'][5:7]+metadata['CALDATE'][8:10]
    newfilename = 'CAL_'+ filekey+'_'+metadata['DEVICE']+'_'+datechar+'.csv'

    if OK:

        if not os.path.exists(output_dir): # check if DIR need to be created
            os.makedirs(output_dir)

        shutil.copy(file ,output_dir+newfilename)

        print("uploaded file passed all QC on file format and is accepted!")

