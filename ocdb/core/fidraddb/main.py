# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from FRMmetadataQCfunctions import FRMmetadataQC
from FRMmainfunctions import readFRMfile, getfilekey, readFRMmetadata, checkFRMmetadata
import shutil

## directory for non-checked FRM4SOC files /// To be adapted ///
DIR_uploaded_files = "/FRM4SOC/fileformats/"

#/// To be adapted ///
file = DIR_uploaded_files+"filename.txt"

def check_FRM_uploaded_file(file):
    """
    determin if an uplodaded FRM calibration file has a valid format
    If yes, file is renamed and copy to the "valid files directories"
    :param file: the path for the uploaded file
    """
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
             'ANGDATA' : ['DEVICE', 'CALDATA', 'CALDATE', 'CALLAB'],
             'POLDATA' : ['CALDATE', 'CALLAB', 'DEVICE', 'CALDATA', 'POLANGLE'],
             'STRAYDATA': ['CALDATE', 'CALLAB', 'DEVICE', 'CALDATA'],
             'TEMPDATA' : ['CALDATE', 'CALLAB', 'DEVICE', 'CALDATA', 'REFTEMP']}

    OPTIONAL = {'RADCAL' : ['PANELDATA', 'LAMPDATA', 'LAMP_CCT', 'VERSION', 'USER', 'LAMP_ID', 'PANEL_ID'],
            'ANGDATA' : ['VERSION', 'USER'],
            'POLDATA': ['VERSION', 'USER'],
            'STRAYDATA': ['VERSION', 'USER'],
            'TEMPDATA' : ['VERSION', 'USER']}

    OK = checkFRMmetadata(filekey, metadataQC, MANDATORY, OPTIONAL)

    ## directory for checked FRM4SOC files (files are copied and file names are adapted) /// To be adapted ///
    DIR_accepted_files = "/FRM4SOC/file_QC_OK/"

    if OK:
    shutil.copy(file ,DIR_accepted_files+filekey+'_'+metadata['DEVICE']+'_'+metadata['CALDATE'][0:10]+'.csv')
    print("uploaded file passed all QC on file format and is accepted!")
