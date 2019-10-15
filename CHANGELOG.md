# Changes in Version 0.1.9

- Fixed submit users not able to list their submissions

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