from src.logics.list_convertor import ListConvertor
from src.core.abstract_model import AbstractModel
from src.core.abstract_convertor import AbstractConvertor
from src.core.common import common
from src.logics.basic_convertor import BasicConvertor
from src.logics.date_convertor import DateTimeConvertor
from src.logics.reference_convertor import ReferenceConvertor


class ConvertFactory:
    def __init__(self):
        self._convertors = [
            BasicConvertor(),
            DateTimeConvertor(), 
            ReferenceConvertor()
        ]
        # ListConvertor добавляется после инициализации, чтобы избежать циклической зависимости
        self._convertors.append(ListConvertor(self))
    
    def convert(self, obj) -> dict:
        if obj is None:
            return {}
            
        result = {}
        fields = common.get_fields(obj)
        
        for field in fields:
            try:
                value = getattr(obj, field)
                converted_value = self._convert_item(value)
                
                # Для ReferenceConvertor добавляем суффикс _id к имени поля
                if isinstance(value, AbstractModel):
                    result[f"{field}_id"] = converted_value
                else:
                    result[field] = converted_value
                    
            except Exception as e:
                # Пропускаем поля, которые не удалось сконвертировать
                continue
        
        return result
    
    def _convert_item(self, value) -> any:
        """Рекурсивно конвертирует отдельный элемент"""
        # Если это список, обрабатываем каждый элемент рекурсивно
        if isinstance(value, list):
            return [self.convert(item) for item in value]
        
        # Для простых значений ищем подходящий конвертор
        else:
            convertor = self._find_convertor(value)
            if convertor:
                return convertor.convert(value)
            else:
                # Если конвертор не найден, возвращаем как есть
                return value
    
    def _find_convertor(self, value) -> AbstractConvertor:
        for convertor in self._convertors:
            if convertor.can_convert(value):
                return convertor
        return None