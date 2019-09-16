from enum import Enum, unique
from typing import List


@unique
class Roles(Enum):
    ADMIN = 'admin'
    SUBMIT = 'submit'

    @classmethod
    def is_admin(cls, roles: List[str]):
        if Roles.ADMIN.value in roles:
            return True
        return False

    @classmethod
    def is_submit(cls, roles: List[str]):
        if Roles.SUBMIT.value in roles:
            return True
        return False

