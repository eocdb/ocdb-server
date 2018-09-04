from eocdb.core.service import Service, ServiceInfo


class TestServiceBase(Service):
    @classmethod
    def info(cls) -> ServiceInfo:
        return dict(name=cls.__name__)

    def __init__(self):
        self.value1 = None
        self.value2 = None
        self.num_inits = 0
        self.num_updates = 0
        self.num_disposes = 0

    def init(self, value1=None, value2=None):
        self.num_inits += 1
        self.value1 = value1
        self.value2 = value2
        assert not (self.value1 == 1 and self.value2 == 1)

    def update(self, value1=None, value2=None):
        self.num_updates += 1
        self.value1 = value1
        self.value2 = value2
        assert not (self.value1 == 2 and self.value2 == 2)

    def dispose(self):
        self.num_disposes += 1
        assert not (self.value1 == 3 and self.value2 == 3)


class TestServiceA(TestServiceBase):
    pass


class TestServiceB(TestServiceA):
    pass


class TestServiceC(TestServiceB):
    pass


class TestServiceD(TestServiceB):
    pass


class TestServiceE(TestServiceB):
    def __init__(self):
        super().__init__()
        assert False
