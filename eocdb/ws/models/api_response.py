from ..model import Model


class ApiResponse(Model):

    def __init__(self):
        self._code = None
        self._type = None
        self._message = None

    @property
    def code(self) -> int:
        return self._code

    @code.setter
    def code(self, value: int):
        self._code = value

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str):
        self._message = value
