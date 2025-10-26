from src.core.abstract_model import AbstractModel
from src.core.validator import Validator
from src.core.abstract_convertor import AbstractConvertor


class ReferenceConvertor(AbstractConvertor):
    def convert(self, value) -> any:
        Validator.validate(value, AbstractModel)
        return value.id

    def can_convert(self, value) -> bool:
        return isinstance(value, AbstractModel)