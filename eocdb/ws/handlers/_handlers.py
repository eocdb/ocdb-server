import tornado.escape

from ..webservice import WsRequestHandler
from ..reqparams import RequestParams
from ..controllers.datasets import *
from ..controllers.docfiles import *
from ..controllers.store import *
from ..controllers.users import *


# noinspection PyAbstractClass
class StoreInfo(WsRequestHandler):

    def get(self):
        """Provide API operation getStoreInfo()."""
        try:
            result = get_store_info(self.ws_context)

            # transform result of type Dict into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result))

        finally:
            self.finish()


# noinspection PyAbstractClass
class StoreUpload(WsRequestHandler):

    def post(self):
        """Provide API operation uploadStoreFiles()."""
        try:
            # transform body with mime-type multipart/form-data into a Dict
            # TODO: transform self.request.body first
            data = self.request.body

            result = upload_store_files(self.ws_context, data=data)

            # transform result of type ApiResponse into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()


# noinspection PyAbstractClass
class StoreDownload(WsRequestHandler):

    def get(self):
        """Provide API operation downloadStoreFiles()."""
        try:
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
            docs = self.query.get_param_bool('docs', default=None)
            result = download_store_files(self.ws_context, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype, wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname, docs=docs)

            # transform result of type str into response with mime-type application/octet-stream
            # TODO: transform result first
            self.write(result)

        finally:
            self.finish()


# noinspection PyAbstractClass
class Datasets(WsRequestHandler):

    def get(self):
        """Provide API operation findDatasets()."""
        try:
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
            result = find_datasets(self.ws_context, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype, wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname, offset=offset, count=count)

            # transform result of type DatasetQueryResult into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()

    def put(self):
        """Provide API operation updateDataset()."""
        try:
            # transform body with mime-type application/json into a Dataset
            data_dict = tornado.escape.json_decode(self.request.body)
            data = Dataset.from_dict(data_dict)

            result = update_dataset(self.ws_context, data=data)

            # transform result of type ApiResponse into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()

    def post(self):
        """Provide API operation addDataset()."""
        try:
            # transform body with mime-type application/json into a Dataset
            data_dict = tornado.escape.json_decode(self.request.body)
            data = Dataset.from_dict(data_dict)

            result = add_dataset(self.ws_context, data=data)

            # transform result of type ApiResponse into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()


# noinspection PyAbstractClass
class DatasetsId(WsRequestHandler):

    def get(self, id: str):
        """Provide API operation getDatasetById()."""
        try:
            id_ = id
            result = get_dataset_by_id(self.ws_context, id_=id_)

            # transform result of type Dataset into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()

    def delete(self, id: str):
        """Provide API operation deleteDataset()."""
        try:
            id_ = id
            api_key = self.header.get_param('api_key', default=None)
            result = delete_dataset(self.ws_context, id_=id_, api_key=api_key)

            # transform result of type ApiResponse into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()


# noinspection PyAbstractClass
class DatasetsAffilProjectCruise(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str):
        """Provide API operation getDatasetsInBucket()."""
        try:
            result = get_datasets_in_bucket(self.ws_context, affil=affil, project=project, cruise=cruise)

            # transform result of type List[DatasetRef] into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()


# noinspection PyAbstractClass
class DatasetsAffilProjectCruiseName(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str, name: str):
        """Provide API operation getDatasetByBucketAndName()."""
        try:
            result = get_dataset_by_bucket_and_name(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)

            # transform result of type str into response with mime-type application/octet-stream
            # TODO: transform result first
            self.write(result)

        finally:
            self.finish()


# noinspection PyAbstractClass
class Docfiles(WsRequestHandler):

    def put(self):
        """Provide API operation addDocFile()."""
        try:
            # transform body with mime-type multipart/form-data into a Dict
            # TODO: transform self.request.body first
            data = self.request.body

            result = add_doc_file(self.ws_context, data=data)

            # transform result of type ApiResponse into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()

    def post(self):
        """Provide API operation updateDocFile()."""
        try:
            # transform body with mime-type multipart/form-data into a Dict
            # TODO: transform self.request.body first
            data = self.request.body

            result = update_doc_file(self.ws_context, data=data)

            # transform result of type ApiResponse into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()


# noinspection PyAbstractClass
class DocfilesAffilProjectCruise(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str):
        """Provide API operation getDocFilesInBucket()."""
        try:
            result = get_doc_files_in_bucket(self.ws_context, affil=affil, project=project, cruise=cruise)

            # transform result of type List[DocFileRef] into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()


# noinspection PyAbstractClass
class DocfilesAffilProjectCruiseName(WsRequestHandler):

    def get(self, affil: str, project: str, cruise: str, name: str):
        """Provide API operation downloadDocFile()."""
        try:
            result = download_doc_file(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)

            # transform result of type str into response with mime-type application/octet-stream
            # TODO: transform result first
            self.write(result)

        finally:
            self.finish()

    def delete(self, affil: str, project: str, cruise: str, name: str):
        """Provide API operation deleteDocFile()."""
        try:
            result = delete_doc_file(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)

            # transform result of type ApiResponse into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()


# noinspection PyAbstractClass
class Users(WsRequestHandler):

    def post(self):
        """Provide API operation createUser()."""
        try:
            # transform body with mime-type application/json into a User
            data_dict = tornado.escape.json_decode(self.request.body)
            data = User.from_dict(data_dict)

            result = create_user(self.ws_context, data=data)

            # transform result of type ApiResponse into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()


# noinspection PyAbstractClass
class UsersLogin(WsRequestHandler):

    def get(self):
        """Provide API operation loginUser()."""
        try:
            username = self.query.get_param('username', default=None)
            password = self.query.get_param('password', default=None)
            result = login_user(self.ws_context, username=username, password=password)

            # transform result of type str into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result))

        finally:
            self.finish()


# noinspection PyAbstractClass
class UsersLogout(WsRequestHandler):

    def get(self):
        """Provide API operation logoutUser()."""
        try:
            result = logout_user(self.ws_context)

            # transform result of type ApiResponse into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()


# noinspection PyAbstractClass
class UsersId(WsRequestHandler):

    def get(self, id: int):
        """Provide API operation getUserByID()."""
        try:
            id_ = RequestParams.to_int(id)
            result = get_user_by_id(self.ws_context, id_=id_)

            # transform result of type User into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()

    def put(self, id: int):
        """Provide API operation updateUser()."""
        try:
            id_ = RequestParams.to_int(id)
            # transform body with mime-type application/json into a User
            data_dict = tornado.escape.json_decode(self.request.body)
            data = User.from_dict(data_dict)

            result = update_user(self.ws_context, id_=id_, data=data)

            # transform result of type ApiResponse into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()

    def delete(self, id: int):
        """Provide API operation deleteUser()."""
        try:
            id_ = RequestParams.to_int(id)
            result = delete_user(self.ws_context, id_=id_)

            # transform result of type ApiResponse into response with mime-type application/json
            self.set_header('Content-Type', 'application/json')
            self.write(tornado.escape.json_encode(result.to_dict()))

        finally:
            self.finish()
