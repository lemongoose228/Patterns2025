from src.logics.convert_factory import ConvertFactory
from src.core.abstract_response import AbstractResponse
from src.core.common import common
from src.core.validator import Validator, OperationException


class ResponseJson(AbstractResponse):
    """
    Класс для формирования ответов в формате JSON.
    
    Наследует от AbstractResponse и реализует преобразование списка объектов
    в JSON структуру. Использует ConvertFactory для корректной сериализации
    сложных типов данных, включая UUID, объекты моделей, словари и списки.
    
    Пример выходного формата:
    [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "грамм",
            "coefficient": 1,
            "base_unit_id": null
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001", 
            "name": "килограмм",
            "coefficient": 1000,
            "base_unit_id": "550e8400-e29b-41d4-a716-446655440000"
        }
    ]
    """

    def __init__(self):
        """
        Инициализирует JSON форматтер ответов и фабрику конверторов.
        """
        super().__init__()
        self._convert_factory = ConvertFactory()  # Создаем экземпляр фабрики

    def build(self, format: str, data: list) -> str:
        """
        Сформировать JSON представление данных.
        
        Преобразует список объектов в JSON массив, где каждый объект
        представлен как JSON объект со своими полями. Использует
        ConvertFactory для корректной сериализации всех типов данных.
        
        Args:
            format (str): Название формата (игнорируется для JSON, сохраняется для совместимости)
            data (list): Список объектов для преобразования в JSON
            
        Returns:
            str: Строковое представление данных в формате JSON с отступами
            
        Raises:
            ArgumentException: Если аргументы не соответствуют ожидаемым типам
            OperationException: Если список данных пуст
        """
        # Валидация входных параметров
        Validator.validate(format, str)
        Validator.validate(data, list)

        # Проверка наличия данных
        if len(data) == 0:
            raise OperationException("Нет данных!")

        result = []
        
        # Обработка каждого объекта в списке данных с использованием ConvertFactory
        for item in data:
            # Используем фабрику для преобразования объекта в словарь
            item_dict = self._convert_factory.convert(item)
            
            # Добавление сериализованного объекта в результирующий список
            result.append(item_dict)

        # Преобразование в JSON строку с поддержкой кириллицы и форматированием
        return result