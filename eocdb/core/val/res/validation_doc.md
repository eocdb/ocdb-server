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
  
which are explained in detail in the following sections.

## Header

This section in the configuration contains all checks to be executed on the 
measurement header entries. All checks need to be of one of the following 
rule types.

### field_required
Checks if a required field is present in the header information and that the field is 
not empty.  A miss of this rule always results in an error. Parameters are:


* **name**: denotes the name of the field. The name tag omits the forward slash and just 
contains the name
* **type**: always "field_required"
* **error**: the error message to be displayed, either direct or as a reference (see below).
Error messages can contain the tags
    * *{reference}*: resolves to the field name.  

Example:

    {
      "name": "investigators",
      "type": "field_required",
      "error": "@required_field_missing"
    }

### field_optional
Checks if an optional field is potentially present and if so that it is not empty. Issues a warning if field 
is empty. Parameters are:

* **name**: denotes the name of the field. The name tag omits the forward slash and just 
contains the name
* **type**: always "field_optional"
* **warning**: the warning message to be displayed, either direct or as a reference (see below).
Warning messages can contain the tags
    * *{reference}*: resolves to the field name.
    
Example:

    {
      "name": "station",
      "type": "field_optional",
      "warning": "@field_value_missing"
    }  




### field_obsolete
Check if an obsolete header field is present in the header. If so, a warning message is issued.
Parameters are:

* **name**: denotes the name of the field. The name tag omits the forward slash and just 
contains the name
* **type**: always "field_obsolete"
* **warning**: the warning message to be displayed, either direct or as a reference (see below).
Warning messages can contain the tags
    * *{reference}*: resolves to the field name.

Example:

    {
      "name": "station_alt_id",
      "type": "field_obsolete",
      "warning": "@obsolete_field"
    }
    
    

### field_compare 
Check that the values of header fields follow relational rules (e.g. stop day not before start day).
Parameters are:

* **reference_name**: denotes the name of the reference field. The name tag omits the forward slash and just 
contains the name
* **compare_name**: denotes the name of the comparand field. The name tag omits the forward slash and just 
contains the name
* **type**: always "field_compare"
* **operation**: one of the relational operators
    * \>=: greater than or equal
    * \>: greater than
    * !=: not equal
    * ==: equal
    * \<: lesser than 
    * \<=: lesser than or equal
* **data_type**: data type of the field value. Must be one of:
    * date: a date value formatted "YYYYmmdd"
    * number: a numerical value
    * string: a string value  
* **error**: the error message to be displayed, either direct or as a reference (see below).
Error messages can contain the tags
    * *{reference}*: resolves to the reference field name. 
    * *{ref_val}*: resolves to the value of the reference field. 
    * *{compare}*: resolves to the comparand field name. 
    * *{comp_val}*: resolves to the value of the comparand field.
* **warning**: the warning message to be displayed, either direct or as a reference (see below).
Warning messages are overridden if error is present. Warning messages can contain the tags
    * *{reference}*: resolves to the reference field name. 
    * *{ref_val}*: resolves to the value of the reference field. 
    * *{compare}*: resolves to the comparand field name. 
    * *{comp_val}*: resolves to the value of the comparand field.
    
Example:

    {
      "type": "field_compare",
      "reference": "start_date",
      "compare": "end_date",
      "operation": "<=",
      "data_type": "date",
      "error": "@header_start_after_finish"
    }


## Records

Checks on the record section cover two entities:
* the correct unit(s) as defined in the "units" header tag
* correct value ranges for all records

The check of the record content supports the following data types:

### Number record

### Date record

### String record


## Errors and Warnings

* messages list
* resolving engine - tags



# Improvements
* if a field of type obsolete is found it would be good to display the replacement 
in the message. Which is not supplied with the fcheck.ini


# Stuff we do not know to handle 

[general]

NAME             | VALUE

bathymetry_check | SRTM30_PLUS  # when changing this, make sure to update bad_bathymetry_header, as well.

strict_delim     | 1