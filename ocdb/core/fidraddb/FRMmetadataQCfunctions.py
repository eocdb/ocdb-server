### all functions that check that the value for each metadata label is valid
import re


def FRMmetadataQC(metadata, scan, filekey):
    """
    Determine for each metadata is their corresponding information is correct
    :param scan: a list of strings corresponding to each line of the cal file
    :param metdata: a dictionnary with metadata names as keys and metadata information as values
    :param filekey:  the keyword corresponding to file type (string)
    :return: a dictionnary with metadata names as keys and "valid" or "not valid" as values
    """
    metadataQC = {}
    inst = checkinst(metadata)
    for key in metadata.keys():
        if key == 'CALDATE':
            metadataQC[key] = FRMcheckDATE(metadata[key])
        if key == 'DEVICE':
            metadataQC[key] = FRMcheckDEVICE(metadata[key])
        if key == 'LSF':
            metadataQC[key] = FRMisNCOLdata(metadata[key], key, scan, ncol=256)
        if key == 'UNCERTAINTY' and filekey == 'STRAYDATA':
            metadataQC[key] = FRMisNCOLdata(metadata[key], key, scan, ncol=256)
        if key == 'UNCERTAINTY' and filekey == 'ANGDATA':
            metadataQC[key] = FRMisNCOLdata(metadata[key], key, scan, ncol=47)
        if key == 'COSERROR':
            metadataQC[key] = FRMisNCOLdata(metadata[key], key, scan, ncol=47)
        if key == 'CALDATA' and filekey == 'RADCAL':
            metadataQC[key] = FRMisNCOLdata(metadata[key], key, scan, ncol=10)
        if  key == 'CALDATA' and filekey in ['POLDATA', 'ANGDATA']:
            metadataQC[key] = FRMisNCOLdata(metadata[key], key, scan, ncol=6)
        if key == 'CALDATA' and filekey == 'TEMPDATA':
            metadataQC[key] = FRMisNCOLdata(metadata[key], key, scan, ncol=4)
        if key in ['PANEL_ID', 'LAMP_ID', 'USER', 'CALLAB']:
            metadataQC[key] = FRMisempty(metadata[key])
        if key in ['DEVICE_TEMP','AMBIENT_TEMP', 'LAMP_CCT', 'VERSION', 'POLANGLE', 'REFERENCE_TEMP', 'AZIMUTH_ANGLE']:
            metadataQC[key] = FRMisfloat(metadata[key])
        if key in ['PANELDATA', 'LAMPDATA']:
            metadataQC[key] = FRMisNCOLdata(metadata[key], key, scan, ncol=4)
    return(metadataQC)

def checkinst(metadata):
    """return the instrument type code (i.e. SAT for SATLANTIC and SAM for TrIOS)"""
    try:
        dev = metadata['DEVICE']
        code_inst = dev[0:3]
        if code_inst in ["SAM", "SAT"]:
            return code_inst
        else:
            return "unknown"
    except ValueError:
        return "unkown"

def FRMcheckDATE(strdate):
    """determine if the date is correct"""
    res = "not valid"
    if len(strdate) == 19:
        year = strdate[0:4]
        month = strdate[5:7]
        day = strdate[8:10]
        hour = strdate[11:13]
        min = strdate[14:16]
        sec = strdate[17:19]

        Yqc = re.search(r'\b(?:2030|20[0-4][0-9]|19[789][0-9])\b', year)
        MOqc = re.search(r'\b(?:12|11|10|0[1-9])\b', month)
        Dqc = re.search(r'\b(?:31|30|[1-2][0-9]|0[1-9])\b', day)
        Hqc = re.search(r'\b(?:2[0-3]|[0-1][0-9])\b', hour)
        MIqc = re.search(r'\b(?:[0-5][0-9])\b', min)
        Sqc = re.search(r'\b(?:[0-5][0-9])\b', sec)

        allQC = [Yqc, MOqc, Dqc, Hqc, MIqc, Sqc]
        if all(allQC):
            res = "valid"
    return(res)



def FRMcheckDEVICE(dev):
    """Determine if information for the metadata "DEVICE" is valid
        valid informations are SAMXXXX or SAT_XXXX for TrIOS and SATLANTIC sensors
    """
    res = "not valid"
    if len(dev) >= 7:
        code_inst = dev[0:3]
        devQC = None
        if code_inst == 'SAM':
            devQC = re.search(r'\b(?:\_[0-9][0-9][a-zA-Z0-9][a-zA-Z0-9])\b', dev[3:8])
        if code_inst == 'SAT':
            devQC = re.search(r'\b(?:[0-9][0-9][0-9][0-9])\b', dev[3:7])
    if devQC :
        res = 'valid'
    return(res)


def is_valid_float(element: str) -> bool:
    """determine if a string corresponds to a decimal number"""
    try:
        float(element)
        return True
    except ValueError:
        return False

def FRMisempty(element: str) -> str:
    """determine if a string is not empty and not a decimal number"""
    if element and is_valid_float(element) == False:
        return 'valid'
    else:
        return 'not valid'

def FRMisfloat(element: str) -> str:
    """return 'valid' is a string corresponds to a decimal number"""
    if is_valid_float(element) :
        return 'valid'
    else :
        return 'not valid'


def FRMisNCOLdata(line, key, scan, ncol=4):
    """determine if metadata informations which have a multi-columns formats are valid"""
    line1 = re.split("[\t]+",line)
#    print(key)
#    print(len(line1))
    isfloat = [is_valid_float(el) for el in line1]
    res = "not valid"
    try:
        istart = scan.index('['+key+']')
        iend = scan.index('[END_OF_'+key+']')
        Nlines = iend - istart
        az = allzeros(scan, key)
    except:
        Nlines = 0
    if Nlines > 5 and all(isfloat) and len(line1) == ncol and az == 'NO':
       res = 'valid'
    return res


def allzeros(scan, key):
    """Check if a table of metadata (several columns) are not all zeros """
    res = 'NO'
    istart = scan.index('[' + key + ']')
    iend = scan.index('[END_OF_' + key + ']')
    p = istart + 2  # first line is skipped because sometime contains non float
    LOZ = []
    while p <= iend - 1:
        line = re.split("[\t]+",scan[p])
        LOZ.append(islineofzeros(line))
        p = p + 1
    if sum(LOZ) == 0:
        res = 'YES'
    return(res)

def islineofzeros(line):
    """ Check if a line is not full of zeros"""
    res = 0 # we assume this is only zeros
    for el in line:
        if is_valid_float(el):
            if float(el) != 0:
                res = 1
    return(res)


