from eocdb.core.models.links import Links


class DbLinks(Links):
    def __init__(self,
                 id_: str,
                 name, str,
                 content: str):
        super().__init__(name, content)
        self._id = id_

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value
