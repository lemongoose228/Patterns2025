from src.core.abstract_response import AbstractResponse
from src.core.common import common
from src.core.validator import Validator, OperationException


class ResponseCsv(AbstractResponse):
    """
    Класс для формирования ответов в формате CSV (Comma-Separated Values).
    
    Наследует от AbstractResponse и реализует преобразование списка объектов
    в CSV формат с разделителем точка с запятой (;). Обеспечивает корректное
    экранирование значений содержащих специальные символы.
    
    Особенности реализации:
    - Разделитель: точка с запятой (;)
    - Экранирование строк в двойных кавычках при наличии разделителей или переносов
    - Преобразование объектов моделей в их имена
    - Сериализация словарей в строку формата "key1:value1, key2:value2"
    
    Пример выходного формата:
    name;coefficient;base_unit
    грамм;1;
    килограмм;1000;грамм
    "Специальный;продукт";200;"ингредиент:мука, тип:пшеничная"
    """

    def __init__(self):
        """
        Инициализирует CSV форматтер ответов.
        """
        super().__init__()

    def build(self, format: str, data: list) -> str:
        """
        Сформировать CSV представление данных.
        
        Создает CSV строку с заголовками столбцов (имена полей) и данными.
        Обеспечивает корректное экранирование значений содержащих разделители
        или символы переноса строки.
        
        Args:
            format (str): Название формата (игнорируется для CSV, сохраняется для совместимости)
            data (list): Список объектов для преобразования в CSV
            
        Returns:
            str: Строковое представление данных в формате CSV
            
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

        text = ""
        
        # Создание шапки таблицы (заголовки столбцов)
        # Берем первый элемент для определения структуры полей
        item = data[0]
        
        # Получаем список полей объекта (исключая словари и списки)
        fields = common.get_fields(item, is_common=True)
        
        # Формирование строки с заголовками столбцов
        headers = []
        for field in fields:
            headers.append(field)
        
        # Создание строки заголовков с разделителем точка с запятой
        text += ";".join(headers) + "\n"

        # Заполнение таблицы данными
        for item in data:
            row = []
            
            # Обработка каждого поля текущего объекта
            for field in fields:
                value = getattr(item, field)
                
                # Обработка объектов моделей (имеющих атрибут 'name')
                if hasattr(value, 'name'):
                    # Для моделей используем значение поля 'name'
                    row.append(str(value.name))
                
                # Обработка словарей
                elif isinstance(value, dict):
                    # Для словарей создаем строку формата "key1:value1, key2:value2"
                    dict_str = ", ".join([f"{k}:{v}" for k, v in value.items()])
                    
                    # Экранируем строку словаря в двойных кавычках
                    # для предотвращения конфликтов с разделителями
                    row.append(f'"{dict_str}"')
                
                # Обработка строк содержащих специальные символы
                elif isinstance(value, str) and (';' in value or '\n' in value):
                    # Экранируем строки содержащие разделители или переносы строк
                    # в двойных кавычках согласно стандарту CSV
                    row.append(f'"{value}"')
                
                # Обработка простых типов данных
                else:
                    # Для простых типов преобразуем в строку
                    row.append(str(value))
            
            # Добавление строки с данными в CSV
            # Все значения объединяются через разделитель точка с запятой
            text += ";".join(row) + "\n"

        return text