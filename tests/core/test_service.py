from unittest import TestCase

from eocdb.core.service import Service, ServiceInfo, ServiceRegistry, ServiceError


class TestServiceBase(Service):

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

    @classmethod
    def info(cls) -> ServiceInfo:
        return dict(name=cls.__name__)


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


class ServiceRegistryTest(TestCase):

    def setUp(self):
        self.registry = ServiceRegistry()

    def test_update_and_find(self):
        self.registry.update({
            "service_a": {
                "type": "tests.core.test_service.TestServiceA",
            },
            "service_b": {
                "type": "tests.core.test_service.TestServiceB",
            },
        })

        # Test all possible lookups so we don't need to do that again in this test class

        service_a = self.registry.find_by_id("service_a")
        self.assertIsInstance(service_a, TestServiceA)
        service_b = self.registry.find_by_id("service_b")
        self.assertIsInstance(service_b, TestServiceB)
        service_c = self.registry.find_by_id("service_c")
        self.assertIsNone(service_c)

        self.assertIs(service_a, self.registry.find_by_id("service_a"))

        services = self.registry.find_by_type(TestServiceA)
        self.assertEqual({service_a, service_b}, set(services))
        services = self.registry.find_by_type(TestServiceB)
        self.assertEqual({service_b}, set(services))
        # noinspection PyTypeChecker
        services = self.registry.find_by_type(object)
        self.assertEqual({service_a, service_b}, set(services))
        # noinspection PyTypeChecker
        services = self.registry.find_by_type(int)
        self.assertEqual(set(), set(services))

        services = self.registry.find_by_filter(lambda sid, s, c: sid.startswith('ser'))
        self.assertEqual({service_a, service_b}, set(services))
        services = self.registry.find_by_filter(lambda sid, s, c: s is service_b)
        self.assertEqual({service_b}, set(services))
        services = self.registry.find_by_filter(lambda sid, s, c: c['type'].endswith('iceA'))
        self.assertEqual({service_a}, set(services))
        services = self.registry.find_by_filter(lambda sid, s, c: c['type'].endswith('iceC'))
        self.assertEqual(set(), set(services))

    def test_nominal_updates(self):
        self.registry.update({
            "service_a": {
                "type": "tests.core.test_service.TestServiceA",
                "parameters": {
                    "value1": 1,
                },
            },
            "service_b": {
                "type": "tests.core.test_service.TestServiceB",
            },
        })

        service_a = self.registry.find_by_id("service_a")
        self.assertIsNotNone(service_a)
        service_b = self.registry.find_by_id("service_b")
        self.assertIsNotNone(service_b)
        self.assertEqual(1, service_a.num_inits)
        self.assertEqual(1, service_b.num_inits)
        self.assertEqual(0, service_a.num_updates)
        self.assertEqual(0, service_b.num_updates)
        self.assertEqual(0, service_a.num_disposes)
        self.assertEqual(0, service_b.num_disposes)

        self.registry.update({
            "service_a": {
                "type": "tests.core.test_service.TestServiceA",
                "parameters": {
                    "value1": 2,
                },
            },
            "service_c": {
                "type": "tests.core.test_service.TestServiceC",
            },
        })

        service_a = self.registry.find_by_id("service_a")
        self.assertIsNotNone(service_a)
        self.assertIsNone(self.registry.find_by_id("service_b"))
        service_c = self.registry.find_by_id("service_c")
        self.assertIsNotNone(service_c)
        self.assertEqual(1, service_a.num_inits)
        self.assertEqual(1, service_b.num_inits)
        self.assertEqual(1, service_c.num_inits)
        self.assertEqual(1, service_a.num_updates)
        self.assertEqual(0, service_b.num_updates)
        self.assertEqual(0, service_c.num_updates)
        self.assertEqual(0, service_a.num_disposes)
        self.assertEqual(1, service_b.num_disposes)
        self.assertEqual(0, service_c.num_disposes)

        self.registry.update({
            "service_a": {
                "type": "tests.core.test_service.TestServiceA",
                "parameters": {
                    "value1": 3,
                },
            },
            "service_c1": {
                "type": "tests.core.test_service.TestServiceC",
            },
            "service_c2": {
                "type": "tests.core.test_service.TestServiceC",
            },
        })

        service_a = self.registry.find_by_id("service_a")
        self.assertIsNotNone(service_a)
        self.assertIsNone(self.registry.find_by_id("service_b"))
        self.assertIsNone(self.registry.find_by_id("service_c"))
        service_c1 = self.registry.find_by_id("service_c1")
        self.assertIsNotNone(service_c1)
        service_c2 = self.registry.find_by_id("service_c2")
        self.assertIsNotNone(service_c2)
        self.assertEqual(1, service_a.num_inits)
        self.assertEqual(1, service_b.num_inits)
        self.assertEqual(1, service_c.num_inits)
        self.assertEqual(1, service_c1.num_inits)
        self.assertEqual(1, service_c2.num_inits)
        self.assertEqual(2, service_a.num_updates)
        self.assertEqual(0, service_b.num_updates)
        self.assertEqual(0, service_c.num_updates)
        self.assertEqual(0, service_c1.num_updates)
        self.assertEqual(0, service_c2.num_updates)
        self.assertEqual(0, service_a.num_disposes)
        self.assertEqual(1, service_b.num_disposes)
        self.assertEqual(1, service_c.num_disposes)
        self.assertEqual(0, service_c1.num_disposes)
        self.assertEqual(0, service_c2.num_disposes)

        self.registry.dispose()

        self.assertIsNone(self.registry.find_by_id("service_a"))
        self.assertIsNone(self.registry.find_by_id("service_b"))
        self.assertIsNone(self.registry.find_by_id("service_c"))
        self.assertIsNone(self.registry.find_by_id("service_c1"))
        self.assertIsNone(self.registry.find_by_id("service_c2"))
        self.assertEqual(1, service_a.num_inits)
        self.assertEqual(1, service_b.num_inits)
        self.assertEqual(1, service_c.num_inits)
        self.assertEqual(1, service_c1.num_inits)
        self.assertEqual(1, service_c2.num_inits)
        self.assertEqual(2, service_a.num_updates)
        self.assertEqual(0, service_b.num_updates)
        self.assertEqual(0, service_c.num_updates)
        self.assertEqual(0, service_c1.num_updates)
        self.assertEqual(0, service_c2.num_updates)
        self.assertEqual(1, service_a.num_disposes)
        self.assertEqual(1, service_b.num_disposes)
        self.assertEqual(1, service_c.num_disposes)
        self.assertEqual(1, service_c1.num_disposes)
        self.assertEqual(1, service_c2.num_disposes)

    def test_illegal_service_init(self):
        with self.assertRaises(ServiceError) as cm:
            self.registry.update({
                "service_a": {
                    "type": "tests.core.test_service.TestServiceA",
                    "parameters": {
                        "value1": 1,
                        "value2": 1,
                    },
                },
            })
        self.assertEqual("failed to initialize service of type <class 'tests.core.test_service.TestServiceA'>"
                         " with configuration {'type': 'tests.core.test_service.TestServiceA',"
                         " 'parameters': {'value1': 1, 'value2': 1}}",
                         f'{cm.exception}')

    def test_illegal_service_update(self):
        self.registry.update({
            "service_a": {
                "type": "tests.core.test_service.TestServiceA",
                "parameters": {
                    "value1": 1,
                    "value2": 2,
                },
            },
        })
        with self.assertRaises(ServiceError) as cm:
            self.registry.update({
                "service_a": {
                    "type": "tests.core.test_service.TestServiceA",
                    "parameters": {
                        "value1": 2,
                        "value2": 2,
                    },
                },
            })
        self.assertEqual("failed to update service of type <class 'tests.core.test_service.TestServiceA'>"
                         " with configuration {'type': 'tests.core.test_service.TestServiceA',"
                         " 'parameters': {'value1': 2, 'value2': 2}}",
                         f'{cm.exception}')

        with self.assertRaises(ServiceError) as cm:
            self.registry.update({
                "service_a": {
                    "type": "tests.core.test_service.TestServiceB",
                    "parameters": {
                        "value1": 1,
                        "value2": 2,
                    },
                },
            })
        self.assertEqual("failed to update service of type <class 'tests.core.test_service.TestServiceA'>"
                         " changing a service's type is not (yet) supported",
                         f'{cm.exception}')

    def test_illegal_service_dispose(self):
        self.registry.update({
            "service_a": {
                "type": "tests.core.test_service.TestServiceA",
                "parameters": {
                    "value1": 3,
                    "value2": 3,
                },
            },
        })
        with self.assertRaises(ServiceError) as cm:
            self.registry.dispose()
        self.assertEqual("failed to dispose service of type <class 'tests.core.test_service.TestServiceA'>"
                         " with configuration {'type': 'tests.core.test_service.TestServiceA',"
                         " 'parameters': {'value1': 3, 'value2': 3}}",
                         f'{cm.exception}')

    def test_illegal_type_config(self):
        self._assert_illegal_config(
            {
                '_': {}
            },
            'missing service "type" value'
        )
        self._assert_illegal_config(
            {
                '_': {"type": "Test"}
            },
            'invalid service "type" value "Test"'
        )
        self._assert_illegal_config(
            {
                '_': {"type": ".Test"}
            },
            'invalid service "type" value ".Test"'
        )
        self._assert_illegal_config(
            {
                '_': {"type": "Test."}
            },
            'invalid service "type" value "Test."'
        )
        self._assert_illegal_config(
            {
                '_': {"type": "mymodule.Test"}
            },
            'invalid service "type" value: module mymodule.Test not found'
        )
        self._assert_illegal_config(
            {
                '_': {"type": "tests.core.test_service.TestServiceX"}
            },
            'invalid service "type" value: class TestServiceX not found in module tests.core.test_service'
        )
        self._assert_illegal_config(
            {
                '_': {"type": "tests.core.test_service.TestServiceE"}
            },
            'invalid service "type" value: cannot create instance of class tests.core.test_service.TestServiceE'
        )

    def _assert_illegal_config(self, illegal_config, expected_message):
        with self.assertRaises(ServiceError) as cm:
            self.registry.update(illegal_config)
        self.assertEqual(expected_message, f'{cm.exception}')
