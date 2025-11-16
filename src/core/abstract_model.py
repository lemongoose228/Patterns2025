from abc import ABC, abstractmethod
import uuid

from src.core.validator import Validator

class AbstractModel(ABC):
    __id: str = ""

    @abstractmethod
    def __init__(self):
        super().__init__()
        self.__id: str = str(uuid.uuid4())


    @property
    def id(self) -> str:
        return self.__id
    

    @id.setter
    def id(self, value: str) -> str:
        Validator.validate(value, str)
        self.__id = value.strip()
                

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, AbstractModel):
            return False

        return self.__id == value.id