from typing import Dict, List

from eocdb.core.models.user import User


class DbUser(User):

    def __init__(self,
                 id_: str,
                 name: str,
                 password: str,
                 first_name: str,
                 last_name: str,
                 email: str,
                 phone: str,
                 roles: List[str]):
        super().__init__(name, password, id_, first_name, last_name, email, phone, roles)
        self._id = id_

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value
