from src.core.validator import Validator
from src.core.abstract_convertor import AbstractConvertor


class ListConvertor(AbstractConvertor):
    def __init__(self, convert_factory):
        self.convert_factory = convert_factory

    def convert(self, value) -> any:
        Validator.validate(value, list)
        return [self.convert_factory._convert_item(item) for item in value]

    def can_convert(self, value) -> bool:
        return isinstance(value, list)