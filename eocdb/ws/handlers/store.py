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
        file_path = self.query.get_param('filePath', None)
        self.set_header('Content-Type', 'text/json')
        return upload_store_files(self.ws_context, file_path=file_path)


# noinspection PyAbstractClass
class DownloadStoreFiles(WsRequestHandler):
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
        docs = self.query.get_param('docs', False)
        self.set_header('Content-Type', 'text/json')
        return download_store_files(self.ws_context, expr=expr, region=region, time=time, wdepth=wdepth, mtype=mtype, wlmode=wlmode, shallow=shallow, pmode=pmode, pgroup=pgroup, pname=pname, docs=docs)
