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

import importlib
from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import Dict, Any, Tuple, Optional

LOGGER = getLogger('eocdb.db')

DbDriverInfo = Dict[str, Any]

DbDriverConfig = Dict[str, Any]
DbDriversConfig = Dict[str, DbDriverConfig]


# Example for two driver configurations:
# {
#   "EUMETSAT-OCDB": {
#     "driver": "eocdb.db.drivers.MongoDbDriver",
#     "write": True,
#     "read": True,
#     "parameters": {
#       "url": "...",
#       "user": "scott",
#       "password": "tiger",
#     }
#   },
#   "SeaBASS-Test": {
#     "driver": "eocdb.db.drivers.SeaBassDriver",
#     "write": False,
#     "read": True,
#     "parameters": {
#       "service_url": "https://seabass.gsfc.nasa.gov/",
#       "access_token": "7345-f3e2-aa50-76b3",
#     }
#   }
# }


class DbDriver(metaclass=ABCMeta):
    """ A database driver. """

    @classmethod
    def get_info(cls) -> DbDriverInfo:
        """ Get basic database driver information. """
        raise NotImplementedError()

    @abstractmethod
    def init(self, **config):
        """ Initialize this database driver. """

    @abstractmethod
    def update(self, **config):
        """ Initialize this database driver, because the configuration has changed. """

    @abstractmethod
    def dispose(self):
        """ Dispose this database driver, because the configuration has changed. """


class DbDriverRegistry:
    """ A database driver registry. """

    def __init__(self):
        self._configs = dict()
        self._drivers = dict()

    def get_all(self):
        """ Return a sequence of tuples of the form (id, driver, configuration). """
        return [(k, self._drivers[k], self._configs[k]) for k in self._configs.keys()]

    def update(self, configs: DbDriversConfig):
        """ Update registry with new driver configuration. """

        new_ids = set(configs.keys())
        old_ids = set(self._configs.keys())

        ids_to_be_added = new_ids - old_ids
        ids_to_be_removed = old_ids - new_ids
        ids_to_be_updated = new_ids.intersection(old_ids)

        for driver_id in ids_to_be_removed:
            driver, config = self._remove_driver(driver_id)
            self._dispose_driver(driver, config)

        for driver_id in ids_to_be_added:
            config = configs[driver_id]
            driver = self._load_driver(config)
            if driver is not None and self._init_driver(driver, config):
                self._add_driver(driver_id, driver, config)

        for driver_id in ids_to_be_updated:
            new_config = configs[driver_id]
            driver, old_config = self._get_driver(driver_id)
            if self._must_update_driver(old_config, new_config):
                self._update_driver(driver, new_config)

    def _get_driver(self, driver_id: str) -> Tuple[DbDriver, DbDriverConfig]:
        return self._drivers[driver_id], \
               self._configs[driver_id]

    def _add_driver(self, driver_id: str, driver: DbDriver, config: DbDriverConfig):
        self._drivers[driver_id] = driver
        self._configs[driver_id] = config

    def _remove_driver(self, driver_id: str) -> Tuple[DbDriver, DbDriverConfig]:
        return self._drivers.pop(driver_id), \
               self._configs.pop(driver_id)

    @classmethod
    def _load_driver(cls, config: DbDriverConfig) -> Optional[DbDriver]:
        # noinspection PyBroadException
        try:
            qual_class_name = config.get('driver')
            if not qual_class_name:
                raise ValueError(f'missing value for "driver" in configuration')
            if '.' not in qual_class_name:
                raise ValueError(f'invalid "driver" value: {qual_class_name}')
            module_name, class_name = qual_class_name.rsplit('.', 1)
            if not module_name or not class_name:
                raise ValueError(f'invalid "driver" value: {qual_class_name}')
            try:
                module = importlib.import_module(module_name)
            except ModuleNotFoundError as error:
                raise ValueError(f'invalid "driver" value: {qual_class_name}: module not found') from error
            try:
                driver_class = getattr(module, class_name)
            except AttributeError as error:
                raise ValueError(f'class {class_name} not found in module {module_name}') from error
            return driver_class()
        except Exception:
            LOGGER.error(f'failed to instantiate driver with configuration {config}')
            return None

    @classmethod
    def _init_driver(cls, driver: DbDriver, config: DbDriverConfig) -> bool:
        # noinspection PyBroadException
        try:
            driver.init(**(config.get('parameters', {})))
            return True
        except Exception:
            LOGGER.error(f'failed to initialize driver of type {type(driver)} '
                         f'with configuration {config}', exc_info=1)
            return False

    @classmethod
    def _update_driver(cls, driver: DbDriver, config: DbDriverConfig) -> bool:
        # noinspection PyBroadException
        try:
            driver.update(**(config.get('parameters', {})))
            return True
        except Exception:
            LOGGER.error(f'failed to update driver of type {type(driver)} '
                         f'with configuration {config}', exc_info=1)
            return False

    @classmethod
    def _dispose_driver(cls, driver: DbDriver, config: DbDriverConfig) -> bool:
        # noinspection PyBroadException
        try:
            driver.dispose()
            return True
        except Exception:
            LOGGER.error(f'failed to dispose driver of type {type(driver)} '
                         f'with configuration {config}', exc_info=1)
            return False

    @classmethod
    def _must_update_driver(cls,
                            old_config: DbDriverConfig,
                            new_config: DbDriverConfig) -> bool:
        # TODO: compare old_config and new_config
        return False
