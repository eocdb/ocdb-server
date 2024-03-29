# The MIT License (MIT)
# Copyright (c) 2018 by EUMETSAT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import functools
from time import strptime

import tornado.escape
import tornado.httputil

from ..controllers.datasets import *
from ..controllers.docfiles import *
from ..controllers.service import *
from ..controllers.store import *
from ..controllers.users import *
from ..utils import ensure_valid_submission_id, ensure_valid_path
from ..webservice import WsRequestHandler
from ...core.models.dataset_ids import DatasetIds

MTYPE_DEFAULT = 'all'
WLMODE_DEFAULT = 'all'
SHALLOW_DEFAULT = 'no'
PMODE_DEFAULT = 'contains'


# noinspection PyAbstractClass
class ServiceInfo(WsRequestHandler):
    def get(self):
        """Provide API operation getServiceInfo()."""
        result = get_service_info(self.ws_context)
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result))


# noinspection PyAbstractClass
class StoreInfo(WsRequestHandler):

    def get(self):
        """Provide API operation getStoreInfo()."""
        result = get_store_info(self.ws_context)
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result))


def _login_required(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        current_user_name = self.get_current_user()
        current_user = self.ws_context.get_user(current_user_name)

        if current_user is None:
            self.set_status(status_code=403, reason='Please login.')
            return

        func(self, *args, **kwargs)

    return wrapper


def _admin_required(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.has_admin_rights():
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

        func(self, *args, **kwargs)

    return wrapper


def _submission_send_authorization_required(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        allowed = False
        if self.has_admin_rights() or self.has_submit_rights():
            allowed = True

        if not allowed:
            self.set_status(status_code=403, reason='Not enough access rights to perform a submission')
            return

        func(self, *args, **kwargs)

    return wrapper


def _submission_authorization_required(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        current_user_name = self.get_current_user()

        submission_id = kwargs['submission_id'] if 'submission_id' in kwargs else None

        authorized = False
        if self.has_admin_rights():
            authorized = True
        elif self.has_submit_rights():
            submission = get_submission(ctx=self.ws_context, submission_id=submission_id)
            if not submission:
                self.set_status(status_code=404, reason=f'{submission_id} not found.')
                return

            if submission.user_id == current_user_name:
                authorized = True

        if not authorized:
            self.set_status(status_code=403, reason='Not enough access rights to perform operations on submission '
                                                    f'{submission_id}.')
            return

        func(self, *args, **kwargs)

    return wrapper


# noinspection PyAbstractClass,PyShadowingBuiltins
class HandleSubmission(WsRequestHandler):

    @_login_required
    @_submission_send_authorization_required
    def post(self):
        """Provide API operation uploadStoreFiles()."""
        user_name = self.get_current_user()

        arguments = dict()
        files = dict()
        # transform body with mime-type multipart/form-data into arguments and files Dict
        tornado.httputil.parse_body_arguments(self.request.headers.get("Content-Type"),
                                              self.request.body,
                                              arguments,
                                              files)

        submission_id = arguments.get("submissionid")
        submission_id = _ensure_string_argument(submission_id, "submissionid")
        ensure_valid_submission_id(submission_id)

        store_user_path = str(user_name) + "_" + submission_id

        path = arguments.get("path")
        path = _ensure_string_argument(path, "path")
        ensure_valid_path(path)

        publication_date = arguments.get("publicationdate")
        publication_date = _ensure_string_argument(publication_date, "publicationdate")
        if publication_date == "null" or publication_date == "None":
            publication_date = None
        # publication_date = datetime.datetime.strptime(publication_date, '%Y-%m-%dT%H:%M:%S')

        allow_publication = arguments.get("allowpublication")
        allow_publication = _ensure_string_argument(allow_publication, 'allowpublication')

        if allow_publication.lower() == 'true':
            allow_publication = True
        else:
            allow_publication = False

        dataset_files = []
        for file in files.get("datasetfiles", []):
            dataset_files.append(UploadedFile.from_dict(file))

        doc_files = []
        for file in files.get("docfiles", []):
            doc_files.append(UploadedFile.from_dict(file))

        result = upload_submission_files(ctx=self.ws_context,
                                         path=path,
                                         store_user_path=store_user_path,
                                         submission_id=submission_id,
                                         user_name=user_name,
                                         publication_date=publication_date,
                                         allow_publication=allow_publication,
                                         dataset_files=dataset_files,
                                         doc_files=doc_files)
        # Note, result is a Dict[filename, DatasetValidationResult]
        self.finish(tornado.escape.json_encode({k: v.to_dict() for k, v in result.items()}))

    @_login_required
    @_submission_authorization_required
    def delete(self, submission_id: str):
        submission = get_submission(ctx=self.ws_context, submission_id=submission_id)
        if submission is None:
            self.set_status(404, reason="Submission not found")
            return

        success = delete_submission(ctx=self.ws_context, submission_id=submission_id)
        if not success:
            self.set_status(400, reason="Error deleting submission")

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode({'message': f'{submission_id} deleted'}))

    @_login_required
    @_submission_authorization_required
    def get(self, submission_id: str):
        submission = get_submission(ctx=self.ws_context, submission_id=submission_id)

        if submission is None:
            self.set_status(404, reason="Submission not found")
            return

        sub_dict = submission.to_dict()
        if isinstance(sub_dict["date"], datetime.datetime):
            sub_dict["date"] = sub_dict["date"].isoformat()
        for f in sub_dict['files']:
            if 'creationdate' in f and isinstance(f['creationdate'], datetime.datetime):
                f['creationdate'] = f['creationdate'].isoformat()

        if sub_dict["publication_date"]:
            sub_dict["publication_date"] = sub_dict["publication_date"]

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(sub_dict))

    @_login_required
    @_submission_authorization_required
    def put(self, submission_id: str):
        user_name = self.get_current_user()
        user = self.ws_context.get_user(user_name)

        if user is not None:
            user_name = user.name
        else:
            user_name = 0

        submission = get_submission(ctx=self.ws_context, submission_id=submission_id)

        if submission is None:
            self.set_status(404, reason="Submission not found")
            return

        body_dict = tornado.escape.json_decode(self.request.body)
        new_submission_id = body_dict["submissionid"]
        new_submission_id = _ensure_string_argument(new_submission_id, "submissionid")
        ensure_valid_submission_id(new_submission_id)

        temp_area_path = str(user_name) + "_" + submission_id

        path = body_dict["path"]
        path = _ensure_string_argument(path, "path")
        ensure_valid_path(path)

        publication_date = body_dict["publicationdate"]
        if publication_date is not None:
            publication_date = _ensure_string_argument(publication_date, "publicationdate")

        allow_publication = body_dict["allowpublication"]

        # if not allow_publication:
        #    publication_date = None

        update_submission_files(ctx=self.ws_context,
                                path=path,
                                store_user_path=temp_area_path,
                                new_submission_id=new_submission_id,
                                submission_id=submission_id,
                                publication_date=publication_date,
                                allow_publication=allow_publication)

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode({'message': f'Submission {submission_id} updated'}))


# noinspection PyAbstractClass
class DownloadSubmissionFile(WsRequestHandler):
    @_login_required
    @_submission_authorization_required
    def get(self, submission_id: str, index: str):
        index = int(index)

        result = download_submission_file_by_id(self.ws_context, submission_id=submission_id, index=index)

        if not result:
            self.set_status(400, reason="Submission File not found")

        self._return_zip_file(result)
        self.finish()

    def _return_zip_file(self, result):
        if result is None:
            return

        self.set_header('Content-Type', 'application/zip')
        path, filename = os.path.split(result.filename)
        self.set_header("Content-Disposition", "attachment; filename=%s" % filename)
        self._stream_file_content(result)
        os.remove(result.filename)

    def _stream_file_content(self, result):
        with open(result.filename, 'rb') as f:
            while True:
                data = f.read(32768)
                if not data:
                    break
                self.write(data)


# Todo: The class UpdateSubmissionStatus is misleading and should be refactored to
#       UpdateSubmissionDetails (see name of former action button!).
#       If the code is correct, the action button might work again and could be enabled.
#       This class is called by two client actions:
#       - updateSubmissionStatus
#       - updateSubmissionDetails
#       If the class name will be changed in the future, take care that the url dispatching
#       is not broken. @see ws.handlers._mappings.py

# noinspection PyAbstractClass,PyShadowingBuiltins
class UpdateSubmissionStatus(WsRequestHandler):
    @_login_required
    @_submission_authorization_required
    def put(self, submission_id: str):

        submission = get_submission(ctx=self.ws_context, submission_id=submission_id)

        if submission is None:
            self.set_status(404, reason="Submission not found")
            return

        body_dict = tornado.escape.json_decode(self.request.body)
        # Todo se : Sabine, please assure that body_dict contains value publication date for key date!
        #           Let's discuss together if required.
        #           Submission has two date attributes: date and publication_data (see submission.py).
        #           _extract_date(body_dict) searches for 'date'! This might be correct, but is misleading.

        # Does the value None for key publication_date corresponds to and is interpreted as 'unset'?
        new_publication_date = self._extract_date(body_dict)
        if new_publication_date is None:
            # Todo se : Does this line really make sense? The method is also used when the user wants to change
            #  submission details. What if the user has intentionally set the publication date to None in order to
            #  remove the existing publication date?
            new_publication_date = submission.publication_date

        # Does the value None for the value of key status corresponds to and is interpreted as 'unset'?
        new_status = None
        if 'status' in body_dict:
            new_status = body_dict['status']

        if new_status is None:
            new_status = submission['status']

        try:
            success = update_submission(ctx=self.ws_context, submission=submission, status=new_status,
                                        publication_date=new_publication_date)
            if not success:
                self.set_status(400, reason="Error updating submission details (" + str(submission_id) + '/' +
                                            new_status + '/' + str(new_publication_date) + ')'
                                )

        except SbFormatError as e:
            self.set_status(403, reason="Error in data format. If status is VALIDATED please contact ops: " + str(e))

        self.finish(tornado.escape.json_encode({'message': f'Status of {submission_id} set to {new_status}'}))

    @staticmethod
    def _extract_date(body_dict):
        if "date" in body_dict:
            publication_date = strptime(body_dict["date"], "%Y%m%d")
        else:
            publication_date = None
        return publication_date


# noinspection PyAbstractClass
class GetSubmissions(WsRequestHandler):
    @_login_required
    # @_submission_authorization_required
    def get(self, user_name: str = None):
        offset = self.query.get_param_int('offset', default=None)
        count = self.query.get_param_int('count', default=None)
        query_column = self.query.get_param('query-column', default=None)
        query_value = self.query.get_param('query-value', default=None)
        query_operator = self.query.get_param('query-operator', default=None)
        if query_operator == 'is':
            if query_value in ['true', 'false']:
                query_value = self.query.to_bool('query_value', query_value)
            if query_value == '':
                query_value = None

        query_value = self.query.to_date('query_value', query_value, raises=False)

        sort_column = self.query.get_param('sort-column', default=None)
        sort_order = self.query.get_param('sort-order', default=None)

        current_user_name = self.get_current_user()
        if current_user_name != user_name:
            raise WsUnauthorizedError('User not allowed.')

        if self.has_admin_rights():
            user_id = None
        elif self.has_submit_rights():
            user_id = current_user_name
        else:
            raise WsUnauthorizedError('You are not allowed querying submissions.')

        result, tot_count = get_submissions(ctx=self.ws_context,
                                            user_id=user_id,
                                            offset=offset,
                                            count=count,
                                            query_column=query_column,
                                            query_value=query_value,
                                            query_operator=query_operator,
                                            sort_column=sort_column,
                                            sort_order=sort_order)

        result_list = []
        for submission in result:
            sub_dict = submission.to_dict()
            if isinstance(sub_dict["date"], datetime.datetime):
                sub_dict["date"] = sub_dict["date"].isoformat()

            if sub_dict["publication_date"]:
                sub_dict["publication_date"] = sub_dict["publication_date"]

            for file_ref in sub_dict['file_refs']:
                if isinstance(file_ref["creationdate"], datetime.datetime):
                    file_ref["creationdate"] = file_ref["creationdate"].isoformat()

            result_list.append(sub_dict)

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(
            {'submissions': result_list, 'tot_count': tot_count}
        ))


# noinspection PyAbstractClass
class HandleSubmissionFile(WsRequestHandler):
    @_login_required
    @_submission_authorization_required
    def get(self, submission_id: str, index: str):
        index = int(index)

        submission_file = get_submission_file(ctx=self.ws_context, submission_id=submission_id, index=index)

        if submission_file is not None:
            submission_file = submission_file.to_dict()
            submission_file['creationdate'] = submission_file['creationdate'].isoformat()

            self.set_header('Content-Type', 'application/json')
            self.finish(tornado.escape.json_encode(submission_file))
        else:
            self.set_status(400, reason="No result found")

    @_login_required
    @_submission_authorization_required
    def post(self, submission_id: str, typ: str):
        submission = get_submission(ctx=self.ws_context, submission_id=submission_id)

        if submission is None:
            self.set_status(404, reason="Submission not found")
            return

        arguments = dict()
        files = dict()
        # transform body with mime-type multipart/form-data into arguments and files Dict
        tornado.httputil.parse_body_arguments(self.request.headers.get("Content-Type"),
                                              self.request.body,
                                              arguments,
                                              files)
        files = files.get("files", [])
        num_files = len(files)

        if num_files != 1:
            self.set_status(400, reason="Invalid number of files supplied")
            return

        submission_file = get_submission_file_by_filename(ctx=self.ws_context, submission_id=submission_id,
                                                          file_name=files[0].filename)

        if not submission_file:
            add_submission_file(ctx=self.ws_context, submission=submission, file=files[0], typ=typ)
        else:
            self.set_status(400,
                            reason=f"File name {files[0].filename} "
                                   f"exists already in submission. Please use re-upload feature")
            return

        self.set_status(200, reason="OK")

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode({'Message': f'File {files[0].filename} added.'}))

    @_login_required
    @_submission_authorization_required
    def put(self, submission_id: str, index: str):
        submission = get_submission(ctx=self.ws_context, submission_id=submission_id)
        if submission is None:
            self.set_status(404, reason="Submission not found")
            return

        index = int(index)

        if index >= len(submission.files) or index < 0:
            self.set_status(400, reason="Invalid submission file index")
            return

        sb_file = get_submission_file(ctx=self.ws_context, submission_id=submission_id, index=index)

        arguments = dict()
        files = dict()
        # transform body with mime-type multipart/form-data into arguments and files Dict
        tornado.httputil.parse_body_arguments(self.request.headers.get("Content-Type"),
                                              self.request.body,
                                              arguments,
                                              files)
        files = files.get("files", [])
        num_files = len(files)

        if num_files != 1:
            self.set_status(400, reason="Invalid number of files supplied")
            return

        result = update_submission_file(ctx=self.ws_context, submission=submission, index=index, file=files[0],
                                        typ=sb_file.filetype)
        if result is None:
            return

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    @_login_required
    @_submission_authorization_required
    def delete(self, submission_id: str, index: str):
        submission = get_submission(ctx=self.ws_context, submission_id=submission_id)
        if submission is None:
            self.set_status(404, reason="Submission not found")
            return

        index = int(index)
        if index >= len(submission.files) or index < 0:
            self.set_status(400, reason="Invalid submission file index")
            return

        result = delete_submission_file(ctx=self.ws_context, submission=submission, index=index)
        if result:
            self.set_status(200, reason="OK")
        else:
            self.set_status(400, reason="Database error")


class Handledecode(WsRequestHandler):
    # def options(self):
    #    print('Hello')

    def get(self):
        print(self.request.headers.get('Authorization'))
        print('Hello')


# noinspection PyAbstractClass
class UpdateSubmissionFileStatus(WsRequestHandler):
    @_login_required
    @_submission_authorization_required
    def get(self, submission_id: str, index: str, status: str):
        submission = get_submission(ctx=self.ws_context, submission_id=submission_id)
        if submission is None:
            self.set_status(404, reason="Submission not found")
            return

        index = int(index)
        if index >= len(submission.files) or index < 0:
            self.set_status(400, reason="Invalid submission file index")
            return

        result = update_submission_file_status(ctx=self.ws_context, submission=submission, index=index, status=status)
        if result:
            self.set_status(200, reason="OK")
        else:
            self.set_status(400, reason="Database error")


# noinspection PyAbstractClass,PyShadowingBuiltins
class StoreDownload(WsRequestHandler):
    def get(self):
        """Provide API operation downloadStoreFiles()."""
        # noinspection PyBroadException,PyUnusedLocal
        # For details see: https://ocdb.readthedocs.io/en/latest/ocdb-api-cli.html
        expr = self.query.get_param('expr', default=None)                     # Looks for any files containing any of the words passed. Also, Lucene syntax can be used
        region = self.query.get_param_float_list('region', default=None)      # Looks for files containing measurements collected in the polygon defined by specified coordinates (format: “[West],[South],[East],[North]”)
        # Todo: Check, whether it's s_time or start_time
        s_time = self.query.get_param_list('time', default=None)              # Looks for any files containing measurement collected later than the selected date (format: “2016-07-01”)
        # Todo: Check, whether it's e_time or end_time
        # e_time = self.query.get_param_list('time', default=None)              # Looks for any files containing measurement collected earlier than the selected date (format: “2016-07-01”)
        wdepth = self.query.get_param_float_list('wdepth', default=None)      # Looks for any files containing measurements collected within the defined range of water (bottom) depth (format:”[[min_depth],[max_depth]]”)
        mtype = self.query.get_param('mtype', default=MTYPE_DEFAULT)          # Measurement type: Filters radiometric data depending on wavelength option. Could be ‘all’, ‘multispectral’ or ‘hyperspectral’
        wlmode = self.query.get_param('wlmode', default=WLMODE_DEFAULT)       #
        shallow = self.query.get_param('shallow', default=SHALLOW_DEFAULT)    # Shallow waters: Set to ‘yes’ to include also measurements indicated as done in shallow waters by the PIs (Default is ‘no’)
        # Can be set either to ‘contains’ (to filter results based on selected pgroup or variables), or
        # to ‘same_cruise’ (to include measurements from cruise during which __all__ the selected groups/variables were acquired), or
        # to ‘do_not_filter’ (to not filter results at all)
        pmode = self.query.get_param('pmode', default=PMODE_DEFAULT)
        pgroup = self.query.get_param_list('pgroup', default=None)            # Parameter group: Looks for files containing only certain geophysical variable types. Refer to [Search](ocdb-search.md) chapter for the complete list
        pname = self.query.get_param_list('pname', default=None)              # Parameter (Variable): Looks for files containing only the specified variables. A complete list of queryable variables are available [here](ocdb-standard-field-unit.md)
        docs = self.query.get_param_bool('docs', default=None)                # Shall documents be downloaded as well?

        result = download_store_files(self.ws_context, expr=expr, region=region, s_time=s_time, wdepth=wdepth,
                                      mtype=mtype, wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup,
                                      pname=pname, docs=docs)

        self._return_zip_file(result)
        self.finish(tornado.escape.json_encode({'message': 'File downloaded'}))

    def post(self):
        id_list_dict = tornado.escape.json_decode(self.request.body)
        dataset_ids = DatasetIds.from_dict(id_list_dict)
        result = download_store_files_by_id(self.ws_context, dataset_ids=dataset_ids.id_list, docs=dataset_ids.docs)

        self._return_zip_file(result)
        self.finish()

    def _return_zip_file(self, result):
        if result is None:
            return

        self.set_header('Content-Type', 'application/zip')
        path, filename = os.path.split(result.filename)
        self.set_header("Content-Disposition", "attachment; filename=%s" % filename)
        self._stream_file_content(result)
        os.remove(result.filename)

    def _stream_file_content(self, result):
        with open(result.filename, 'rb') as f:
            while True:
                data = f.read(32768)
                if not data:
                    break
                self.write(data)


# noinspection PyAbstractClass
class ValidateSubmission(WsRequestHandler):
    @_login_required
    def post(self):
        """Provide API operation validateDataset()."""
        # transform body with mime-type application/json into a Dataset
        data_dict = tornado.escape.json_decode(self.request.body)
        self.set_header('Content-Type', 'application/json')

        dataset = SbFileReader().read(io.StringIO(data_dict['data']))
        # dataset = Dataset.from_dict(data_dict)
        result = validate_dataset(self.ws_context, dataset=dataset)
        # transform result of type DatasetValidationResult into response with mime-type application/json
        self.finish(tornado.escape.json_encode(result.to_dict()))


# noinspection PyAbstractClass
class Datasets(WsRequestHandler):
    def get(self):
        """Provide API operation findDatasets()."""
        # noinspection PyBroadException,PyUnusedLocal
        expr = self.query.get_param('expr', default=None)
        region = self.query.get_param_float_list('region', default=None)
        tim = self.extract_time()
        wdepth = self.query.get_param_float_list('wdepth', default=None)
        submission_id = self.query.get_param('submission_id', default=None)
        status = self.query.get_param('status', default=None)
        mtype = self.query.get_param('mtype', default=MTYPE_DEFAULT)
        wlmode = self.query.get_param('wlmode', default=None)
        shallow = self.query.get_param('shallow', default=SHALLOW_DEFAULT)
        pmode = self.query.get_param('pmode', default=PMODE_DEFAULT)
        pgroup = self.query.get_param_list('pgroup', default=None)
        pname = self.query.get_param_list('pname', default=None)
        geojson = self.query.get_param_bool('geojson', default=False)
        offset = self.query.get_param_int('offset', default=None)
        count = self.query.get_param_int('count', default=None)
        user_id = self.query.get_param('user_id', default=None)

        if self.has_admin_rights():
            status = None
            user_id = None
        else:
            status = 'PUBLISHED'

        try:
            result = find_datasets(self.ws_context, expr=expr, region=region, time=tim, wdepth=wdepth, mtype=mtype,
                                   wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname,
                                   submission_id=submission_id, status=status,
                                   offset=offset, count=count, geojson=geojson, user_id=user_id)
        except Exception as e:
            self.set_status(status_code=403, reason=str(e))
            return

        # transform result of type DatasetQueryResult into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def extract_time(self):
        start_time = self.query.get_param('start_time', default=None)
        end_time = self.query.get_param('end_time', default=None)
        if start_time is not None or end_time is not None:
            if start_time is not None:
                start_time = self.query.to_date('start_time', start_time + "T00:00", raises=True)

            if end_time is not None:
                end_time = self.query.to_date('end_time', end_time + "T23:59", raises=True)
            t = [start_time, end_time]
        else:
            t = None
        return t


# noinspection PyAbstractClass,PyShadowingBuiltins
class GetDatasetsById(WsRequestHandler):

    def get(self, id: str):
        """Provide API operation getDatasetById()."""
        dataset_id = id
        result = get_dataset_by_id_strict(self.ws_context, dataset_id=dataset_id)
        # transform result of type Dataset into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def delete(self, id: str):
        """Provide API operation deleteDataset()."""
        if not self.has_admin_rights():
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

        dataset_id = id
        delete_dataset(self.ws_context, dataset_id=dataset_id, )
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class GetDatasetsBySubmissionId(WsRequestHandler):

    def get(self, submission_id: str):
        """Provide API operation getDatasetById()."""
        result = find_datasets(self.ws_context, submission_id=submission_id)
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    @_login_required
    @_admin_required
    def delete(self, submission_id: str):
        """Provide API operation deleteDatasets by submission ID()."""
        result = find_datasets(self.ws_context, submission_id=submission_id)
        for ds in result.datasets:
            delete_dataset(ctx=self.ws_context, dataset_id=ds.id)

        self.finish(tornado.escape.json_encode(
            {'message': f'{result.total_count} Datasets for {submission_id} deleted'})
        )


# noinspection PyAbstractClass,PyShadowingBuiltins
class DatasetsAffilProjectCruise(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str):
        """Provide API operation getDatasetsInBucket()."""
        result = get_datasets_in_path(self.ws_context, affil=affil, project=project, cruise=cruise)
        # transform result of type List[DatasetRef] into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode([item.to_dict() for item in result]))


# noinspection PyAbstractClass,PyShadowingBuiltins
class DatasetsAffilProjectCruiseName(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str, name: str):
        """Provide API operation getDatasetByBucketAndName()."""
        result = get_dataset_by_name(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)
        # transform result of type str into response with mime-type text/plain
        self.set_header('Content-Type', 'text/plain')
        self.finish(result)


# noinspection PyAbstractClass,PyShadowingBuiltins
class DatasetsIdQcinfo(WsRequestHandler):

    def get(self, id: str):
        """Provide API operation getDatasetQcInfo()."""
        dataset_id = id
        result = get_dataset_qc_info(self.ws_context, dataset_id=dataset_id)
        # transform result of type QcInfo into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def post(self, id: str):
        """Provide API operation setDatasetQcInfo()."""
        if not self.has_admin_rights():
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

        dataset_id = id
        # transform body with mime-type application/json into a QcInfo
        data_dict = tornado.escape.json_decode(self.request.body)
        qc_info = QcInfo.from_dict(data_dict)
        set_dataset_qc_info(self.ws_context, dataset_id=dataset_id, qc_info=qc_info)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class Docfiles(WsRequestHandler):

    def put(self):
        """Provide API operation addDocFile()."""
        # transform body with mime-type multipart/form-data into a Dict
        # TODO (generated): transform self.request.body first
        data = self.request.body
        add_doc_file(self.ws_context, data=data)
        self.finish()

    def post(self):
        """Provide API operation updateDocFile()."""
        # transform body with mime-type multipart/form-data into a Dict
        # TODO (generated): transform self.request.body first
        data = self.request.body
        update_doc_file(self.ws_context, data=data)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class DocfilesAffilProjectCruise(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str):
        """Provide API operation getDocFilesInPath()."""
        result = get_doc_files_in_path(self.ws_context, affil=affil, project=project, cruise=cruise)
        # transform result of type List[DocFileRef] into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode([item.to_dict() for item in result]))


# noinspection PyAbstractClass,PyShadowingBuiltins
class DocfilesAffilProjectCruiseName(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str, name: str):
        """Provide API operation getDocFileByName()."""
        result = get_doc_file_by_name(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)
        # transform result of type bytes into response with mime-type application/octet-stream
        self.set_header('Content-Type', 'application/octet-stream')
        self.finish(result)

    def delete(self, affil: str, project: str, cruise: str, name: str):
        """Provide API operation deleteDocFile()."""
        delete_doc_file(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class HandleMatchupFiles(WsRequestHandler):
    def get(self):
        import ftptool

        a_host = ftptool.FTPHost.connect("ftp.eumetsat.int", user="anonymous", password="hdzierz@gmail.com")
        a_host.current_directory = '/pub/RSP/OLCI_MATCHUPS'

        data = []
        for (dirname, subdirs, files) in a_host.walk('/pub/RSP/OLCI_MATCHUPS'):
            for f in files:
                data.append({'dirname': dirname, 'filename': f})

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(data))


def _ensure_string_argument(arg_value, arg_name: str):
    if isinstance(arg_value, list):
        if len(arg_value) != 1:
            raise WsBadRequestError(f"Invalid argument '{arg_name}' in body: {repr(arg_value)}")
        arg_value = arg_value[0]

    if isinstance(arg_value, bytes):
        arg_value = arg_value.decode("utf-8")

    if not isinstance(arg_value, str):
        raise WsBadRequestError(f"Invalid argument '{arg_name}' in body: {repr(arg_value)}")

    return arg_value


def _ensure_int_argument(arg_value, arg_name: str):
    if isinstance(arg_value, list):
        if len(arg_value) != 1:
            raise WsBadRequestError(f"Invalid argument '{arg_name}' in body: {repr(arg_value)}")
        arg_value = arg_value[0]
    if not isinstance(arg_value, int):
        raise WsBadRequestError(f"Invalid argument '{arg_name}' in body: {repr(arg_value)}")

    return arg_value
