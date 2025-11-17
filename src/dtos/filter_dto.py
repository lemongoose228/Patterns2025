from src.core.validator import Validator
from src.models.filter_type import FilterType

class FilterDto:
    __field_name: str = ""
    __value: str = ""
    __type: FilterType = FilterType.EQUALS
    
    @property
    def field_name(self) -> str:
        return self.__field_name
    
    @field_name.setter
    def field_name(self, value: str):
        Validator.validate(value, str)
        self.__field_name = value

    @property
    def value(self) -> str:
        return self.__value
    
    @value.setter
    def value(self, value: str):
        Validator.validate(value, str)
        self.__value = value

    
    @property
    def type(self) -> FilterType:
        return self.__type
    
    @type.setter
    def type(self, value: FilterType):
        Validator.validate(value, FilterType)
        self.__type = value

    @staticmethod
    def from_dict(data: dict) -> 'FilterDto':
        dto = FilterDto()
        dto.field_name = data.get('field_name', '')
        dto.value = data.get('value', '')
        
        filter_type_str = data.get('type', 'EQUALS')
        try:
            dto.type = FilterType[filter_type_str]
        except KeyError:
            dto.type = FilterType.EQUALS
            
        return dto