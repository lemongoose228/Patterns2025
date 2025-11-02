from abc import ABC, abstractmethod
from datetime import datetime
from src.core.abstract_model import AbstractModel
from src.core.validator import Validator

class AbstractConvertor(ABC):
    @abstractmethod
    def convert(self, field_name: str, value) -> any:
        pass

    @abstractmethod
    def can_convert(self, value) -> bool:
        pass