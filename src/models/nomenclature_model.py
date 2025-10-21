from src.models.unit_measurement_model import UnitMeasurement
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.core.validator import Validator
from src.core.entity_model import EntityModel


class NomenclatureModel(EntityModel):
    __full_name: str = ""
    __group_nomenclature: GroupNomenclatureModel = None
    __unit_measurement: UnitMeasurement = None


    def __init__(self, name, fullname, group, unit):
        super().__init__()
        self.name = name
        self.full_name = fullname
        self.group_nomenclature = group
        self.unit_measurement = unit


    @property
    def full_name(self) -> str:
        return self.__full_name
    
    @full_name.setter
    def full_name(self, value: str) -> str:
        Validator.validate(value, str, 255, ">")
        self.__full_name = value

    
    @property
    def group_nomenclature(self):
        return self.__group_nomenclature

    @group_nomenclature.setter
    def group_nomenclature(self, value: GroupNomenclatureModel):
        Validator.validate(value, GroupNomenclatureModel)
        self.__group_nomenclature = value        


    @property
    def unit_measurement(self):
        return self.__unit_measurement
    
    @unit_measurement.setter
    def unit_measurement(self, value: UnitMeasurement):
        Validator.validate(value, UnitMeasurement)
        self.__unit_measurement = value           
