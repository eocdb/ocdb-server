import os
from typing import Optional

import yaml

from eocdb.core.models.bucket import Bucket
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
    return os.path.normpath(os.path.join(os.path.dirname(__file__), 'res'))


def new_dataset(n: int):
    dataset = Dataset()
    dataset.id = None
    dataset.name = f"dataset-{n}"
    bucket = Bucket()
    bucket.affil = f"affil_{n}"
    bucket.project = f"project_{n}"
    bucket.cruise = f"cruise_{n}"
    dataset.header = dict(fields=["a", "b", "c"])
    dataset.records = [[n + 1.2, n + 2.3, n + 3.4], [n + 4.5, n + 5.6, n + 6.7]]
    return dataset


class RequestParamsMock(RequestParams):
    def __init__(self, **kvp):
        self.kvp = kvp

    def get_param(self, name: str, default: Optional[str]) -> Optional[str]:
        return self.kvp.get(name, default)


