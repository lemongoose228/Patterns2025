from src.core.abstract_response import AbstractResponse
from src.core.common import common
from src.core.validator import Validator, OperationException
import xml.etree.ElementTree as ET


class ResponseXml(AbstractResponse):
    """
    Класс для формирования ответов в формате XML.
    
    Наследует от AbstractResponse и реализует преобразование списка объектов
    в XML структуру. Поддерживает сериализацию простых типов, объектов моделей
    и словарей.
    
    Пример XML структуры:
    <data>
        <item>
            <name>Значение</name>
            <field>Другое значение</field>
            <dictionary>
                <entry key="ключ1" value="значение1"/>
                <entry key="ключ2" value="значение2"/>
            </dictionary>
        </item>
    </data>
    """

    def __init__(self):
        """
        Инициализирует XML форматтер ответов.
        """
        super().__init__()

    def build(self, format: str, data: list) -> str:
        """
        Сформировать XML представление данных.
        
        Создает XML структуру, где каждый объект представлен как элемент <item>,
        а его поля - как дочерние элементы. Объекты моделей сериализуются по их
        имени, словари - как набор элементов <entry> с атрибутами key и value.
        
        Args:
            format (str): Название формата (игнорируется для XML, сохраняется для совместимости)
            data (list): Список объектов для преобразования в XML
            
        Returns:
            str: Строковое представление данных в формате XML
            
        Raises:
            ArgumentException: Если аргументы не соответствуют ожидаемым типам
            OperationException: Если список данных пуст
        """
        # Валидация входных параметров
        Validator.validate(format, str)
        Validator.validate(data, list)

        if len(data) == 0:
            raise OperationException("Нет данных!")

        # Создание корневого элемента XML
        root = ET.Element("data")
        
        # Обработка каждого объекта в списке данных
        for item in data:
            # Создание элемента для текущего объекта
            item_element = ET.SubElement(root, "item")
            
            # Получение списка полей объекта (исключая словари и списки)
            fields = common.get_fields(item, is_common=True)
            
            # Обработка каждого поля объекта
            for field in fields:
                value = getattr(item, field)
                
                # Обработка объектов моделей (имеющих атрибут 'name')
                if hasattr(value, 'name'):
                    field_element = ET.SubElement(item_element, field)
                    field_element.text = str(value.name)
                
                # Обработка словарей
                elif isinstance(value, dict):
                    field_element = ET.SubElement(item_element, field)
                    
                    # Создание элементов для каждой пары ключ-значение в словаре
                    for key, dict_value in value.items():
                        sub_element = ET.SubElement(field_element, "entry")
                        sub_element.set("key", str(key))
                        sub_element.set("value", str(dict_value))
                
                # Обработка простых типов данных
                else:
                    field_element = ET.SubElement(item_element, field)
                    field_element.text = str(value)

        # Преобразование XML дерева в строку
        return ET.tostring(root, encoding='unicode', method='xml')