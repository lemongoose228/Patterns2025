import unittest
import json
import xml.etree.ElementTree as ET

from src.core.validator import ArgumentException
from src.models.unit_measurement_model import UnitMeasurement
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.models.nomenclature_model import NomenclatureModel
from src.logics.response_csv import ResponseCsv
from src.logics.response_markdown import ResponseMarkdown
from src.logics.response_json import ResponseJson
from src.logics.response_xml import ResponseXml


class TestResponseFormats(unittest.TestCase):

    def setUp(self):
        # Создаем тестовые данные для каждого типа модели отдельно
        self.units_data = [
            UnitMeasurement("грамм", 1),
            UnitMeasurement("килограмм", 1000),
            UnitMeasurement("литр", 1)
        ]

        self.groups_data = [
            self._create_group("Ингредиенты"),
            self._create_group("Посуда"),
            self._create_group("Инструменты")
        ]

        # Создаем номенклатуры с зависимостями
        self.ingredients_group = self._create_group("Ингредиенты")
        self.gram_unit = UnitMeasurement("грамм", 1)
        self.nomenclatures_data = [
            NomenclatureModel("мука", "пшеничная мука", self.ingredients_group, self.gram_unit),
            NomenclatureModel("сахар", "сахарный песок", self.ingredients_group, self.gram_unit),
            NomenclatureModel("соль", "поваренная соль", self.ingredients_group, self.gram_unit)
        ]

    def _create_group(self, name):
        group = GroupNomenclatureModel()
        group.name = name
        return group

    # Тесты для единиц измерения
    def test_csv_format_for_units_measurement(self):
        """Тест CSV формата для единиц измерения"""
        response = ResponseCsv()
        result = response.build("csv", self.units_data)

        # Проверка структуры CSV
        lines = result.strip().split('\n')
        self.assertGreaterEqual(len(lines), 4)  # заголовок + 3 строки данных

        # Проверка заголовков
        self.assertIn("name", lines[0])
        self.assertIn("coefficient", lines[0])

        # Проверка данных
        self.assertIn("грамм", result)
        self.assertIn("килограмм", result)
        self.assertIn("литр", result)
        self.assertIn("1000", result)

    def test_markdown_format_for_units_measurement(self):
        """Тест Markdown формата для единиц измерения"""
        response = ResponseMarkdown()
        result = response.build("markdown", self.units_data)

        # Проверка структуры таблицы Markdown
        self.assertIn("| name |", result)
        self.assertIn("| coefficient |", result)
        self.assertIn("| --- |", result)

        # Проверка данных
        self.assertIn("| грамм |", result)
        self.assertIn("| килограмм |", result)
        self.assertIn("| литр |", result)
        self.assertIn("| 1000 |", result)

    def test_json_format_for_units_measurement(self):
        """Тест JSON формата для единиц измерения"""
        response = ResponseJson()
        result = response.build("json", self.units_data)

        # Проверяем что это валидный JSON
        parsed = json.loads(result)
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 3)

        # Проверяем структуру данных
        unit_names = [item["name"] for item in parsed]
        self.assertIn("грамм", unit_names)
        self.assertIn("килограмм", unit_names)
        self.assertIn("литр", unit_names)

        coefficients = [item["coefficient"] for item in parsed]
        self.assertIn(1, coefficients)
        self.assertIn(1000, coefficients)

    def test_xml_format_for_units_measurement(self):
        """Тест XML формата для единиц измерения"""
        response = ResponseXml()
        result = response.build("xml", self.units_data)

        # Проверяем что это валидный XML
        root = ET.fromstring(result)
        self.assertEqual(root.tag, "data")

        # Проверяем структуру данных
        items = root.findall("item")
        self.assertEqual(len(items), 3)

        names = [item.find("name").text for item in items]
        self.assertIn("грамм", names)
        self.assertIn("килограмм", names)
        self.assertIn("литр", names)

    # Тесты для групп номенклатур
    def test_csv_format_for_groups_nomenclature(self):
        """Тест CSV формата для групп номенклатур"""
        response = ResponseCsv()
        result = response.build("csv", self.groups_data)

        # Проверка данных
        self.assertIn("Ингредиенты", result)
        self.assertIn("Посуда", result)
        self.assertIn("Инструменты", result)

    def test_markdown_format_for_groups_nomenclature(self):
        """Тест Markdown формата для групп номенклатур"""
        response = ResponseMarkdown()
        result = response.build("markdown", self.groups_data)

        # Проверка данных
        self.assertIn("| Ингредиенты |", result)
        self.assertIn("| Посуда |", result)
        self.assertIn("| Инструменты |", result)

    def test_json_format_for_groups_nomenclature(self):
        """Тест JSON формата для групп номенклатур"""
        response = ResponseJson()
        result = response.build("json", self.groups_data)

        parsed = json.loads(result)
        group_names = [item["name"] for item in parsed]

        self.assertIn("Ингредиенты", group_names)
        self.assertIn("Посуда", group_names)
        self.assertIn("Инструменты", group_names)

    def test_xml_format_for_groups_nomenclature(self):
        """Тест XML формата для групп номенклатур"""
        response = ResponseXml()
        result = response.build("xml", self.groups_data)

        root = ET.fromstring(result)
        items = root.findall("item")

        names = [item.find("name").text for item in items]
        self.assertIn("Ингредиенты", names)
        self.assertIn("Посуда", names)
        self.assertIn("Инструменты", names)

    # Тесты для номенклатур
    def test_csv_format_for_nomenclatures(self):
        """Тест CSV формата для номенклатур"""
        response = ResponseCsv()
        result = response.build("csv", self.nomenclatures_data)

        # Проверка данных
        self.assertIn("мука", result)
        self.assertIn("сахар", result)
        self.assertIn("соль", result)
        self.assertIn("пшеничная мука", result)
        self.assertIn("сахарный песок", result)

    def test_markdown_format_for_nomenclatures(self):
        """Тест Markdown формата для номенклатур"""
        response = ResponseMarkdown()
        result = response.build("markdown", self.nomenclatures_data)

        # Проверка данных
        self.assertIn("| мука |", result)
        self.assertIn("| сахар |", result)
        self.assertIn("| соль |", result)
        self.assertIn("| пшеничная мука |", result)

    def test_json_format_for_nomenclatures(self):
        """Тест JSON формата для номенклатур"""
        response = ResponseJson()
        result = response.build("json", self.nomenclatures_data)

        parsed = json.loads(result)
        nomenclature_names = [item["name"] for item in parsed]
        full_names = [item["full_name"] for item in parsed]

        self.assertIn("мука", nomenclature_names)
        self.assertIn("сахар", nomenclature_names)
        self.assertIn("соль", nomenclature_names)
        self.assertIn("пшеничная мука", full_names)

    def test_xml_format_for_nomenclatures(self):
        """Тест XML формата для номенклатур"""
        response = ResponseXml()
        result = response.build("xml", self.nomenclatures_data)

        root = ET.fromstring(result)
        items = root.findall("item")

        names = [item.find("name").text for item in items]
        full_names = [item.find("full_name").text for item in items]

        self.assertIn("мука", names)
        self.assertIn("сахар", names)
        self.assertIn("соль", names)
        self.assertIn("пшеничная мука", full_names)

    # Тесты обработки ошибок
    def test_all_formats_handle_empty_data_gracefully(self):
        """Тест обработки пустых данных для всех форматов"""
        formats = [
            (ResponseCsv(), "CSV"),
            (ResponseMarkdown(), "Markdown"),
            (ResponseJson(), "Json"),
            (ResponseXml(), "XML")
        ]

        for response, format_name in formats:
            with self.subTest(format=format_name):
                with self.assertRaises(Exception):
                    response.build(format_name.lower(), [])

    def test_all_formats_handle_single_item(self):
        """Тест обработки одного элемента для всех форматов"""
        single_unit = [UnitMeasurement("штука", 1)]

        formats = [
            (ResponseCsv(), "csv"),
            (ResponseMarkdown(), "markdown"),
            (ResponseJson(), "json"),
            (ResponseXml(), "xml")
        ]

        for response, format_name in formats:
            with self.subTest(format=format_name):
                try:
                    result = response.build(format_name, single_unit)
                    self.assertIsInstance(result, str)
                    self.assertGreater(len(result), 0)
                    self.assertIn("штука", result)
                except Exception as e:
                    self.fail(f"Формат {format_name} не смог обработать один элемент: {e}")