import os
from typing import Optional

import yaml

from eocdb.core.db.db_dataset import DbDataset
from eocdb.core.models.dataset import Dataset
from eocdb.ws.context import WsContext
from eocdb.ws.reqparams import RequestParams


def new_test_service_context() -> WsContext:
    ctx = WsContext(base_dir=get_test_res_dir())
    config_file = os.path.join(ctx.base_dir, 'config.yml')
    with open(config_file) as fp:
        ctx.configure(yaml.load(fp))
    return ctx


def get_test_res_dir() -> str:
    return os.path.normpath(os.path.join(os.path.dirname(__file__), 'ws/res'))


def new_test_dataset(n: int = 0):
    return Dataset(f"relative_path-{n}",
                   f"dataset-{n}",
                   "new",
                   dict(fields=["a", "b", "c"]),
                   [[n + 1.2, n + 2.3, n + 3.4], [n + 4.5, n + 5.6, n + 6.7]])


def new_test_db_dataset(n: int = 0):
    return DbDataset(f"relative_path-{n}",
                     f"dataset-{n}",
                     "new",
                     dict(fields=["a", "b", "c"]),
                     [[n + 1.2, n + 2.3, n + 3.4], [n + 4.5, n + 5.6, n + 6.7]])


class RequestParamsMock(RequestParams):
    def __init__(self, **kvp):
        self.kvp = kvp

    def get_param(self, name: str, default: Optional[str]) -> Optional[str]:
        return self.kvp.get(name, default)
