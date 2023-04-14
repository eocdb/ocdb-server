# Changes in Version 0.1.21
- FidRadDB interface added
  - possibility to upload Cal/Char files
    - only allowed for logged in users with the role "fidrad" or admins  
    - Cal/Char file validation
    - Use Metadata-key / File-type Matrix from Héloïse
    - Generating meaningful error messages
    - check for existing files
    - rename all files to upper case
    - create database entries per file
      - containing the filename, username, public: bool, utc_upload_time 
    - create history via logging with user integrated
    - allow to set a database property for "publish" or "not publish" a file
  - fetch a history tail
    - only allowed for logged in users with the role "fidrad" or admins  
    - with user-definable num lines
    - default: last 50 lines
  - grep like bottom up history search implemented
    - only allowed for logged in users with the role "fidrad" or admins  
    - with user-definable maximum number of results
    - default: 20 results
  - list files
    - allowed for everyone
      - Guest users only see public files in the list
      - Logged in users will see all public and own private files
      - Logged in admin will see all files in the list
  - download file
    - allowed for everyone
      - Guest users can only download public files
      - Logged in users can download public and own files
      - Logged in admin can download any files
  - delete file
    - only allowed for logged in users or admins  
    - Logged in users can delete own files
    - Logged in administrators can delete any files
- added library six to environment.yml

# Changes in Version 0.1.20
- upload file size ... maximum file size for upload changed from 8500000 to 40000000
- sb_file_reader ... Ensure that wrong time notation raises an error.
  see https://seabass.gsfc.nasa.gov/wiki/metadataheaders#start_date
- search ... Error fixed which occurred if one of the dates (from_date or to_date) was not set, but the other one was. 
- submissions ... if a user has both the submiter and the admin role, it was previously the case that users only saw
  their own submissions, although he should see all submissions as admin. This has been corrected.
- ensure that a user can see only own submissions. Except admin user.
- deployment date: FRM4SOC version 2.3 ??.??.????
- validator ... handling of suffixed var names corrected
- validator ... strip wavelength corrected
- several updates in validation_config.json see gitlab 14.11.2022
- sb_file_reader ... The splitting of data rows into columns has been changed so that data gaps can be detected.
  Previously, the exact position of the data gap could not be determined because the data gap was removed and thus the
  number of data in this data row was reduced. So far, it could only be determined that data is missing.
- sb_file_reader ... If values are missing in the data rows instead of marking them with the " missing " value, an error
  message is generated, informing the user in which row and column the data gap is located.
- sb_file_reader ... If header values can be interpreted as numbers, they will be read in as numerical values, not as
  strings.
- Fixing (#46) users cannot login anymore when details have changed using the ocdb-cli.
- Fixing (#36) credentials fail after using `ocdb-cli user udpate -k password -v newpassword`. User are now prevented
  using `udpate` for changing passwords. Users should use `ocdb-cli user pwd`.
- Restricted submission id to alphanumeric characters only. Required by security.

# Changes in Version 0.1.19

- The server can now correctly handle query parameters that are lists of numbers (i.e. int and float) (appeared during
  Issue #72 dependency updates)
- The server can now also handle query parameters `user_id` and `wlmode` (appeared during Issue #72 dependency updates)
- The query parameter `wdepth` is now handled correctly (appeared during Issue #72 dependency updates)
- Added submission query parameters allowing filtering and sorting submissions (appeared during Issue #72 dependency
  updates)
- Removed auto-loading of validation file. Does not work as the validation file is opened on validation in class
  Validation.
- Ensured that the bbox is translated correctly to an array (appeared during Issue #72 dependency updates)
- Added option DOTALL to regex validating the submission path and submission ID fixing security issues. Without
  DOTALL malicious code could be imputed after a new line to be executed on server side. (Reported by EUMETSAT IT
  document CERT-1057.doc)
- path and submission ID is now validated also in PUT operations. The path and submission ID could have been used
  to impute malicious code to be executed on server side. (Reported by EUMETSAT IT document CERT-1057.doc)
- Ensured that time ranges are sent as dates to the mongodb when filtering.
- Fixed error when user details are updated using the ocdb command line client. (#36)
- The validation process is now reports an error if the numbers of entries in rows in a dataframe does not correspond
  to the number of fields (closing #37 ocdb-client)

# Changes in Version 0.1.18

- This version has only been released as docker image which was an oversight as only the docker image bit not the
  actual software was changed.
- Tightened user permissions in the docker image. A container will now be run as user `ocdb` and the configs file is
  not writable for the ocdb user.

# Changes in Version 0.1.17

- Changed static cookie secret in app.py to a random
  string [Issue 103](https://gitlab.eumetsat.int/OC/External/OC-DB/ocdb-webui/-/issues/103)
- The ocdb server is now preventing a Path Traversal vulnerability on the Submission
  File Upload & Download feature in multiple
  parameters [Issue 104](https://gitlab.eumetsat.int/OC/External/OC-DB/ocdb-webui/-/issues/104)
- The docker image uses now an alpine base image. These base images tend to be smaller and have therefore less
  security issues

# Changes in Version 0.1.16

- Fixed login from WebUI

# Changes in Version 0.1.15

- Fixed 500 error thrown if the SB file contains a wrongly formatted datetime in the data section. Throws now a proper
  SbFormatError. This will also ensure that the error os reported.
- Ensured that the server does not throw a http 500 error if an optional field has not warning configured and a required
  field no error. The error report will include a message advising to contact teh admin die to a misconfigured
  validation json.
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

- Submission upload is now attempting to detect the charset of text
  files ([#6](https://gitlab.eumetsat.int/OC/External/OC-DB/ocdb-webui/issues/6)) 