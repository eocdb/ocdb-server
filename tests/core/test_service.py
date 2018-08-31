from unittest import TestCase

from eocdb.core.service import Service, ServiceRegistry, ServiceError
from tests.core.helpers import TestServiceA, TestServiceB


class ServiceTest(TestCase):

    def test_info(self):
        self.assertEqual(dict(name='Service'), Service.info())
        self.assertEqual(dict(name='TestServiceA'), TestServiceA.info())

    def test_default_instance(self):
        service_a = TestServiceA()
        self.assertIs(service_a, service_a.instance())


class ServiceRegistryTest(TestCase):

    def setUp(self):
        self.registry = ServiceRegistry()

    def test_update_and_find(self):
        self.registry.update({
            "service_a": {
                "type": "tests.core.helpers.TestServiceA",
            },
            "service_b": {
                "type": "tests.core.helpers.TestServiceB",
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
                "type": "tests.core.helpers.TestServiceA",
                "parameters": {
                    "value1": 1,
                },
            },
            "service_b": {
                "type": "tests.core.helpers.TestServiceB",
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
                "type": "tests.core.helpers.TestServiceA",
                "parameters": {
                    "value1": 2,
                },
            },
            "service_c": {
                "type": "tests.core.helpers.TestServiceC",
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
                "type": "tests.core.helpers.TestServiceA",
                "parameters": {
                    "value1": 3,
                },
            },
            "service_c1": {
                "type": "tests.core.helpers.TestServiceC",
            },
            "service_c2": {
                "type": "tests.core.helpers.TestServiceC",
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

    def test_illegal_registry_constr(self):
        with self.assertRaises(ServiceError) as cm:
            # noinspection PyTypeChecker
            self.registry.update([])
        self.assertEqual("service configuration must be a dictionary",
                         f'{cm.exception}')

    def test_illegal_service_init(self):
        with self.assertRaises(ServiceError) as cm:
            self.registry.update({
                "service_a": {
                    "type": "tests.core.helpers.TestServiceA",
                    "parameters": {
                        "value1": 1,
                        "value2": 1,
                    },
                },
            })
        self.assertEqual("failed to initialize service of type <class 'tests.core.helpers.TestServiceA'>"
                         " with configuration {'type': 'tests.core.helpers.TestServiceA',"
                         " 'parameters': {'value1': 1, 'value2': 1}}",
                         f'{cm.exception}')

    def test_illegal_service_update(self):
        self.registry.update({
            "service_a": {
                "type": "tests.core.helpers.TestServiceA",
                "parameters": {
                    "value1": 1,
                    "value2": 2,
                },
            },
        })
        with self.assertRaises(ServiceError) as cm:
            self.registry.update({
                "service_a": {
                    "type": "tests.core.helpers.TestServiceA",
                    "parameters": {
                        "value1": 2,
                        "value2": 2,
                    },
                },
            })
        self.assertEqual("failed to update service of type <class 'tests.core.helpers.TestServiceA'>"
                         " with configuration {'type': 'tests.core.helpers.TestServiceA',"
                         " 'parameters': {'value1': 2, 'value2': 2}}",
                         f'{cm.exception}')

        with self.assertRaises(ServiceError) as cm:
            self.registry.update({
                "service_a": {
                    "type": "tests.core.helpers.TestServiceB",
                    "parameters": {
                        "value1": 1,
                        "value2": 2,
                    },
                },
            })
        self.assertEqual("failed to update service of type <class 'tests.core.helpers.TestServiceA'>"
                         " changing a service's type is not (yet) supported",
                         f'{cm.exception}')

    def test_illegal_service_dispose(self):
        self.registry.update({
            "service_a": {
                "type": "tests.core.helpers.TestServiceA",
                "parameters": {
                    "value1": 3,
                    "value2": 3,
                },
            },
        })
        with self.assertRaises(ServiceError) as cm:
            self.registry.dispose()
        self.assertEqual("failed to dispose service of type <class 'tests.core.helpers.TestServiceA'>"
                         " with configuration {'type': 'tests.core.helpers.TestServiceA',"
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
            'invalid service "type" value: module mymodule not found'
        )
        self._assert_illegal_config(
            {
                '_': {"type": "tests.core.helpers.TestServiceX"}
            },
            'invalid service "type" value: class TestServiceX not found in module tests.core.helpers'
        )
        self._assert_illegal_config(
            {
                '_': {"type": "tests.core.helpers.TestServiceE"}
            },
            'invalid service "type" value: cannot create instance of class tests.core.helpers.TestServiceE'
        )

    def _assert_illegal_config(self, illegal_config, expected_message):
        with self.assertRaises(ServiceError) as cm:
            self.registry.update(illegal_config)
        self.assertEqual(expected_message, f'{cm.exception}')
