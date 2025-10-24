from src.core.abstract_response import AbstractResponse
from src.core.common import common
from src.core.validator import Validator, OperationException
import json
import uuid


class ResponseJson(AbstractResponse):
    """
    Класс для формирования ответов в формате JSON.
    
    Наследует от AbstractResponse и реализует преобразование списка объектов
    в JSON структуру. Обеспечивает корректную сериализацию сложных типов данных,
    включая UUID, объекты моделей, словари и списки.
    
    Пример выходного формата:
    [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "грамм",
            "coefficient": 1,
            "base_unit": null
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001", 
            "name": "килограмм",
            "coefficient": 1000,
            "base_unit": "грамм"
        }
    ]
    """

    def __init__(self):
        """
        Инициализирует JSON форматтер ответов.
        """
        super().__init__()

    def build(self, format: str, data: list) -> str:
        """
        Сформировать JSON представление данных.
        
        Преобразует список объектов в JSON массив, где каждый объект
        представлен как JSON объект со своими полями. Обеспечивает
        рекурсивную сериализацию вложенных структур.
        
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
        
        # Обработка каждого объекта в списке данных
        for item in data:
            item_dict = {}
            
            # Получение списка полей объекта (исключая словари и списки)
            fields = common.get_fields(item, is_common=True)
            
            # Заполнение словаря значениями полей объекта
            for field in fields:
                value = getattr(item, field)
                
                # Рекурсивная сериализация значения поля
                item_dict[field] = self._serialize_value(value)
            
            # Добавление сериализованного объекта в результирующий список
            result.append(item_dict)

        # Преобразование в JSON строку с поддержкой кириллицы и форматированием
        return json.dumps(result, ensure_ascii=False, indent=2, default=self._json_serializer)

    def _serialize_value(self, value):
        """
        Рекурсивно преобразовать значение в сериализуемый формат.
        
        Обрабатывает различные типы данных:
        - None значения
        - Объекты моделей (с атрибутом 'name') 
        - Словари (рекурсивно)
        - Списки (рекурсивно)
        - Простые типы (str, int, float, bool)
        
        Args:
            value: Значение для сериализации
            
        Returns:
            Значение в сериализуемом формате
        """
        # Обработка None значений
        if value is None:
            return None
        
        # Обработка объектов моделей - используем значение поля 'name'
        elif hasattr(value, 'name'):
            return value.name
        
        # Рекурсивная обработка словарей
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        
        # Рекурсивная обработка списков
        elif isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        
        # Обработка простых типов - возвращаем как есть
        else:
            return value

    def _json_serializer(self, obj):
        """
        Кастомный сериализатор для обработки нестандартных типов данных в JSON.
        
        Используется как параметр default в json.dumps() для обработки типов,
        которые не поддерживаются стандартным сериализатором JSON.
        
        Args:
            obj: Объект для сериализации
            
        Returns:
            Сериализуемое представление объекта
            
        Raises:
            TypeError: Если тип объекта не поддерживается сериализацией
        """
        # Обработка UUID - преобразуем в строку
        if isinstance(obj, uuid.UUID):
            return str(obj)
        
        # Обработка объектов с атрибутами - пытаемся сериализовать их __dict__
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        
        # Для неподдерживаемых типов вызываем стандартное исключение
        else:
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")