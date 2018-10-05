from ..webservice import WsRequestHandler
from ..controllers.store import *


# noinspection PyAbstractClass
class GetStoreInfo(WsRequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/json')
        return get_store_info(self.ws_context)


# noinspection PyAbstractClass
class UploadStoreFiles(WsRequestHandler):
    def post(self):
        file_path = self.params.get_query_argument('filePath', None)
        self.set_header('Content-Type', 'text/json')
        return upload_store_files(self.ws_context, file_path=file_path)


# noinspection PyAbstractClass
class DownloadStoreFiles(WsRequestHandler):
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
        docs = self.params.get_query_argument('docs', False)
        self.set_header('Content-Type', 'text/json')
        return download_store_files(self.ws_context, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype, wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname, docs=docs)
