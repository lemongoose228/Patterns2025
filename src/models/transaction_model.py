from datetime import datetime
from src.core.validator import Validator, ArgumentException
from src.core.abstract_model import AbstractModel
from src.models.nomenclature_model import NomenclatureModel
from src.models.storage_model import StorageModel
from src.models.unit_measurement_model import UnitMeasurement

class TransactionModel(AbstractModel):
    __date: datetime = None
    __nomenclature: NomenclatureModel = None
    __storage: StorageModel = None
    __quantity: float = 0
    __unit_measurement: UnitMeasurement = None
    __transaction_type: str = ""  # "in" - приход, "out" - расход

    def __init__(self, date: datetime, nomenclature: NomenclatureModel, 
                 storage: StorageModel, quantity: float, unit_measurement: UnitMeasurement, 
                 transaction_type: str):
        super().__init__()
        self.date = date
        self.nomenclature = nomenclature
        self.storage = storage
        self.quantity = quantity
        self.unit_measurement = unit_measurement
        self.transaction_type = transaction_type

    @property
    def date(self) -> datetime:
        return self.__date
    
    @date.setter
    def date(self, value: datetime):
        Validator.validate(value, datetime)
        self.__date = value

    @property
    def nomenclature(self) -> NomenclatureModel:
        return self.__nomenclature
    
    @nomenclature.setter
    def nomenclature(self, value: NomenclatureModel):
        Validator.validate(value, NomenclatureModel)
        self.__nomenclature = value

    @property
    def storage(self) -> StorageModel:
        return self.__storage
    
    @storage.setter
    def storage(self, value: StorageModel):
        Validator.validate(value, StorageModel)
        self.__storage = value

    @property
    def quantity(self) -> float:
        return self.__quantity
    
    @quantity.setter
    def quantity(self, value: float):
        Validator.validate(value, (int, float))
        self.__quantity = float(value)

    @property
    def unit_measurement(self) -> UnitMeasurement:
        return self.__unit_measurement
    
    @unit_measurement.setter
    def unit_measurement(self, value: UnitMeasurement):
        Validator.validate(value, UnitMeasurement)
        self.__unit_measurement = value

    @property
    def transaction_type(self) -> str:
        return self.__transaction_type
    
    @transaction_type.setter
    def transaction_type(self, value: str):
        Validator.validate(value, str)
        if value not in ["in", "out"]:
            raise ArgumentException("Тип транзакции должен быть 'in' или 'out'")
        self.__transaction_type = value

    def get_quantity_in_base_units(self) -> float:
        """Получить количество в базовых единицах измерения"""
        if self.unit_measurement.base_unit is None:
            return self.quantity
        return self.quantity * self.unit_measurement.coefficient