from enum import Enum

class FilterType(Enum):
    EQUALS = "EQUALS"  # Полное совпадение
    LIKE = "LIKE"      # Вхождение строки
    GREATER = "GREATER" # Больше
    GREATER_EQUAL = "GREATER_EQUAL" # Больше или равно
    LESS = "LESS"      # Меньше
    LESS_EQUAL = "LESS_EQUAL" # Меньше или равно
    NOT_EQUAL = "NOT_EQUAL" # Не равно