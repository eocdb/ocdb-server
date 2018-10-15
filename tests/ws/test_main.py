import unittest

import tornado.ioloop

from eocdb.ws.main import main, new_web_service  # , new_web_service
# from tornado.ioloop import IOLoop
# from eocdb.ws.service import WebService
from eocdb.ws.webservice import WebService


class MainSmokeTest(unittest.TestCase):

    def test_cli(self):
        try:
            main(['--help'])
        except SystemExit:
            pass

    def test_start_stop_service(self):
        service = new_web_service(args=['--port', '20001', '--update', '0'])
        self.assertIsInstance(service, WebService)
        tornado.ioloop.IOLoop.current().call_later(0.1, service.stop)
        service.start()
