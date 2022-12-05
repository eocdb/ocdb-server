import tornado.escape

from ocdb.ws.controllers.links import get_links, update_links
from ocdb.ws.handlers._handlers import _admin_required
from ocdb.ws.webservice import WsRequestHandler


# noinspection PyAbstractClass
class Links(WsRequestHandler):
    def get(self):
        """Provide API operation getUserByID()."""
        result = get_links(self.ws_context)
        self.set_header('Content-Type', 'application/txt')
        self.finish(tornado.escape.json_encode({'content': result['content']}))

    @_admin_required
    def post(self):
        """Provide API operation getUserByID()."""
        result = tornado.escape.json_decode(self.request.body)

        content = result['content']

        result = update_links(self.ws_context, content)
        self.set_header('Content-Type', 'application/txt')
        self.finish(result)
