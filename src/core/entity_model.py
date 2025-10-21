from src.core.abstract_model import AbstractModel
from src.core.validator import Validator


"""
Общий класс для наследования. Содержит стандартное определение: код, наименование
"""
class EntityModel(AbstractModel):
    __name:str = ""

    def __init__(self):
        super().__init__()


    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, value: str) -> str:
        Validator.validate(value, str, 50, ">")
        self.__name = value.strip()


    # Фабричный метод
    @staticmethod
    def create(name:str):
        item = EntityModel()
        item.name = name
        return item
    
  