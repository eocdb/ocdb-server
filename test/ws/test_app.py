import unittest

from eocdb.ws.app import main  # , new_service


# from tornado.ioloop import IOLoop
# from eocdb.ws.service import Service


class AppSmokeTest(unittest.TestCase):

    def test_cli(self):
        try:
            main(['--help'])
        except SystemExit:
            pass

    def test_start_stop_service(self):
        pass
        # TODO: The following test code will cause timeouts in test/test_handlers.py - why?
        # service = new_service(args=['--port', '20001', '--update', '0'])
        # self.assertIsInstance(service, Service)
        # # service.stop()
        # IOLoop.current().call_later(0.1, service.stop)
        # service.start()
