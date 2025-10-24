from src.core.abstract_response import AbstractResponse
from src.core.common import common
from src.core.validator import Validator, OperationException


class ResponseMarkdown(AbstractResponse):
    """
    Класс для формирования ответов в формате Markdown таблицы.
    
    Наследует от AbstractResponse и реализует преобразование списка объектов
    в таблицу формата Markdown. Поддерживает сериализацию простых типов, 
    объектов моделей и словарей.
    
    Пример выходного формата:
    | name | coefficient | base_unit |
    | --- | --- | --- |
    | грамм | 1 | None |
    | килограмм | 1000 | грамм |
    | литр | 1 | None |
    """

    def __init__(self):
        """
        Инициализирует Markdown форматтер ответов.
        """
        super().__init__()

    def build(self, format: str, data: list) -> str:
        """
        Сформировать Markdown таблицу из данных.
        
        Создает таблицу в формате Markdown, где первая строка - заголовки столбцов
        (имена полей), вторая строка - разделители, а последующие строки - данные.
        
        Args:
            format (str): Название формата (игнорируется для Markdown, сохраняется для совместимости)
            data (list): Список объектов для преобразования в Markdown таблицу
            
        Returns:
            str: Строковое представление данных в формате Markdown таблицы
            
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

        # Дополнительная проверка на пустой список (избыточная, но оставлена для ясности)
        if len(data) == 0:
            return ""

        # Создание шапки таблицы
        # Берем первый элемент для определения структуры полей
        item = data[0]
        
        # Получаем список полей объекта (исключая словари и списки)
        fields = common.get_fields(item, is_common=True)
        
        # Создание строки с заголовками столбцов
        # Формат: | field1 | field2 | field3 |
        text = "| " + " | ".join(fields) + " |\n"
        
        # Создание строки с разделителями столбцов
        # Формат: | --- | --- | --- |
        text += "| " + " | ".join(["---"] * len(fields)) + " |\n"

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
                    # Для словарей выводим количество элементов
                    row.append(str(len(value)))
                
                # Обработка простых типов данных
                else:
                    # Для простых типов преобразуем в строку
                    row.append(str(value))
            
            # Добавление строки с данными в таблицу
            # Формат: | value1 | value2 | value3 |
            text += "| " + " | ".join(row) + " |\n"

        return text