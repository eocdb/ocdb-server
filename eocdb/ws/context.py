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

from .defaults import DEFAULT_SERVER_NAME, DEFAULT_MAX_THREAD_COUNT
from ..core.db.db_driver import DbDriver
from ..core.service import ServiceRegistry

_LOG = logging.getLogger('eocdb')

Config = Dict[str, Any]

STORE_PATH_CONFIG_NAME = "store_path"
UPLOAD_PATH_CONFIG_NAME = "upload_path"
DEFAULT_STORE_PATH = "~/.eocdb/store"
DEFAULT_UPLOAD_PATH = "~/.eocdb/uploads"

DB_DRIVERS_CONFIG_NAME = "databases"

DATASETS_DIR_NAME = "archive"
DOC_FILES_DIR_NAME = "documents"


class WsContext:

    def __init__(self, base_dir=None):
        self._base_dir = os.path.abspath(base_dir or '')
        self._config = {}
        self._store_path = None
        self._db_drivers = ServiceRegistry()
        self._thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=DEFAULT_MAX_THREAD_COUNT,
                                                                  thread_name_prefix=DEFAULT_SERVER_NAME)

    @property
    def config(self) -> Config:
        return self._config

    @property
    def base_dir(self) -> str:
        return self._base_dir

    @property
    def store_path(self) -> str:
        return self._extract_path(STORE_PATH_CONFIG_NAME, DEFAULT_STORE_PATH)

    @property
    def upload_path(self) -> str:
        return self._extract_path(UPLOAD_PATH_CONFIG_NAME, DEFAULT_UPLOAD_PATH)

    @property
    def db_drivers(self) -> Sequence[DbDriver]:
        # noinspection PyTypeChecker
        return self._db_drivers.find_services(service_type=DbDriver)

    @property
    def db_driver(self) -> DbDriver:
        """Get the primary database driver."""

        primary_db_driver = None

        def filter_db_drivers(service_id, service, config):
            nonlocal primary_db_driver
            if not isinstance(service, DbDriver):
                return False
            if config.get('primary', False):
                if primary_db_driver is not None:
                    raise RuntimeError('There can only be a single primary database driver')
                primary_db_driver = service
            return True

        drivers = self._db_drivers.find_services(service_filter=filter_db_drivers)
        if primary_db_driver is None:
            if len(drivers) == 1:
                primary_db_driver = drivers[0]
            elif len(drivers) == 0:
                raise RuntimeError('No database driver found')
            else:
                raise RuntimeError('With multiple database drivers, one must be configured to be the primary one')

        # noinspection PyTypeChecker
        return primary_db_driver

    def get_datasets_store_path(self, sub_path: str) -> str:
        return os.path.join(self.store_path, sub_path, DATASETS_DIR_NAME)

    def get_datasets_upload_path(self, sub_path: str) -> str:
        return os.path.join(self.upload_path, sub_path, DATASETS_DIR_NAME)

    def get_doc_files_store_path(self, sub_path: str) -> str:
        return os.path.join(self.store_path, sub_path, DOC_FILES_DIR_NAME)

    def get_doc_files_upload_path(self, sub_path: str) -> str:
        return os.path.join(self.upload_path, sub_path, DOC_FILES_DIR_NAME)

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

    def _extract_path(self, property_name, default_path):
        path = self.config.get(property_name, default_path)
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = os.path.join(self.base_dir, path)
        return path
