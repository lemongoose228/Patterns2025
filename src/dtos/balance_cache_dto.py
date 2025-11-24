from src.core.validator import Validator
from datetime import datetime
from src.core.common import common


class BalanceCacheDto:
    """
    DTO для хранения кэшированных данных балансов
    """

    def __init__(self):
        self.__nomenclature_id: str = ""
        self.__balance: float = 0.0
        self.__calculation_date: datetime = None
        self.__nomenclature_data: dict = {}

    @property
    def nomenclature_id(self) -> str:
        return self.__nomenclature_id

    @nomenclature_id.setter
    def nomenclature_id(self, value: str):
        Validator.validate(value, str)
        self.__nomenclature_id = value

    @property
    def balance(self) -> float:
        return self.__balance

    @balance.setter
    def balance(self, value: float):
        Validator.validate(value, (int, float))
        self.__balance = float(value)

    @property
    def calculation_date(self) -> datetime:
        return self.__calculation_date

    @calculation_date.setter
    def calculation_date(self, value: datetime):
        Validator.validate(value, datetime)
        self.__calculation_date = value

    @property
    def nomenclature_data(self) -> dict:
        return self.__nomenclature_data

    @nomenclature_data.setter
    def nomenclature_data(self, value: dict):
        Validator.validate(value, dict)
        self.__nomenclature_data = value

    @staticmethod
    def from_dict(data: dict) -> 'BalanceCacheDto':
        """Создать DTO из словаря с использованием setattr"""
        dto = BalanceCacheDto()

        # Получаем все поля DTO
        fields = common.get_fields(dto)

        # Устанавливаем поля через setattr
        for field in fields:
            if field in data:
                try:
                    setattr(dto, field, data[field])
                except Exception:
                    # Пропускаем поля, которые не удалось установить
                    continue

        # Обрабатываем специальные поля
        if 'calculation_date' in data and data['calculation_date']:
            try:
                dto.calculation_date = datetime.fromisoformat(data['calculation_date'])
            except ValueError:
                pass

        return dto

    def to_dict(self) -> dict:
        """Преобразовать DTO в словарь"""
        result = {}
        fields = common.get_fields(self)

        for field in fields:
            try:
                value = getattr(self, field)
                # Сериализуем datetime в строку
                if isinstance(value, datetime):
                    result[field] = value.isoformat()
                else:
                    result[field] = value
            except Exception:
                continue

        return result