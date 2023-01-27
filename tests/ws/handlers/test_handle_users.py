import tornado.escape

from ocdb.core.db.db_user import DbUser
from ocdb.core.models import User
from ocdb.core.roles import Roles
from ocdb.version import MIN_CLIENT_VERSION
from ocdb.ws.controllers.users import create_user

from ocdb.ws.handlers import API_URL_PREFIX
from tests.ws.handlers.test_handlers import WsTestCase


class HandleUsersTest(WsTestCase):

    def test__list_user__as_admin(self):
        cookie = self.login_admin()

        response = self.fetch(API_URL_PREFIX + "/users", method='GET', headers={"Cookie": cookie})

        self.assertEqual(200, response.code)
        self.assertEqual("OK", response.reason)
        body_dict = tornado.escape.json_decode(response.body)
        self.assertEqual(list, type(body_dict))
        self.assertEqual(2, len(body_dict))
        self.assertEqual("submit", body_dict[0])
        self.assertEqual("chef", body_dict[1])

    def test__list_user__as_submit(self):
        cookie = self.login_submit()

        response = self.fetch(API_URL_PREFIX + "/users", method='GET', headers={"Cookie": cookie})

        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operation.', response.reason)

    def test__list_user__not_logged_in(self):
        response = self.fetch(API_URL_PREFIX + "/users", method='GET')

        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test__add_user__as_submit_user(self):
        cookie = self.login_submit()

        data = {
            'name': 'hinz',
            'first_name': 'Hinz',
            'last_name': 'Kunz',
            'password': 'lappig9',
            'email': None,
            'phone': None,
            'roles': ['admin']
        }
        body = tornado.escape.json_encode(data)

        response = self.fetch(API_URL_PREFIX + "/users", method='POST', body=body, headers={"Cookie": cookie})
        # Todo:Please check response code and reason
        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operation.', response.reason)

    def test__add_user__without_being_logged_in(self):
        data = {
            'name': 'hinz',
            'first_name': 'Hinz',
            'last_name': 'Kunz',
            'password': 'lappig9',
            'email': None,
            'phone': None,
            'roles': ['admin']
        }
        body = tornado.escape.json_encode(data)

        response = self.fetch(API_URL_PREFIX + "/users", method='POST', body=body)
        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test__add_user__as_admin(self):
        cookie = self.login_admin()

        try:
            data = {
                'name': 'hinz',
                'first_name': 'Hinz',
                'last_name': 'Kunz',
                'password': 'lappig9',
                'email': None,
                'phone': None,
                'roles': ['admin']
            }
            body = tornado.escape.json_encode(data)

            response = self.fetch(API_URL_PREFIX + "/users", method='POST', body=body, headers={"Cookie": cookie})
            self.assertEqual(200, response.code)
            self.assertEqual('OK', response.reason)

        finally:
            self.logout_admin()

    def test_add_existing_user(self):
        cookie = self.login_admin()

        data = {
            'name': 'hinz',
            'first_name': 'Hinz',
            'last_name': 'Kunz',
            'password': 'lappig9',
            'email': None,
            'phone': None,
            'roles': ['admin']
        }
        body = tornado.escape.json_encode(data)

        response = self.fetch(API_URL_PREFIX + "/users", method='POST', body=body, headers={"Cookie": cookie})

        self.assertEqual(200, response.code)
        self.assertEqual('User ' + data['name'] + ' added', tornado.escape.json_decode(response.body)['message'])

        response = self.fetch(API_URL_PREFIX + "/users", method='POST', body=body, headers={"Cookie": cookie})

        self.assertEqual(400, response.code)
        self.assertEqual('User exists:  ' + data['name'], response.reason)


class LoginUsersTest(WsTestCase):

    # 1.1 Tests for ocdb-cli command "user login": method LoginUser ('/users/login', POST)
    def test_login_existing_user(self):
        user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                    first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)

        credentials = {'username': "scott", 'password': "tiger", 'client_version': MIN_CLIENT_VERSION}
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='POST', body=body)

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        expected_response_data = {
            'id': '',
            'name': 'scott',
            'email': 'bruce.scott@gmail.com',
            'first_name': 'Bruce',
            'last_name': 'Scott',
            'phone': '+34 5678901234',
            'roles': ['submit', 'admin']
        }

        actual_response_data = tornado.escape.json_decode(response.body)
        # Since the created ID is unknown in beforehand ...
        actual_response_data['id'] = ''
        self.assertEqual(expected_response_data, actual_response_data)

    def test_login_existing_user_wrong_password(self):
        user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                    first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)

        credentials = {'username': "scott", 'password': "lion", 'client_version': MIN_CLIENT_VERSION}
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='POST', body=body)

        self.assertEqual(401, response.code)
        self.assertEqual('Unknown username or password', response.reason)

    def test_login_unknown_user(self):
        credentials = {'username': "malcolm", 'password': "rattenloch", 'client_version': MIN_CLIENT_VERSION}

        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='POST', body=body)

        self.assertEqual(401, response.code)
        self.assertEqual('Unknown username or password', response.reason)


class WhoamiTest(WsTestCase):

    def test__whoami__as_submit(self):
        cookie = self.login_submit()

        response = self.fetch(API_URL_PREFIX + '/users/login', method='GET', headers={"Cookie": cookie})

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        self.assertEqual('I am submit.', tornado.escape.json_decode(response.body)['message'])

    def test__whoami__not_logged_in(self):
        response = self.fetch(API_URL_PREFIX + '/users/login', method='GET')

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        self.assertEqual('Not Logged in.', tornado.escape.json_decode(response.body)['message'])


# Tests e.g. for ocdb-cli command "user pwd": method LoginUser ('/users/login', PUT)
class ChangingPasswordTest(WsTestCase):

    # 2.1 Submit user is logged in and tries to change its own password
    def test_submit_user_changes_own_password_with_username(self):
        cookie = self.login_submit()

        # username is not required to change own pwd.
        # Oldpassword is required to change own password, not to change pwd of other users (admins only).
        credentials = dict(username="submit", oldpassword="submit", newpassword1='submit2', newpassword2='submit2')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        # Todo:
        #   When executing:
        #  "ocdb-cli user pwd --username test1 --oldpassword secret --newpassword1 secret2 --newpassword2 secret2":
        #  The following failure is raised:
        #  "Error: no such option: --username"
        #  because the key --username has to be omitted.
        #  How can we test this?
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        user = self.ctx.get_user('submit').to_dict()
        self.assertEqual('submit2', user['password'])

    # 2.2 Submit user logs in and changes own password without specifying username
    def test_submit_user_changes_own_password_without_username(self):
        cookie = self.login_submit()

        # Oldpassword is required to change own password, not to change pwd of other users (admins only).
        credentials = dict(oldpassword="submit", newpassword1='submit2', newpassword2='submit2')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        fetched_user = self.ctx.get_user('submit').to_dict()
        self.assertEqual('submit2', fetched_user['password'])

    def test_submit_user_changes_own_passwd_with_wrong_old_passwd(self):
        cookie = self.login_submit()

        credentials = dict(username="submit", oldpassword="submit22", newpassword1='submit2', newpassword2='submit2')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        self.assertEqual(403, response.code)
        self.assertEqual('Current password does not match.', response.reason)

    # 2.3.2 Submit user logs in and tries to change own password with wrong newpassword2
    #
    # Currently, Iam not aware of a ocdb-cli or webui use case, in which user inputs
    #
    def test_submit_user_changes_own_passwd_with_wrong_newpassword2(self):
        cookie = self.login_submit()

        credentials = dict(oldpassword="submit", newpassword1='submit2', newpassword2='wrongpassword2')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        # user = get_user_by_name(ctx=self.ctx, user_name='submit', retain_password=True)

        self.assertEqual(403, response.code)
        # Todo: Please check error message!
        self.assertEqual("Passwords don't match.", response.reason)

        fetched_user = self.ctx.get_user('submit').to_dict()
        # the password is still unchanged
        self.assertEqual('submit', fetched_user['password'])

    # 2.3.3 Submit user logs in and tries to change password of another user
    def test_submit_user_changes_passwd_from_someone_else_without_admin_rights(self):
        cookie = self.login_submit()

        user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                    first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)

        # Oldpassword is required to change own password, not to change pwd of other users (admins only).
        credentials = dict(username="scott", oldpassword="tiger", newpassword1='sdfv', newpassword2='sdfv')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        self.assertEqual(403, response.code)
        self.assertEqual('Not enough rights to perform this operation.', response.reason)

    # 2.4 Admin creates new user and changes password
    def test_admin_change_passwd_of_newly_created_user_scott(self):
        cookie = self.login_admin()

        user = User(name='scott', last_name='Scott', password='tiger', email='bruce.scott@gmail.com',
                    first_name='Bruce', roles=[Roles.SUBMIT.value, Roles.ADMIN.value], phone='+34 5678901234')

        create_user(self.ctx, user)

        # oldpassword is required to change own password, not to change pwd of other users (admins only).
        credentials = dict(username="scott", newpassword1='sdfv', newpassword2='sdfv')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        fetched_user = self.ctx.get_user('scott').to_dict()
        self.assertEqual('sdfv', fetched_user['password'])

        expected_response_data = {'id': '', 'message': "User scott's password updated."}

        actual_response_data = tornado.escape.json_decode(response.body)
        actual_response_data['id'] = ''
        self.assertEqual(expected_response_data, actual_response_data)

    def test_admin_will_change_the_passwd_of_existing_submit_user_without_oldpassword(self):
        cookie = self.login_admin()

        # oldpassword is required to change own password, not to change pwd of other users (admins only).
        credentials = dict(username='submit', newpassword1='submit2', newpassword2='submit2')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        user = self.ctx.get_user('submit').to_dict()

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        self.assertEqual('submit2', user['password'])

    def test_admin_will_change_own_passwd(self):
        cookie = self.login_admin()

        # Username is not required to change own password
        # Oldpassword is required to change own password, not to change pwd of other users (admins only).
        credentials = dict(oldpassword="ocdb_chef", newpassword1='new_chef_pw', newpassword2='new_chef_pw')
        body = tornado.escape.json_encode(credentials)
        response = self.fetch(API_URL_PREFIX + f"/users/login", method='PUT', body=body, headers={"Cookie": cookie})

        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)
        fetched_user = self.ctx.get_user('chef').to_dict()
        self.assertEqual('new_chef_pw', fetched_user['password'])

    # 3. Use case "Check client version required for login"
    def test_login_too_low_client_version(self):
        res = self.login_admin_no_assert(client_version="0.1")
        self.assertEqual(409, res.code)


class LogoutUsersTest(WsTestCase):

    def test_get_no_user_logged_in(self):
        response = self.fetch(API_URL_PREFIX + "/users/logout", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

    def test_get(self):
        self.login_admin()

        response = self.fetch(API_URL_PREFIX + "/users/logout", method='GET')
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)


class GetUsersByNameTest(WsTestCase):

    # 1. Test for ocdb-cli command user get ('/users/{username}', GET)
    def test__users_name_get__as_admin(self):
        cookie = self.login_admin()

        name = 'chef'

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='GET', headers={"Cookie": cookie})
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual("chef", actual_response_data['name'])
        self.assertEqual(['submit', 'admin'], actual_response_data['roles'])

    def test__users_name_get__not_logged_in(self):
        name = 'chef'
        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='GET')
        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test__users_name_get__as_submit_user_own_user_name(self):
        cookie = self.login_submit()
        name = 'submit'
        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='GET', headers={"Cookie": cookie})
        self.assertEqual(200, response.code)
        # Todo: Any other test?

    def test__users_name_get__as_submit_user_not_own_user_name(self):
        cookie = self.login_submit()
        name = 'chef'
        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='GET', headers={"Cookie": cookie})
        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operations on user chef.', response.reason)

    def test__users_name_put__admin_changes_several_fields(self):
        cookie = self.login_admin()

        data = dict(
            first_name='fn',
            last_name="ln",
            email="some@mail.com",
            phone="985",
            roles=["admin", 'submit']
        )

        name = 'submit'

        current_user_submit = self.ctx.get_user(name).to_dict()
        # merges two dictionaries
        expected_user = current_user_submit | data

        body = tornado.escape.json_encode(data)

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='PUT', body=body,
                              headers={"Cookie": cookie})
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        expected_response_data = {'message': 'User submit updated.'}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)

        fetched_user = self.ctx.get_user(name).to_dict()
        self.assertEqual(fetched_user, expected_user)

    def test__users_name_put__changing_user_id___is_not_allowed(self):
        cookie = self.login_admin()

        new_data = dict(
            id_="gaga"
        )

        name = 'submit'

        body = tornado.escape.json_encode(new_data)

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='PUT', body=body, headers={"Cookie": cookie})
        self.assertEqual(422, response.code)
        self.assertEqual("Changing the users id is not allowed.", response.reason)

    def test__users_name_put__changing_user_id_is_not_allowed(self):
        cookie = self.login_admin()

        new_data = dict(
            id="gaga"
        )

        name = 'submit'

        body = tornado.escape.json_encode(new_data)

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='PUT', body=body, headers={"Cookie": cookie})
        self.assertEqual(422, response.code)
        self.assertEqual("Changing the users id is not allowed.", response.reason)

    def test__users_name_put__changing_username_is_not_allowed(self):
        cookie = self.login_admin()

        new_data = dict(
            name="another_name"
        )

        name = 'submit'

        body = tornado.escape.json_encode(new_data)

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='PUT', body=body, headers={"Cookie": cookie})
        self.assertEqual(422, response.code)
        self.assertEqual("Changing the users name is not allowed.", response.reason)

    def test__users_name_put__changing_password_is_not_possible_using_the_method_user_update(self):
        cookie = self.login_admin()

        data = dict(
            password="submit",
        )

        name = 'chef'

        body = tornado.escape.json_encode(data)

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='PUT', body=body,
                              headers={"Cookie": cookie})
        self.assertEqual(422, response.code)
        self.assertEqual(
            "Cannot handle changing password using 'user update'. Use specific password operation (e.g. 'ocdb-cli user pwd').",
            response.reason)

    def test__users_name_put__not_logged_in(self):
        name = 'chef'
        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='PUT', body=tornado.escape.json_encode({}))
        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test__users_name_put__not_own_user_name(self):
        cookie = self.login_submit()

        user = DbUser(
            id_='asdoökvn',
            name="helge",
            password="submit",
            first_name='Submit',
            last_name="Submit",
            email="sdfv",
            phone="",
            roles=["submit", ]
        )

        name = 'chef'

        data = user.to_dict()

        body = tornado.escape.json_encode(data)
        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='PUT', body=body,
                              headers={"Cookie": cookie})
        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operations on user chef.', response.reason)

    def test__users_name_put__changing_of_own_role_not_allowed_for_submit_user(self):
        cookie = self.login_submit()
        data = dict(
            roles=["admin"]
        )
        name = 'submit'
        body = tornado.escape.json_encode(data)
        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='PUT', body=body,
                              headers={"Cookie": cookie})
        self.assertEqual(401, response.code)
        self.assertEqual('Admin role required to change roles.', response.reason)

    def test__users_name_delete__delete_newly_created_user(self):
        cookie = self.login_admin()

        name = "new_user"
        user = DbUser(
            id_='habaksdblarbldbcvlasdbvlauzbeehbvlsudzbcv',
            name=name,
            password="n_u_pw",
            first_name='fn',
            last_name="ln",
            email="shgd@sdhf.com",
            phone="2361418",
            roles=["submit"]
        )
        create_user(self.ctx, user=user)

        response = self.fetch(API_URL_PREFIX + f"/users/{name}",
                              method='DELETE', headers={'Cookie': cookie})
        self.assertEqual(200, response.code)
        self.assertEqual('OK', response.reason)

        expected_response_data = {'message': 'User new_user deleted'}
        actual_response_data = tornado.escape.json_decode(response.body)
        self.assertEqual(expected_response_data, actual_response_data)

        fetched_user = self.ctx.get_user(name)
        self.assertIsNone(fetched_user)

    def test__users_name_delete__not_logged_in(self):
        name = 'chef'

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='DELETE')
        self.assertEqual(403, response.code)
        self.assertEqual('Please login.', response.reason)

    def test__users_name_delete__not_admin(self):
        cookie = self.login_submit()

        name = 'chef'

        response = self.fetch(API_URL_PREFIX + f"/users/{name}", method='DELETE',
                              headers={"Cookie": cookie})
        self.assertEqual(403, response.code)
        self.assertEqual('Not enough access rights to perform operation.', response.reason)
