from ..webservice import WsRequestHandler
from ..controllers.docfiles import *


# noinspection PyAbstractClass
class AddDocFile(WsRequestHandler):
    def put(self):
        self.set_header('Content-Type', 'text/json')
        return add_doc_file(self.ws_context)


# noinspection PyAbstractClass
class UpdateDocFile(WsRequestHandler):
    def post(self):
        self.set_header('Content-Type', 'text/json')
        return update_doc_file(self.ws_context)


# noinspection PyAbstractClass
class GetDocFilesInBucket(WsRequestHandler):
    def get(self, affil: str, project: str, cruise: str):
        self.set_header('Content-Type', 'text/json')
        return get_doc_files_in_bucket(self.ws_context, affil=affil, project=project, cruise=cruise)


# noinspection PyAbstractClass
class DownloadDocFile(WsRequestHandler):
    def get(self, affil: str, project: str, cruise: str, name: str):
        self.set_header('Content-Type', 'text/json')
        return download_doc_file(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)


# noinspection PyAbstractClass
class DeleteDocFile(WsRequestHandler):
    def delete(self, affil: str, project: str, cruise: str, name: str):
        self.set_header('Content-Type', 'text/json')
        return delete_doc_file(self.ws_context, affil=affil, project=project, cruise=cruise, name=name)
