from src.core.validator import Validator
from src.core.abstract_convertor import AbstractConvertor


class BasicConvertor(AbstractConvertor):
    def convert(self, value) -> any:
        Validator.validate(value, (str, int, float, bool, type(None)))
        return value

    def can_convert(self, value) -> bool:
        return isinstance(value, (str, int, float, bool)) or value is None