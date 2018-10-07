from ..webservice import WsRequestHandler
from ..controllers.datasets import *


# noinspection PyAbstractClass
class FindDatasets(WsRequestHandler):
    def get(self):
        expr = self.query.get_param('expr', None)
        region = self.query.get_param('region', None)
        time = self.query.get_param('time', None)
        wdepth = self.query.get_param('wdepth', None)
        mtype = self.query.get_param('mtype', 'all')
        wlmode = self.query.get_param('wlmode', 'all')
        shallow = self.query.get_param('shallow', 'no')
        pmode = self.query.get_param('pmode', 'contains')
        pgroup = self.query.get_param('pgroup', None)
        pname = self.query.get_param('pname', None)
        offset = self.query.get_param('offset', 1)
        count = self.query.get_param('count', 1000)
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
