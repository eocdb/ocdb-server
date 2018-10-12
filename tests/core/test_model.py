import unittest
from typing import List

from eocdb.core.model import Model


class ModelTest(unittest.TestCase):
    PERSON_1_DICT = dict(name="Hans-Dieter", age=37, size=182.5, female=False)
    PERSON_2_DICT = dict(name="Gertrude", age=32, size=167.2, female=True)

    def test_flat_object_to_dict(self):
        person = Person()
        person.name = "Hans-Dieter"
        person.age = 37
        person.size = 182.5
        person.female = False
        actual_dict = person.to_dict()
        expected_dict = ModelTest.PERSON_1_DICT
        self.assertEqual(expected_dict, actual_dict)

    def test_flat_object_from_dict(self):
        actual_person = Person.from_dict(ModelTest.PERSON_2_DICT)
        expected_person = Person()
        expected_person.name = "Gertrude"
        expected_person.age = 32
        expected_person.size = 167.2
        expected_person.female = True
        self.assertEqual(expected_person, actual_person)

    def test_deep_object_to_dict(self):
        person_1 = Person()
        person_1.name = "Hans-Dieter"
        person_1.age = 37
        person_1.size = 182.5
        person_1.female = False
        person_2 = Person()
        person_2.name = "Gertrude"
        person_2.age = 32
        person_2.size = 167.2
        person_2.female = True
        query = PersonQuery()
        query.expr = 'size > 165.0'
        result = PersonQueryResult()
        result.query = query
        result.persons = [person_1, person_2]
        actual_dict = result.to_dict()
        expected_dict = dict(query=dict(expr="size > 165.0"),
                             persons=[ModelTest.PERSON_1_DICT,
                                      ModelTest.PERSON_2_DICT])
        self.assertEqual(expected_dict, actual_dict)

    def test_deep_object_from_dict(self):
        actual_result = PersonQueryResult.from_dict(dict(query=dict(expr="size > 165.0"),
                                                         persons=[ModelTest.PERSON_1_DICT,
                                                                  ModelTest.PERSON_2_DICT]))
        expected_person_1 = Person()
        expected_person_1.name = "Hans-Dieter"
        expected_person_1.age = 37
        expected_person_1.size = 182.5
        expected_person_1.female = False
        expected_person_2 = Person()
        expected_person_2.name = "Gertrude"
        expected_person_2.age = 32
        expected_person_2.size = 167.2
        expected_person_2.female = True
        expected_query = PersonQuery()
        expected_query.expr = 'size > 165.0'
        expected_result = PersonQueryResult()
        expected_result.query = expected_query
        expected_result.persons = [expected_person_1, expected_person_2]
        self.assertEqual(expected_result, actual_result)


class Person(Model):

    def __init__(self):
        self._name = None
        self._age = None
        self._size = None
        self._female = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        self._age = value

    @property
    def size(self) -> float:
        return self._size

    @size.setter
    def size(self, value: float):
        self._size = value

    @property
    def female(self) -> bool:
        return self._female

    @female.setter
    def female(self, value: bool):
        self._female = value


class PersonQuery(Model):
    def __init__(self):
        self._expr = None

    @property
    def expr(self) -> str:
        return self._expr

    @expr.setter
    def expr(self, value: str):
        self._expr = value


class PersonQueryResult(Model):
    def __init__(self):
        self._query = None
        self._persons = None

    @property
    def query(self) -> PersonQuery:
        return self._query

    @query.setter
    def query(self, value: PersonQuery):
        self._query = value

    @property
    def persons(self) -> List[Person]:
        return self._persons

    @persons.setter
    def persons(self, value: List[Person]):
        self._persons = value
