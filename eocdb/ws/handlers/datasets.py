from ..webservice import WsRequestHandler
from ..controllers.datasets import *


# noinspection PyAbstractClass
class FindDatasets(WsRequestHandler):
    def get(self):
        expr = self.params.get_query_argument('expr', None)
        region = self.params.get_query_argument('region', None)
        time = self.params.get_query_argument('time', None)
        wdepth = self.params.get_query_argument('wdepth', None)
        mtype = self.params.get_query_argument('mtype', 'all')
        wlmode = self.params.get_query_argument('wlmode', 'all')
        shallow = self.params.get_query_argument('shallow', 'no')
        pmode = self.params.get_query_argument('pmode', 'contains')
        pgroup = self.params.get_query_argument('pgroup', None)
        pname = self.params.get_query_argument('pname', None)
        offset = self.params.get_query_argument('offset', 1)
        count = self.params.get_query_argument('count', 1000)
        self.set_header('Content-Type', 'text/json')
        return find_datasets(self.ws_context, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype, wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname, offset=offset, count=count)


# noinspection PyAbstractClass
class UpdateDataset(WsRequestHandler):
    def put(self):
        self.set_header('Content-Type', 'text/json')
        return update_dataset(self.ws_context)


# noinspection PyAbstractClass
class AddDataset(WsRequestHandler):
    def post(self):
        self.set_header('Content-Type', 'text/json')
        return add_dataset(self.ws_context)


# noinspection PyAbstractClass
class GetDatasetById(WsRequestHandler):
    def get(self, id: str):
        self.set_header('Content-Type', 'text/json')
        return get_dataset_by_id(self.ws_context, id=id)


# noinspection PyAbstractClass
class DeleteDataset(WsRequestHandler):
    def delete(self, id: int):
        self.set_header('Content-Type', 'text/json')
        return delete_dataset(self.ws_context, id=id)


# noinspection PyAbstractClass
class GetDatasetsInBucket(WsRequestHandler):
    def get(self, affil: str, project: str, cruise: str):
        self.set_header('Content-Type', 'text/json')
        return get_datasets_in_bucket(self.ws_context, affil=affil, project=project, cruise=cruise)


# noinspection PyAbstractClass
class GetDatasetByBucketAndName(WsRequestHandler):
    def get(self, affil: str, project: str, cruise: str, name: str):
        self.set_header('Content-Type', 'text/json')
        return get_dataset_by_bucket_and_name(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)
