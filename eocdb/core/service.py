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
from typing import Dict, Any, Tuple, Optional, Type, Callable, Sequence

ServiceInfo = Dict[str, Any]

ServiceId = str
ServiceConfig = Dict[str, Any]
ServiceConfigs = Dict[ServiceId, ServiceConfig]

SERVICE_TYPE_CONFIG_NAME = "type"
SERVICE_PARAMS_CONFIG_NAME = "parameters"


class ServiceError(Exception):
    pass


class Service(metaclass=ABCMeta):
    """ Some service. """

    @classmethod
    def info(cls) -> ServiceInfo:
        """ Get basic service information. """
        return dict(name=cls.__name__)

    @abstractmethod
    def init(self, **config):
        """ Initialize this service. """

    @abstractmethod
    def update(self, **config):
        """ Initialize this service, because the configuration has changed. """

    @abstractmethod
    def dispose(self):
        """ Dispose this service, because the configuration has changed. """

    def instance(self):
        """ Get the actual service instance. """
        return self


ServiceType = Type[Service]
ServiceFilter = Callable[[ServiceId, Service, ServiceConfig], bool]


class ServiceLookup(metaclass=ABCMeta):
    """ A provider for services. """

    @abstractmethod
    def find_by_id(self, service_id: ServiceId) -> Optional[Service]:
        """ Find service by identifier . """

    @abstractmethod
    def find_by_type(self, service_type: ServiceType) -> Optional[Service]:
        """ Find services by type. """

    @abstractmethod
    def find_by_filter(self, service_filter: ServiceFilter) -> Sequence[Service]:
        """ Get basic service information. """


class ServiceRegistry(ServiceLookup):
    """ 
    A service registry that can be updated by service configurations. 
    
    Example for two database driver configurations:
    
        "database_drivers": {
            "EUMETSAT-OCDB": {
                "type": "eocdb.db.services.MongoDbDriver",
                "write": True,
                "read": True,
                "parameters": {
                    "url": "...",
                    "user": "scott",
                    "password": "tiger",
                }
            },
            "SeaBASS-Test": {
                "type": "eocdb.db.services.SeaBassDriver",
                "write": False,
                "read": True,
                "parameters": {
                    "service_url": "https://seabass.gsfc.nasa.gov/",
                    "access_token": "7345-f3e2-aa50-76b3",
                }
            }
        }

    Within a service configuration, the only required setting is "type", whose value must be a
    the fully qualified name of an existing and accessible class.

    The optional setting "parameters" is expected to be a dictionary of keyword-arguments passed to the
    service, i.e. ``service.init(**config)`` and ``service.update(**config)``.
    
    """

    def __init__(self):
        self._configs = dict()
        self._services = dict()

    def find_by_id(self, service_id: ServiceId) -> Optional[Service]:
        """ Find service by identifier *service_id*. Return None, if no such service exists. """
        return self._services.get(service_id)

    def find_by_type(self, service_type: ServiceType) -> Sequence[Service]:
        """ Find services that are instances of the given type *service_type*. """
        return [service for service in self._services.values() if isinstance(service, service_type)]

    def find_by_filter(self, service_filter: ServiceFilter) -> Sequence[Service]:
        """
        Find service by a filter function. *service_filter* is called
        with the service id, the service, and its configuration.
        """
        return [self._services[service_id] for service_id in self._services.keys()
                if service_filter(service_id, self._services[service_id], self._configs[service_id])]

    def update(self, configs: ServiceConfigs):
        """
        Update registry with new service configurations. *configs* is a mapping
        from service identifiers to respective services' configuration.
        """
        if not isinstance(configs, dict):
            raise ServiceError('service configuration must be a dictionary')

        new_ids = set(configs.keys())
        old_ids = set(self._configs.keys())

        ids_to_be_added = new_ids - old_ids
        ids_to_be_removed = old_ids - new_ids
        ids_to_be_updated = new_ids.intersection(old_ids)

        for service_id in ids_to_be_removed:
            service, config = self._remove_service(service_id)
            self._dispose_service(service, config)

        for service_id in ids_to_be_added:
            config = configs[service_id]
            service = self._load_service(config)
            self._init_service(service, config)
            self._add_service(service_id, service, config)

        for service_id in ids_to_be_updated:
            new_config = configs[service_id]
            service, old_config = self._get_service(service_id)
            if old_config != new_config:
                self._update_service(service, old_config, new_config)

    def dispose(self):
        """ Dispose and remove all services. """
        self.update({})

    def _get_service(self, service_id: str) -> Tuple[Service, ServiceConfig]:
        return self._services[service_id], \
               self._configs[service_id]

    def _add_service(self, service_id: str, service: Service, config: ServiceConfig):
        self._services[service_id] = service
        self._configs[service_id] = config

    def _remove_service(self, service_id: str) -> Tuple[Service, ServiceConfig]:
        return self._services.pop(service_id), \
               self._configs.pop(service_id)

    @classmethod
    def _load_service(cls, config: ServiceConfig) -> Optional[Service]:
        qual_class_name = config.get(SERVICE_TYPE_CONFIG_NAME)
        if not qual_class_name:
            raise ServiceError(f'missing service "{SERVICE_TYPE_CONFIG_NAME}" value')
        if '.' not in qual_class_name:
            raise ServiceError(f'invalid service "{SERVICE_TYPE_CONFIG_NAME}" value '
                               f'"{qual_class_name}"')

        module_name, class_name = qual_class_name.rsplit('.', 1)
        if not module_name or not class_name:
            raise ServiceError(f'invalid service "{SERVICE_TYPE_CONFIG_NAME}" value '
                               f'"{qual_class_name}"')

        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as error:
            raise ServiceError(f'invalid service "{SERVICE_TYPE_CONFIG_NAME}" value: '
                               f'module {module_name} not found') from error

        try:
            service_class = getattr(module, class_name)
        except AttributeError as error:
            raise ServiceError(f'invalid service "{SERVICE_TYPE_CONFIG_NAME}" value: '
                               f'class {class_name} not found in module {module_name}') from error

        try:
            return service_class()
        except Exception as error:
            raise ServiceError(f'invalid service "{SERVICE_TYPE_CONFIG_NAME}" value: '
                               f'cannot create instance of class {qual_class_name}') from error

    @classmethod
    def _init_service(cls, service: Service, config: ServiceConfig):
        params = config.get(SERVICE_PARAMS_CONFIG_NAME, {})
        # noinspection PyBroadException
        try:
            service.init(**params)
        except Exception as error:
            raise ServiceError(f'failed to initialize service of type {type(service)} '
                               f'with configuration {config}') from error

    @classmethod
    def _update_service(cls, service: Service, old_config: ServiceConfig, new_config: ServiceConfig):
        old_type = old_config.get(SERVICE_TYPE_CONFIG_NAME)
        new_type = new_config.get(SERVICE_TYPE_CONFIG_NAME)
        if old_type != new_type:
            raise ServiceError(f'failed to update service of type {type(service)}'
                               f' changing a service\'s type is not (yet) supported')

        old_params = old_config.get(SERVICE_PARAMS_CONFIG_NAME, {})
        new_params = new_config.get(SERVICE_PARAMS_CONFIG_NAME, {})
        if old_params == new_params:
            return

        # noinspection PyBroadException
        try:
            service.update(**new_params)
        except Exception as error:
            raise ServiceError(f'failed to update service of type {type(service)} '
                               f'with configuration {new_config}') from error

    @classmethod
    def _dispose_service(cls, service: Service, config: ServiceConfig):
        # noinspection PyBroadException
        try:
            service.dispose()
        except Exception as error:
            raise ServiceError(f'failed to dispose service of type {type(service)} '
                               f'with configuration {config}')from error
