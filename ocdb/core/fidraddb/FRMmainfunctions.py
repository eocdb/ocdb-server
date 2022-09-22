import re
import sys

def readFRMfile(file):
    """ 
    read a text file
    :param file:the path for the uploaded file
    :return: a list of strings corresponding to each line of the file
    """
    sc = open(file, 'r')
    sc = sc.readlines()
    # split lines, trim and remove leading slash
    alllines = [re.sub("[\r\n]+", '', line).strip() for line in sc]
    print(file+" has been read")
    print('--------------------------')
    return(alllines)

def getfilekey(scan):
    """
    Determine the type of calibration file 
    :param scan: a list of strings corresponding to each line of the cal file
    :return: a string, the keyword corresponding to file type
    """
    ALF = {'!RADCAL':False, '!ANGDATA':False, '!POLDATA':False, '!STRAYDATA':False, '!TEMPDATA':False}
    for key in ALF.keys():
        if key in scan:
            ALF[key] = True
## subset the dictionnary with recongized keywords
    ALF_subset = {key: value for key, value in ALF.items() if value }
    filekey = None
    if len(ALF_subset) == 1 :
        filekey = list(ALF_subset.keys())[0]
        filekey = filekey[1:]
        print(filekey+' file has been recognized')
        print('--------------------------')
    else:
        print('Error, file type could not be recognized')
        print('--------------------------')
        sys.exit()
    return(filekey)


### read all metadata information
def readFRMmetadata(scan):
    """
    Read the medatadata 
    :param scan: a list of strings corresponding to each line of the cal file
    :return: a diectionnary with metadata names as keys and metadata information as values
    """
    metadata = {}
    for line in scan:
        RES = re.match(r'\[(.*?)\]', line)
        if RES is not None:
            metadatakey = RES.string[1:-1]
            if metadatakey[0:6] != "END_OF":
                ## store metadatakey and data from line below in a dictionnary
                index = scan.index(line)+1
                if index <= len(scan):
                    #print('metadata key is found ' + metadatakey)
                    metadata[metadatakey] = scan[index]
    print("The following metadata were found:")
    for k in metadata.keys():
        print(k + ': ' + metadata[k])
    print('--------------------------')
    return(metadata)

### Check that mandatory metadata are valid
def checkFRMmetadata(filekey, metadataQC, MANDATORY, OPTIONAL):
    """
    Determine if file contains enought metadata information
    :param filekey:  the keyword corresponding to file type (string)
    :param metadataQC: a dictionnary with metadata names as keys and "valid" or "not valid" as values
    :param MANDATORY: a dictionnary with file types keywords as kays and the list of mandatory metadata as values
    :Param OPTIONAL: a dictionnary with file types keywords as kays and the list of optional metadata as values
    :return: True if file contains enought information, process is stopped otherwhise
    """

    for met in MANDATORY[filekey]:
        try:
            metadataQC[met]
        except:
            print('Error: metadata '+met+' is mandatory but is not available')
            exit()
        else:
            if metadataQC[met] != 'valid':
                print('Error: metadata '+met+' is mandatory but is invalid')
                exit()

    for met in OPTIONAL[filekey]:
        try:
            metadataQC[met]
        except:
            print('Warning: optional metadata '+met+' is not available')
        else:
            if metadataQC[met] != 'valid':
                print('Warning: optional metadata '+met+' is invalid')
    return True
