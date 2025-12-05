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

    """
    Событие - добавление элемента в справочник
    """
    @staticmethod
    def log_reference_add_key() -> str:
        return "log_reference_add"

    """
    Событие - обновление элемента справочника
    """
    @staticmethod
    def log_reference_update_key() -> str:
        return "log_reference_update"

    """
    Событие - удаление элемента справочника
    """
    @staticmethod
    def log_reference_delete_key() -> str:
        return "log_reference_delete"

    """
    Событие - расчет остатков
    """
    @staticmethod
    def log_balance_calculation_key() -> str:
        return "log_balance_calculation"

    """
    Событие - формирование отчета
    """
    @staticmethod
    def log_report_generation_key() -> str:
        return "log_report_generation"

    """
    Событие - складская операция
    """
    @staticmethod
    def log_storage_operation_key() -> str:
        return "log_storage_operation"

    """
    Событие - вызов API метода
    """
    @staticmethod
    def log_api_call_key() -> str:
        return "log_api_call"

    """
    Событие - изменение настроек
    """
    @staticmethod
    def log_settings_change_key() -> str:
        return "log_settings_change"

    """
    Событие - ошибка приложения
    """
    @staticmethod
    def log_error_key() -> str:
        return "log_error"

    """
    Событие - информационное сообщение
    """
    @staticmethod
    def log_info_key() -> str:
        return "log_info"

    """
    Событие - отладочное сообщение
    """
    @staticmethod
    def log_debug_key() -> str:
        return "log_debug"

    # Получить список всех событий
    @staticmethod
    def events():
        return [attr[:-4] for attr in dir(EventType) 
                if not attr.startswith('_') 
                and not callable(getattr(EventType, attr))
                and attr.endswith('_key')]