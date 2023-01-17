import functools

import tornado.escape

from ocdb.core.models import User
from ocdb.version import MIN_CLIENT_VERSION, MIN_WEBUI_VERSION
from ocdb.ws.controllers.users import create_user, get_user_names, login_user, get_user_by_name, update_user, \
    delete_user
from ocdb.ws.errors import WsUnprocessable, WsUnauthorizedError
from ocdb.ws.handlers._handlers import _login_required, _admin_required
from ocdb.ws.handlers._version_check import is_version_valid
from ocdb.ws.webservice import WsRequestHandler


def _user_authorization_required(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        current_user_name = self.get_current_user()

        user_name = kwargs['user_name'] if 'user_name' in kwargs else None

        authorized = False
        if self.has_admin_rights():
            authorized = True
        elif current_user_name == user_name:
            authorized = True

        if not authorized:
            self.set_status(status_code=403, reason='Not enough access rights to perform operations on user '
                                                    f'{user_name}.')
            return

        func(self, *args, **kwargs)

    return wrapper


# noinspection PyAbstractClass,PyShadowingBuiltins
class HandleUsers(WsRequestHandler):
    @_login_required
    @_admin_required
    def post(self):
        """Provide API operation create_user()."""
        # transform body with mime-type application/json into a User
        data_dict = tornado.escape.json_decode(self.request.body)
        user = User.from_dict(data_dict)
        create_user(self.ws_context, user=user)

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode({'message': f'User {user.name} added'}))

    @_login_required
    @_admin_required
    def get(self):
        """Provide API operation get_user_names()."""

        # transform body with mime-type application/json into a User
        result = get_user_names(self.ws_context)

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result))


# noinspection PyAbstractClass,PyShadowingBuiltins
class LoginUser(WsRequestHandler):

    def get(self):
        return self.whoami()

    def post(self):
        return self.login_user()

    @_login_required
    def put(self):
        return self.change_password()

    def whoami(self):
        """Is used only by 'ocdb-cli whoami'."""
        current_user = self.get_current_user()
        if current_user is None:
            return self.finish(tornado.escape.json_encode({'message': f'Not Logged in.'}))
        return self.finish(tornado.escape.json_encode({'message': f'I am {current_user}.', 'name': current_user}))

    def login_user(self):
        """Provide API operation loginUser()."""
        credentials = tornado.escape.json_decode(self.request.body)
        username = credentials.get('username')
        password = credentials.get('password')
        client_version = credentials.get('client_version', 0)
        client = credentials.get('client', 'cli')

        client_allowed = True

        if client == 'cli' and not is_version_valid(client_version, MIN_CLIENT_VERSION):
            client_allowed = False

        if client == 'webui' and not is_version_valid(client_version, MIN_WEBUI_VERSION):
            client_allowed = False

        if not client_allowed:
            self.set_header('Content-Type', 'application/json')
            self.set_status(409)
            if client == 'cli':
                return self.finish(tornado.escape.json_encode({
                    'message': f'You are using a deprecated version of the ocdb client. Please update to at least '
                               f'version {MIN_CLIENT_VERSION}. Please update with conda update -c ocdb ocdb-client'
                }))
            else:
                return self.finish(tornado.escape.json_encode({
                    'message': f'You are using an outdated version of the ocdb website. Please clear your browser '
                               f'cache and reload the page.'
                }))

        user_info = login_user(self.ws_context, username=username, password=password)
        if user_info is not None:
            # expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=1440)
            self.set_secure_cookie("user", username, expires_days=1, expires=None)

        if 'password' in user_info:
            del user_info['password']

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(user_info))

    def change_password(self):
        current_user = self.get_current_user()
        credentials = tornado.escape.json_decode(self.request.body)
        username = credentials.get('username')
        new_password1 = credentials.get('newpassword1')
        new_password2 = credentials.get('newpassword2')

        if username is None:
            username = current_user

        same = username == current_user

        if same and not ('oldpassword' in credentials):
            self.set_status(status_code=403, reason="Old password is missing.")
            return

        if same:
            oldpassword = credentials.get('oldpassword')
            user = self.ws_context.get_user(username, oldpassword)
            if user is None:
                self.set_status(status_code=403, reason="Current password does not match.")
                return
        else:
            user = self.ws_context.get_user(username)

        if user is None:
            self.set_status(status_code=403, reason='User with name "' + username + '" does not exist.')
            return

        if username != current_user and not self.has_admin_rights():
            self.set_status(status_code=403, reason="Not enough rights to perform this operation.")
            return

        if new_password1 != new_password2:
            self.set_status(status_code=403, reason="Passwords don't match.")
            return

        user = get_user_by_name(ctx=self.ws_context, user_name=username, retain_password=True)

        user['password'] = new_password1

        # Todo: SE, please check whether password is encrypted
        update_user(self.ws_context, user_name=username, data=user)

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode({'message': f'User {username}\'s password updated.'}))


# noinspection PyAbstractClass,PyShadowingBuiltins
class LogoutUser(WsRequestHandler):

    def get(self):
        current_user = self.get_current_user()
        if current_user is not None:
            self.clear_cookie("user")
            return self.finish(tornado.escape.json_encode({'message': f'User {current_user} logged out'}))

        return self.finish(tornado.escape.json_encode({'message': f'No user logged in'}))


# noinspection PyAbstractClass,PyShadowingBuiltins
class GetUserByName(WsRequestHandler):
    @_login_required
    @_user_authorization_required
    def get(self, user_name: str):
        """Provide API operation getUserByID()."""
        return self.get_user_by_name(user_name)

    @_login_required
    @_user_authorization_required
    def put(self, user_name: str):
        """Provide API operation updateUser()."""
        return self.update_user(user_name)

    @_login_required
    @_admin_required
    def delete(self, user_name: str):
        """Provide API operation deleteUser()."""
        return self.delete_user(user_name)

    def get_user_by_name(self, user_name: str):
        result = get_user_by_name(self.ws_context, user_name=user_name)
        # transform result of type User into response with mime-type application/json
        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode(result))

    def update_user(self, user_name: str):
        # transform body with mime-type application/json into a User
        data_dict = tornado.escape.json_decode(self.request.body)

        if not user_name:
            raise WsUnprocessable("The required user_name is missing.")

        current_user_infos = get_user_by_name(self.ws_context, user_name=user_name)

        if ('id_' in data_dict and data_dict['id_'] != current_user_infos['id']) \
                or ('id' in data_dict and data_dict['id'] != current_user_infos['id']):
            raise WsUnprocessable(f"Changing the users id is not allowed.")

        if 'name' in data_dict and data_dict['name'] != user_name:
            raise WsUnprocessable(f"Changing the users name is not allowed.")

        if 'password' in data_dict:
            raise WsUnprocessable("Cannot handle changing password using 'user update'. " +
                                  "Use specific password operation (e.g. 'ocdb-cli user pwd').")

        authorized = self.has_admin_rights()

        # want_to_change_username = False
        # if 'name' in data_dict:
        #     new_user_name = data_dict['name']
        #     want_to_change_username = new_user_name != user_name
        #     if want_to_change_username and authorized is False:
        #         raise WsUnauthorizedError("Admin role required to change user name.")

        if 'roles' in data_dict:
            current_roles = current_user_infos['roles']
            new_roles = data_dict['roles']
            # sorting both the lists
            current_roles.sort()
            if isinstance(new_roles, str):
                new_roles = [new_roles]
            new_roles.sort()
            # using == to check if lists are equal
            want_to_change_roles = current_roles != new_roles
            if want_to_change_roles and authorized is False:
                raise WsUnauthorizedError("Admin role required to change roles.")

        data_dict['name'] = user_name

        updated = update_user(self.ws_context, user_name=user_name, data=data_dict)

        if updated:
            msg = f'User {user_name} updated.'
            # if want_to_change_username:
            #     msg += ' User has been renamed to ' + new_user_name + '.'
            self.finish(tornado.escape.json_encode({'message': msg}))
        else:
            msg = f'User {user_name} not updated.'
            self.finish(tornado.escape.json_encode({'message': msg}))

    def delete_user(self, user_name: str):
        if not self.has_admin_rights():
            self.set_status(status_code=403, reason='Not enough access rights to perform operation.')
            return

        delete_user(self.ws_context, user_name)

        self.set_header('Content-Type', 'application/json')
        self.finish(tornado.escape.json_encode({'message': f'User {user_name} deleted'}))
