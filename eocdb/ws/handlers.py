# The MIT License (MIT)
# Copyright (c) 2018 by EUMETSAT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .webservice import WsRequestHandler


# from tornado import gen
# from tornado.ioloop import IOLoop

# noinspection PyAbstractClass
class InfoHandler(WsRequestHandler):

    def get(self):
        self.set_header('Content-Type', 'text/json')
        self.write(self.to_json((self.ws_context.get_app_info())))


# noinspection PyAbstractClass
class MeasurementsQueryHandler(WsRequestHandler):

    def get(self):
        self.set_header('Content-Type', 'text/json')
        query_string = self.query.get_param('query', self.query.get_param('q', ''))
        self.write(self.to_json(self.ws_context.query_measurements(query_string)))
