from abc import ABC, abstractmethod
from src.core.validator import Validator
from src.dtos.filter_dto import FilterDto
from src.models.filter_type import FilterType
from src.core.common import common

# Абстрактный класс - прототип
class Prototype:
    __data: list = []

    # Набор данных
    @property
    def data(self):
        return self.__data

    def __init__(self, data: list):
        Validator.validate(data, list)
        self.__data = data

    # Клонирование
    def clone(self, data: list = None) -> "Prototype":
        inner_data = None

        if data is None:
            inner_data = self.__data
        else:
            inner_data = data

        instance = Prototype(inner_data)
        return instance
    
    # Универсальный фильтр
    @staticmethod
    def filter(data: list, filters: list[FilterDto]):
        if len(data) == 0 or len(filters) == 0:
            return data
        
        result = data
        
        for filter_dto in filters:
            filtered_result = []
            
            for item in result:
                if Prototype._apply_filter(item, filter_dto):
                    filtered_result.append(item)
            
            result = filtered_result
        
        return result
    
    @staticmethod
    def _apply_filter(item, filter_dto: FilterDto) -> bool:
        try:
            # Поддержка вложенных свойств через "/"
            if '/' in filter_dto.field_name:
                parts = filter_dto.field_name.split('/')
                current_value = item
                
                for part in parts:
                    # Работаем как с объектами, так и со словарями
                    if isinstance(current_value, dict):
                        if part in current_value:
                            current_value = current_value[part]
                        else:
                            return False
                    elif hasattr(current_value, part):
                        current_value = getattr(current_value, part)
                    else:
                        return False
                
                field_value = current_value
            else:
                # Работаем как с объектами, так и со словарями
                if isinstance(item, dict):
                    if filter_dto.field_name not in item:
                        return False
                    field_value = item[filter_dto.field_name]
                elif hasattr(item, filter_dto.field_name):
                    field_value = getattr(item, filter_dto.field_name)
                else:
                    return False
            
            # Применяем фильтр в зависимости от типа
            return Prototype._compare_values(field_value, filter_dto.value, filter_dto.type)
                
        except Exception:
            return False
    
    @staticmethod
    def _compare_values(field_value, filter_value: str, filter_type: FilterType) -> bool:
        """Сравнение значений в зависимости от типа фильтра"""
        str_field_value = str(field_value)
        str_filter_value = str(filter_value)
        
        if filter_type == FilterType.EQUALS:
            return str_field_value == str_filter_value
        elif filter_type == FilterType.LIKE:
            return str_filter_value.lower() in str_field_value.lower()
        elif filter_type == FilterType.NOT_EQUAL:
            return str_field_value != str_filter_value
        else:
            # Для числовых сравнений пытаемся преобразовать в числа
            try:
                num_field = float(field_value)
                num_filter = float(filter_value)
                
                if filter_type == FilterType.GREATER:
                    return num_field > num_filter
                elif filter_type == FilterType.GREATER_EQUAL:
                    return num_field >= num_filter
                elif filter_type == FilterType.LESS:
                    return num_field < num_filter
                elif filter_type == FilterType.LESS_EQUAL:
                    return num_field <= num_filter
                else:
                    return str_field_value == str_filter_value
                    
            except (ValueError, TypeError):
                # Если не удалось преобразовать в числа, используем строковое сравнение
                if filter_type == FilterType.GREATER:
                    return str_field_value > str_filter_value
                elif filter_type == FilterType.GREATER_EQUAL:
                    return str_field_value >= str_filter_value
                elif filter_type == FilterType.LESS:
                    return str_field_value < str_filter_value
                elif filter_type == FilterType.LESS_EQUAL:
                    return str_field_value <= str_filter_value
                else:
                    return str_field_value == str_filter_value
