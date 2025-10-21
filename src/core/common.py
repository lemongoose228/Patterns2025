from src.core.entity_model import EntityModel
from src.core.abstract_model import AbstractModel
from src.core.validator import ArgumentException

# Набор статических общих методов
class common:

    """
    Получить список наименований всех моделей
    """
    @staticmethod
    def get_models() -> list:
        result = []
        for  inheritor in EntityModel.__subclasses__():
            result.append(inheritor.__name__)

        return result    


    """
    Получить полный список полей любой модели
        - is_common = True - исключить из списка словари и списки
    """
    @staticmethod
    def get_fields(source, is_common: bool = False) -> list:
        if source is None:
            raise ArgumentException("Некорректно переданы аргументы!")

        items = list(filter(lambda x: not x.startswith("_") , dir(source))) 
        result = []

        for item in items:
            attribute = getattr(source.__class__, item)
            if isinstance(attribute, property):
                value = getattr(source, item)

                # Флаг. Только простые типы и модели включать
                if is_common == True and (isinstance(value, dict) or isinstance(value, list) ):
                    continue

                result.append(item)

        return result