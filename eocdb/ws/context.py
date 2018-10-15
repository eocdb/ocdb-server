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
from typing import Any, Dict, Sequence

from . import __version__, __description__
from .defaults import DEFAULT_SERVER_NAME, DEFAULT_MAX_THREAD_COUNT
from ..core.db.db_driver import DbDriver
from ..core.service import ServiceRegistry

_LOG = logging.getLogger('eocdb')

Config = Dict[str, Any]

DB_DRIVERS_CONFIG_NAME = "databases"


class WsContext:

    def __init__(self, base_dir=None):
        self._base_dir = os.path.abspath(base_dir or '')
        self._config = {}
        self._db_drivers = ServiceRegistry()
        self._thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=DEFAULT_MAX_THREAD_COUNT,
                                                                  thread_name_prefix=DEFAULT_SERVER_NAME)

    @property
    def base_dir(self) -> str:
        return self._base_dir

    @property
    def config(self) -> Config:
        return self._config

    def configure(self, new_config: Config):
        old_config = self._config
        new_config = new_config or {}

        old_db_drivers = old_config.get(DB_DRIVERS_CONFIG_NAME, {})
        new_db_drivers = new_config.get(DB_DRIVERS_CONFIG_NAME, {})
        if old_db_drivers != new_db_drivers:
            self._db_drivers.update(new_db_drivers)

        self._config = dict(new_config)

    def dispose(self):
        self._db_drivers.dispose()

    def get_db_drivers(self, mode: str = None):
        if mode not in ("r", "w", "rw", "wr"):
            raise ValueError(f"illegal mode {repr(mode)}")
    @classmethod
    def get_app_info(cls) -> Dict:
        return dict(name=DEFAULT_SERVER_NAME,
                    description=__description__,
                    version=__version__)

    def get_db_driver(self) -> DbDriver:
        """Get the primary database driver."""

        num_primary_db_drivers = 0

        def filter_db_drivers(service_id, service, config):
            nonlocal num_primary_db_drivers
            if not isinstance(service, DbDriver):
                return False
            if config.get('primary', False):
                num_primary_db_drivers += 1
            return True

        drivers = self._db_drivers.find_services(service_filter=filter_db_drivers)
        if len(drivers) == 0:
            raise RuntimeError('No database driver found')
        if num_primary_db_drivers > 1:
            raise RuntimeError('There can only be a single primary database driver')
        if len(drivers) > 1:
            raise RuntimeError('With multiple database drivers, one must be configured to be the primary one')

        # noinspection PyTypeChecker
        return drivers[0]

    def get_db_drivers(self) -> Sequence[DbDriver]:
        # noinspection PyTypeChecker
        return self._db_drivers.find_services(service_type=DbDriver)
