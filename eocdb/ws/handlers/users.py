from ..webservice import WsRequestHandler
from ..controllers.users import *


# noinspection PyAbstractClass
class CreateUser(WsRequestHandler):
    def post(self):
        self.set_header('Content-Type', 'text/json')
        return create_user(self.ws_context)


# noinspection PyAbstractClass
class LoginUser(WsRequestHandler):
    def get(self):
        username = self.params.get_query_argument('username', None)
        password = self.params.get_query_argument('password', None)
        self.set_header('Content-Type', 'text/json')
        return login_user(self.ws_context, username=username, password=password)


# noinspection PyAbstractClass
class LogoutUser(WsRequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/json')
        return logout_user(self.ws_context)


# noinspection PyAbstractClass
class GetUserByID(WsRequestHandler):
    def get(self, id: int):
        self.set_header('Content-Type', 'text/json')
        return get_user_by_id(self.ws_context, id=id)


# noinspection PyAbstractClass
class UpdateUser(WsRequestHandler):
    def put(self, id: int):
        self.set_header('Content-Type', 'text/json')
        return update_user(self.ws_context, id=id)


# noinspection PyAbstractClass
class DeleteUser(WsRequestHandler):
    def delete(self, id: int):
        self.set_header('Content-Type', 'text/json')
        return delete_user(self.ws_context, id=id)
