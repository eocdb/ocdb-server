import os
from typing import Optional

import yaml

from eocdb.ws.context import ServiceContext
from eocdb.ws.reqparams import RequestParams


def new_test_service_context() -> ServiceContext:
    ctx = ServiceContext(base_dir=get_test_res_dir())
    config_file = os.path.join(ctx.base_dir, 'config.yml')
    with open(config_file) as fp:
        ctx.config = yaml.load(fp)
    return ctx


def get_test_res_dir() -> str:
    return os.path.normpath(os.path.join(os.path.dirname(__file__), 'res'))


class RequestParamsMock(RequestParams):
    def __init__(self, **kvp):
        self.kvp = kvp

    def get_query_argument(self, name: str, default: Optional[str]) -> Optional[str]:
        return self.kvp.get(name, default)
