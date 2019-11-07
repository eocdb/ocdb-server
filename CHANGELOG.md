# Changes in Version 0.1.12

- Fixed check admin check not working

# Changes in Version 0.1.11

- Ensured that datasets attributes are always lower case
- Removed static OCDB website

# Changes in Version 0.1.10

- Submission: Fixed downloading of added document files

# Changes in Version 0.1.9

- Fixed submit users not able to list their submissions
- Fixed [authorisation issues](https://gitlab.eumetsat.int/OC/External/OC-DB/ocdb-client/issues/23)

# Changes in Version 0.1.8

- Introduced an API_VERSION_TAG and set it to latest. Ensures that software does
  not fail due to a change in version during the maintenance phase 
- Ensures now None publication dates on submission with null publication date

# Changes in Version 0.1.7

- The system allows now adding submission files to a submission
- A user can now validate a single submission file independent of submitting
- The function download_datasets does now accept a dataset object as well as id strings
 

# Changes in Version 0.1.6

- Submission upload is now attempting to detect the charset of text files ([#6](https://gitlab.eumetsat.int/OC/External/OC-DB/ocdb-webui/issues/6)) 