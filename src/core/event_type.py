
"""
Типы событий
"""
class EventType:
    """
    Событие - обновились справочники
    """
    @staticmethod
    def change_reference_type_key() -> str:
        return "change_reference_type"


    """
    Событие - обновилась единица измерения у номенклатуры
    """
    @staticmethod
    def change_nomenclature_unit_key() -> str:
        return "change_nomenclature_unit"


    """
    Событие - удаление номенклатуры
    """
    @staticmethod
    def delete_nomenclature_key() -> str:
        return "delete_nomenclature"

    """
    Событие - удаление группы номенклатур
    """
    @staticmethod
    def delete_group_nomenclature_key() -> str:
        return "delete_group_nomenclature"

    """
    Событие - удаление склада
    """
    @staticmethod
    def delete_storage_key() -> str:
        return "delete_storage"

    """
    Событие - удаление единицы измерения
    """
    @staticmethod
    def delete_unit_key() -> str:
        return "delete_unit"

    # Получить список всех событий
    def events(self):
        return [attr[:-4] for attr in dir(self) 
                if not attr.startswith('_') 
                and not callable(getattr(self, attr))
                and attr.endswith('_key')]    