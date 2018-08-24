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

import concurrent.futures
import logging
import os
from typing import Any, Dict

from . import __version__, __description__
from .defaults import DEFAULT_SERVER_NAME, DEFAULT_MAX_THREAD_COUNT
from .errors import ServiceBadRequestError

_LOG = logging.getLogger('eocdb')

Config = Dict[str, Any]


class ServiceContext:

    def __init__(self, base_dir=None, config: Config = None):
        self.base_dir = os.path.abspath(base_dir or '')
        self._config = dict(config or {})
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=DEFAULT_MAX_THREAD_COUNT,
                                                                 thread_name_prefix=DEFAULT_SERVER_NAME)

    @property
    def config(self) -> Config:
        return self._config

    @config.setter
    def config(self, config: Config):
        if self._config:
            # Here: React to changed configuration
            pass
        self._config = dict(config or {})

    # noinspection PyMethodMayBeStatic
    def get_app_info(self) -> Dict:
        return dict(name=DEFAULT_SERVER_NAME,
                    description=__description__,
                    version=__version__)

    # noinspection PyMethodMayBeStatic
    def query_measurements(self, query_string: str):
        # TODO: use database API (tb)
        if query_string == 'ernie':
            return dict(id=[1, 2, 3, 4, 5],
                        lon=[58.1, 58.4, 58.5, 58.2, 58.9],
                        lat=[11.1, 11.4, 10.9, 10.8, 11.2],
                        chl=[0.3, 0.2, 0.7, 0.2, 0.1])
        else:
            raise ServiceBadRequestError('The only valid query string is "ernie"')

    # Here: add service methods, use thread_pool for concurrent requests
