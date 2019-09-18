import unittest

from ocdb.ws.main import main \
    # from ocdb.ws.main import main, new_web_service  # , new_web_service


# import tornado.ioloop
# from tornado.ioloop import IOLoop
# from ocdb.ws.service import WebService
# from ocdb.ws.webservice import WebService


class MainSmokeTest(unittest.TestCase):

    # noinspection PyMethodMayBeStatic
    def test_cli(self):
        try:
            main(['--help'])
        except SystemExit:
            pass

    def test_start_stop_service(self):
        # Check why this test blocks all other handler tests
        # service = new_web_service(args=['--port', '20001', '--update', '0'])
        # self.assertIsInstance(service, WebService)
        # tornado.ioloop.IOLoop.current().call_later(0.1, service.stop)
        # service.start()
        pass
