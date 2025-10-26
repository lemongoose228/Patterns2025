from datetime import datetime
from src.core.validator import Validator
from src.core.abstract_convertor import AbstractConvertor


class DateTimeConvertor(AbstractConvertor):
    def convert(self, value) -> any:
        Validator.validate(value, datetime)
        return value.isoformat() if value else None

    def can_convert(self, value) -> bool:
        return isinstance(value, datetime)