from src.core.validator import Validator
from src.core.entity_model import EntityModel
from src.models.nomenclature_model import NomenclatureModel


class RecipeModel(EntityModel):
    __description: str = ""
    __ingredients = {}

    def __init__(self, name, description):
        super().__init__()
        self.name = name
        self.description = description


    @property
    def description(self) -> str:
        return self.__description
    
    @description.setter
    def description(self, value: str) -> str:
        Validator.validate(value, str, 2000, ">")
        self.__description = value.strip()

    @property
    def ingredients(self):
        return self.__ingredients
    

    

    