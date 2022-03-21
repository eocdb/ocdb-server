# Changes in Version 0.1.19 (in development)

- The server can now correctly handle query parameters that are lists if numbers (i.e. int and float)
- The server can now also handle query parameters `user_id` and `wlmode`
- The query parameter `wdepth` is now handled correctly
- Added submission query parameters allowing filtering and sorting submissions

# Changes in Version 0.1.18

- Tightened user permissions in the docker image. A container will now be run as user `ocdb` and teh configs file is
  not writable for the ocdb user. 

# Changes in Version 0.1.17

- Changed static cookie secret in app.py to a random string [Issue 103](https://gitlab.eumetsat.int/OC/External/OC-DB/ocdb-webui/-/issues/103)
- The ocdb server is now preventing a Path Traversal vulnerability on the Submission
  File Upload & Download feature in multiple parameters [Issue 104](https://gitlab.eumetsat.int/OC/External/OC-DB/ocdb-webui/-/issues/104)
- The docker image uses now an alpine base image. These base images tend to be smaller and have therefore less 
  security issues

# Changes in Version 0.1.16

- Fixed login from WebUI

# Changes in Version 0.1.15

- Fixed 500 error thrown if the SB file contains a wrongly formatted datetime in the data section. Throws now a proper SbFormatError. This will also ensure that the error os reported.
- Ensured that the server does not throw a http 500 error if an optional field has not warning configured and a required field no error. The error report will include a message advising to contact teh admin die to a misconfigured validation json. 
- It is now possible to set a minimum client version. The Version is
  tested on login.

# Changes in Version 0.1.14

- Fixed update own pwd. Not duplicating users anymore

# Changes in Version 0.1.13

- Fixed issue that admin could not delete users
- Fixed listing datasets by submission

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