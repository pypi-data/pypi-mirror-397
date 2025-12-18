"""Exceptions module"""


class ArkhamError(Exception):
    id: int
    name: str
    message: str

    def __init__(self, id: int, name: str, message: str):
        self.id = id
        self.name = name
        self.message = message
        super().__init__(f"{name} ({id}): {message}")
