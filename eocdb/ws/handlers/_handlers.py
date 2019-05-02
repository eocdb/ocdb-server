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
from time import strptime

import tornado.escape
import tornado.httputil

from eocdb.core.db.db_user import DbUser
from eocdb.ws.controllers.links import get_links, update_links
from ..controllers.datasets import *
from ..controllers.docfiles import *
from ..controllers.service import *
from ..controllers.store import *
from ..controllers.users import *
from ..webservice import WsRequestHandler
from ...core.models.dataset import Dataset
from ...core.models.dataset_ids import DatasetIds
from ...core.models.user import User

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


# noinspection PyAbstractClass,PyShadowingBuiltins
class StoreUploadSubmission(WsRequestHandler):

    def post(self):
        """Provide API operation uploadStoreFiles()."""

        # @todo 1 tb/tb fetch current user ID and assemble path into temp-storage
        # return if user not set - prevent from unauthorized uploads
        # self.current_user
        # user_id = 8877827454

        arguments = dict()
        files = dict()
        # transform body with mime-type multipart/form-data into arguments and files Dict
        tornado.httputil.parse_body_arguments(self.request.headers.get("Content-Type"),
                                              self.request.body,
                                              arguments,
                                              files)

        submission_id = arguments.get("submissionid")
        submission_id = _ensure_string_argument(submission_id, "submissionid")

        user_id = arguments.get("userid")
        user_id = _ensure_string_argument(user_id, "userid")

        temp_area_path = str(user_id) + "_" + submission_id

        path = arguments.get("path")
        path = _ensure_string_argument(path, "path")
        target_path = os.path.join(temp_area_path, path)

        publication_date = arguments.get("publicationdate")
        publication_date = _ensure_string_argument(publication_date, "publicationdate")
        # publication_date = datetime.datetime.strptime(publication_date, '%Y-%m-%dT%H:%M:%S')

        allow_publication = arguments.get("allowpublication")
        allow_publication = _ensure_string_argument(allow_publication, 'allowpublication')

        if allow_publication == 'true':
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
                                         path=target_path,
                                         submission_id=submission_id,
                                         user_id=user_id,
                                         publication_date=publication_date,
                                         allow_publication=allow_publication,
                                         dataset_files=dataset_files,
                                         doc_files=doc_files)
        # Note, result is a Dict[filename, DatasetValidationResult]
        self.finish(tornado.escape.json_encode({k: v.to_dict() for k, v in result.items()}))

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

    def get(self, submission_id: str):
        submission = get_submission(ctx=self.ws_context, submission_id=submission_id)

        if submission is None:
            self.set_status(404, reason="Submission not found")
            return

        sub_dict = submission.to_dict()
        sub_dict["date"] = sub_dict["date"].isoformat()

        if sub_dict["publication_date"]:
            sub_dict["publication_date"] = sub_dict["publication_date"]

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(sub_dict))


# noinspection PyAbstractClass
class StoreDownloadsubmissionFile(WsRequestHandler):
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


# noinspection PyAbstractClass,PyShadowingBuiltins
class StoreStatusSubmission(WsRequestHandler):

    def put(self, submission_id: str):
        user_name = self.get_current_user()
        if not (self.has_admin_rights() or self.is_self(user_name)):
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

        submission = get_submission(ctx=self.ws_context, submission_id=submission_id)
        if submission is None:
            self.set_status(404, reason="Submission not found")
            return

        body_dict = tornado.escape.json_decode(self.request.body)
        status = body_dict["status"]
        publication_date = self._extract_date(body_dict)

        success = update_submission(ctx=self.ws_context, submission=submission, status=status,
                                    publication_date=publication_date)
        if not success:
            self.set_status(400, reason="Error updating submission")

        self.finish(tornado.escape.json_encode({'message': f'Status of {submission_id} set to {status}'}))

    @staticmethod
    def _extract_date(body_dict):
        if "date" in body_dict:
            publication_date = strptime(body_dict["date"], "%Y%m%d")
        else:
            publication_date = None
        return publication_date


# noinspection PyAbstractClass
class StoreUploadUser(WsRequestHandler):

    def get(self, userid: str):
        result = get_submissions(ctx=self.ws_context, user_id=userid)

        result_list = []
        for submission in result:
            sub_dict = submission.to_dict()
            sub_dict["date"] = sub_dict["date"].isoformat()
            if sub_dict["publication_date"]:
                sub_dict["publication_date"] = sub_dict["publication_date"]
            result_list.append(sub_dict)

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result_list))


# noinspection PyAbstractClass
class StoreUploadSubmissionFile(WsRequestHandler):

    def get(self, submission_id: str, index: str):
        user_name = self.get_current_user()
        if not (self.has_admin_rights() or self.is_self(user_name)):
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

        index = int(index)

        submission_file = get_submission_file(ctx=self.ws_context, submission_id=submission_id, index=index)
        if submission_file is not None:
            self.set_header('Content-Type', 'application/json')
            self.finish(tornado.escape.json_encode(submission_file.to_dict()))
        else:
            self.set_status(400, reason="No result found")

    def put(self, submission_id: str, index: str):
        user_name = self.get_current_user()
        if not (self.has_admin_rights() or self.is_self(user_name)):
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

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

        #if result.status is not "OK":
        #    self.set_status(400, reason="Validation Error")

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def delete(self, submission_id: str, index: str):
        user_name = self.get_current_user()
        if not (self.has_admin_rights() or self.is_self(user_name)):
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

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


# noinspection PyAbstractClass
class StoreUpdateSubmissionFile(WsRequestHandler):

    def get(self, submission_id: str, index: str, status: str):
        user_name = self.get_current_user()
        if not (self.has_admin_rights() or self.is_self(user_name)):
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

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
        expr = self.query.get_param('expr', default=None)
        region = self.query.get_param_float_list('region', default=None)
        s_time = self.query.get_param_list('time', default=None)
        wdepth = self.query.get_param_float_list('wdepth', default=None)
        mtype = self.query.get_param('mtype', default=MTYPE_DEFAULT)
        wlmode = self.query.get_param('wlmode', default=WLMODE_DEFAULT)
        shallow = self.query.get_param('shallow', default=SHALLOW_DEFAULT)
        pmode = self.query.get_param('pmode', default=PMODE_DEFAULT)
        pgroup = self.query.get_param_list('pgroup', default=None)
        pname = self.query.get_param_list('pname', default=None)
        docs = self.query.get_param_bool('docs', default=None)

        result = download_store_files(self.ws_context, expr=expr, region=region, s_time=s_time, wdepth=wdepth,
                                      mtype=mtype, wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup,
                                      pname=pname, docs=docs)

        self._return_zip_file(result)
        self.finish()

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
class DatasetsValidate(WsRequestHandler):

    def post(self):
        """Provide API operation validateDataset()."""
        if not self.has_admin_rights():
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

        # transform body with mime-type application/json into a Dataset
        data_dict = tornado.escape.json_decode(self.request.body)
        dataset = Dataset.from_dict(data_dict)
        result = validate_dataset(self.ws_context, dataset=dataset)
        # transform result of type DatasetValidationResult into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))


# noinspection PyAbstractClass
class Datasets(WsRequestHandler):

    def get(self):
        """Provide API operation findDatasets()."""
        # noinspection PyBroadException,PyUnusedLocal
        expr = self.query.get_param('expr', default=None)
        region = self.query.get_param_float_list('region', default=None)
        time = self.extract_time()
        wdepth = self.query.get_param_float_list('wdepth', default=None)
        submission_id = self.query.get_param('submission_id', default=None)
        #user_id = self.query.get_param_int('user_id', default=None)
        status = self.query.get_param('status', default=None)
        mtype = self.query.get_param('mtype', default=MTYPE_DEFAULT)
        wlmode = self.query.get_param('wlmode', default=WLMODE_DEFAULT)
        shallow = self.query.get_param('shallow', default=SHALLOW_DEFAULT)
        pmode = self.query.get_param('pmode', default=PMODE_DEFAULT)
        pgroup = self.query.get_param_list('pgroup', default=None)
        pname = self.query.get_param_list('pname', default=None)
        geojson = self.query.get_param_bool('geojson', default=False)
        offset = self.query.get_param_int('offset', default=None)
        count = self.query.get_param_int('count', default=None)
        result = find_datasets(self.ws_context, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype,
                               wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname,
                               submission_id=submission_id, status=status,
                               offset=offset, count=count, geojson=geojson)
        # transform result of type DatasetQueryResult into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def extract_time(self):
        start_time = self.query.get_param('start_time', default=None)
        end_time = self.query.get_param('end_time', default=None)
        if start_time is not None or end_time is not None:
            time = [start_time, end_time]
        else:
            time = None
        return time


# noinspection PyAbstractClass,PyShadowingBuiltins
class DatasetsId(WsRequestHandler):

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
        delete_dataset(self.ws_context, dataset_id=dataset_id,)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class DatasetsSubmissionId(WsRequestHandler):

    def get(self, submissionid: str):
        """Provide API operation getDatasetById()."""
        result = find_datasets(self.ws_context, submission_id=submissionid)
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def delete(self, submissionid: str):
        """Provide API operation deleteDatasets by submission ID()."""
        result = find_datasets(self.ws_context, submission_id=submissionid)
        api_key = self.header.get_param('api_key', default=None)
        for ds in result.datasets:
            delete_dataset(ctx=self.ws_context, dataset_id=ds.id, api_key=api_key)

        self.finish(tornado.escape.json_encode({'message': f'Datasets for {submissionid} deleted'}))


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
class Users(WsRequestHandler):

    def post(self):
        """Provide API operation createUser()."""
        if not self.has_admin_rights():
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

        # transform body with mime-type application/json into a User
        data_dict = tornado.escape.json_decode(self.request.body)
        user = User.from_dict(data_dict)
        create_user(self.ws_context, user=user)

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode({'message': f'User {user.name} added'}))


# noinspection PyAbstractClass,PyShadowingBuiltins
class UsersLogin(WsRequestHandler):

    def post(self):
        """Provide API operation loginUser()."""
        credentials = tornado.escape.json_decode(self.request.body)
        username = credentials.get('username')
        password = credentials.get('password')
        user_info = login_user(self.ws_context, username=username, password=password)
        if user_info is not None:
            self.set_secure_cookie("user", username, expires_days=1)

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(user_info))


# noinspection PyAbstractClass,PyShadowingBuiltins
class UsersLogout(WsRequestHandler):

    def get(self):
        current_user = self.get_current_user()
        if current_user is not None:
            self.clear_cookie("user")
            return self.finish(tornado.escape.json_encode({'message': f'User {current_user} logged out'}))

        return self.finish(tornado.escape.json_encode({'message': f'No user logged in'}))


# noinspection PyAbstractClass,PyShadowingBuiltins
class UsersId(WsRequestHandler):

    def get(self, user_name: str):
        """Provide API operation getUserByID()."""
        if not(self.has_admin_rights() or
               self.is_self(user_name)):
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

        result = get_user_by_name(self.ws_context, user_name=user_name)
        # transform result of type User into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result))

    def put(self, user_name: str):
        """Provide API operation updateUser()."""
        if not self.has_admin_rights():
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

        # transform body with mime-type application/json into a User
        data_dict = tornado.escape.json_decode(self.request.body)
        data = DbUser.from_dict(data_dict)
        update_user(self.ws_context, user_name=user_name, data=data)
        self.finish(tornado.escape.json_encode({'message': f'User {user_name} updated'}))

    def delete(self, user_name: str):
        """Provide API operation deleteUser()."""
        if not self.has_admin_rights():
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

        delete_user(self.ws_context, user_name)

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode({'message': f'User {user_name} deleted'}))


# noinspection PyAbstractClass
class Links(WsRequestHandler):
    def get(self):
        result = get_links(self.ws_context)
        self.set_header('Content-Type', 'application/txt')
        self.finish(tornado.escape.json_encode({'content': result}))

    def post(self):
        result = tornado.escape.json_decode(self.request.body)

        content = result['content']

        result = update_links(self.ws_context, content)
        self.set_header('Content-Type', 'application/txt')
        self.finish(result)


def _ensure_string_argument(arg_value, arg_name: str):
    if isinstance(arg_value, list):
        if len(arg_value) != 1:
            raise WsBadRequestError(f"Invalid argument '{arg_name}' in body: {repr(arg_value)}")
        arg_value = arg_value[0]
    elif not (isinstance(arg_value, str) or isinstance(arg_value, bytes)):
        raise WsBadRequestError(f"Invalid argument '{arg_name}' in body: {repr(arg_value)}")

    if isinstance(arg_value, bytes):
        arg_value = arg_value.decode("utf-8")

    return arg_value


def _ensure_int_argument(arg_value, arg_name: str):
    if isinstance(arg_value, list):
        if len(arg_value) != 1:
            raise WsBadRequestError(f"Invalid argument '{arg_name}' in body: {repr(arg_value)}")
        arg_value = arg_value[0]
    elif not isinstance(arg_value, int):
        raise WsBadRequestError(f"Invalid argument '{arg_name}' in body: {repr(arg_value)}")

    return arg_value
