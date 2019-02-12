# Validation configuration
Every in-situ measurement document entering the OC-DB system is validated 
against a list of rules before being accepted by the system. 
The validation rules can be freely configured using the configuration file 
"validation_config.json"

The validation system checks both header fields and measurement records 
using "Rules". Each rule relates to a section in the configuration file. 
Also, error and warning messages can be freely configured and associated 
to the rules.

The configuration file contains four major sections:

{  
"header": [],  
"record": [],  
"errors": [],  
"warnings": []  
}  
  
which are explained in detail in the following sections

## Header

## Records


# Improvements
* if a field of type obsolete is found it would be good to display the replacement 
in the message. Which is not supplied with the fcheck.ini


# Stuff we do not know to handle 

[general]

NAME             | VALUE

bathymetry_check | SRTM30_PLUS  # when changing this, make sure to update bad_bathymetry_header, as well.

strict_delim     | 1