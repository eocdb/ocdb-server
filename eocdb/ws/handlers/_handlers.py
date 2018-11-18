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


import tornado.escape
import tornado.httputil

from ..controllers.datasets import *
from ..controllers.docfiles import *
from ..controllers.service import *
from ..controllers.store import *
from ..controllers.users import *
from ..reqparams import RequestParams
from ..webservice import WsRequestHandler
from ...core.models.dataset import Dataset
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
class StoreUpload(WsRequestHandler):

    def post(self):
        """Provide API operation uploadStoreFiles()."""
        arguments = dict()
        files = dict()
        # transform body with mime-type multipart/form-data into arguments and files Dict
        tornado.httputil.parse_body_arguments(self.request.headers.get("Content-Type"),
                                              self.request.body,
                                              arguments,
                                              files)

        path = arguments.get("path")
        if isinstance(path, list):
            if len(path) != 1:
                raise WsBadRequestError(f"Invalid path argument in body: {repr(path)}")
            path = path[0]
        elif not isinstance(path, str):
            raise WsBadRequestError(f"Invalid path argument in body: {repr(path)}")

        if isinstance(path, bytes):
            path = path.decode("utf-8")

        dataset_files = []
        for file in files.get("dataset_files", []):
            dataset_files.append(UploadedFile.from_dict(file))

        doc_files = []
        for file in files.get("doc_files", []):
            doc_files.append(UploadedFile.from_dict(file))

        result = upload_store_files(self.ws_context, path, dataset_files, doc_files)
        # Note, result is a Dict[filename, DatasetValidationResult]
        self.finish(tornado.escape.json_encode({k: v.to_dict() for k, v in result.items()}))


# noinspection PyAbstractClass,PyShadowingBuiltins
class StoreDownload(WsRequestHandler):

    def get(self):
        """Provide API operation downloadStoreFiles()."""
        # noinspection PyBroadException,PyUnusedLocal
        expr = self.query.get_param('expr', default=None)
        region = self.query.get_param_float_list('region', default=None)
        time = self.query.get_param_list('time', default=None)
        wdepth = self.query.get_param_float_list('wdepth', default=None)
        mtype = self.query.get_param('mtype', default=MTYPE_DEFAULT)
        wlmode = self.query.get_param('wlmode', default=WLMODE_DEFAULT)
        shallow = self.query.get_param('shallow', default=SHALLOW_DEFAULT)
        pmode = self.query.get_param('pmode', default=PMODE_DEFAULT)
        pgroup = self.query.get_param_list('pgroup', default=None)
        pname = self.query.get_param_list('pname', default=None)
        docs = self.query.get_param_bool('docs', default=None)
        result = download_store_files(self.ws_context, expr=expr, region=region, time=time, wdepth=wdepth,
                                      mtype=mtype, wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup,
                                      pname=pname, docs=docs)
        # transform result of type str into response with mime-type application/octet-stream
        # TODO (generated): transform result first
        self.finish(result)


# noinspection PyAbstractClass
class DatasetsValidate(WsRequestHandler):

    def post(self):
        """Provide API operation validateDataset()."""
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
        time = self.query.get_param_list('time', default=None)
        wdepth = self.query.get_param_float_list('wdepth', default=None)
        mtype = self.query.get_param('mtype', default=None)
        wlmode = self.query.get_param('wlmode', default=None)
        shallow = self.query.get_param('shallow', default=None)
        pmode = self.query.get_param('pmode', default=None)
        pgroup = self.query.get_param_list('pgroup', default=None)
        pname = self.query.get_param_list('pname', default=None)
        offset = self.query.get_param_int('offset', default=None)
        count = self.query.get_param_int('count', default=None)
        result = find_datasets(self.ws_context, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype,
                               wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname,
                               offset=offset, count=count)
        # transform result of type DatasetQueryResult into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def put(self):
        """Provide API operation addDataset()."""
        # transform body with mime-type application/json into a Dataset
        data_dict = tornado.escape.json_decode(self.request.body)
        dataset = Dataset.from_dict(data_dict)
        result = add_dataset(self.ws_context, dataset=dataset)
        # transform result of type DatasetRef into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))
        self.finish()

    def post(self):
        """Provide API operation updateDataset()."""
        # transform body with mime-type application/json into a Dataset
        data_dict = tornado.escape.json_decode(self.request.body)
        dataset = Dataset.from_dict(data_dict)
        update_dataset(self.ws_context, dataset=dataset)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class DatasetsId(WsRequestHandler):

    def get(self, id: str):
        """Provide API operation getDatasetById()."""
        dataset_id = id
        result = get_dataset_by_id(self.ws_context, dataset_id=dataset_id)
        # transform result of type Dataset into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def delete(self, id: str):
        """Provide API operation deleteDataset()."""
        dataset_id = id
        api_key = self.header.get_param('api_key', default=None)
        delete_dataset(self.ws_context, dataset_id=dataset_id, api_key=api_key)
        self.finish()


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
        dataset_id = id
        # transform body with mime-type application/json into a QcInfo
        data_dict = tornado.escape.json_decode(self.request.body)
        qc_info = QcInfo.from_dict(data_dict)
        result = set_dataset_qc_info(self.ws_context, dataset_id=dataset_id, qc_info=qc_info)
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
        # transform body with mime-type application/json into a User
        data_dict = tornado.escape.json_decode(self.request.body)
        user = User.from_dict(data_dict)
        create_user(self.ws_context, user=user)


# noinspection PyAbstractClass,PyShadowingBuiltins
class UsersLogin(WsRequestHandler):

    def get(self):
        """Provide API operation loginUser()."""
        username = self.query.get_param('username', default=None)
        password = self.query.get_param('password', default=None)
        login_user(self.ws_context, username=username, password=password)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class UsersLogout(WsRequestHandler):

    def get(self):
        """Provide API operation logoutUser()."""
        logout_user(self.ws_context)
        self.finish()


# noinspection PyAbstractClass,PyShadowingBuiltins
class UsersId(WsRequestHandler):

    def get(self, id: str):
        """Provide API operation getUserByID()."""
        user_id = RequestParams.to_int('id', id)
        result = get_user_by_id(self.ws_context, user_id=user_id)
        # transform result of type User into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result.to_dict()))

    def put(self, id: str):
        """Provide API operation updateUser()."""
        user_id = RequestParams.to_int('id', id)
        # transform body with mime-type application/json into a User
        data_dict = tornado.escape.json_decode(self.request.body)
        data = User.from_dict(data_dict)
        update_user(self.ws_context, user_id=user_id, data=data)
        self.finish()

    def delete(self, id: str):
        """Provide API operation deleteUser()."""
        user_id = RequestParams.to_int('id', id)
        delete_user(self.ws_context, user_id=user_id)
        self.finish()
