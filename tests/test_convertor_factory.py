import unittest
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.models.unit_measurement_model import UnitMeasurement
from src.models.nomenclature_model import NomenclatureModel
from src.logics.convert_factory import ConvertFactory
from datetime import datetime

class TestConvertFactory(unittest.TestCase):

    def setUp(self):
        """Подготовка фабрики конверторов перед каждым тестом"""
        self.factory = ConvertFactory()

    def test_convert_none_returns_empty_dict(self):
        """Проверка конвертации None в пустой словарь"""
        # Действие
        result = self.factory.convert(None)
        
        # Проверка
        self.assertEqual(result, {})


    def test_convert_entity_model(self):
        """Проверка конвертации EntityModel с добавлением _id"""
        # Подготовка
        entity = GroupNomenclatureModel.create("Test Group")
        
        # Действие
        result = self.factory.convert(entity)
        
        # Проверка
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "Test Group")
        self.assertIsInstance(result["id"], str)
        self.assertTrue(len(result["id"]) > 0)

    def test_convert_nomenclature_model(self):
        """Проверка конвертации сложной модели NomenclatureModel"""
        # Подготовка
        group = GroupNomenclatureModel()
        group.name = "Food Group"
        unit = UnitMeasurement.create_gramm()
        nomenclature = NomenclatureModel(
            name="Sugar", 
            fullname="Granulated Sugar", 
            group=group, 
            unit=unit
        )
        
        # Действие
        result = self.factory.convert(nomenclature)
        
        # Проверка
        self.assertEqual(result["name"], "Sugar")
        self.assertEqual(result["full_name"], "Granulated Sugar")
        self.assertIn("group_nomenclature_id", result)
        self.assertIn("unit_measurement_id", result)
        self.assertIsInstance(result["group_nomenclature_id"], str)
        self.assertIsInstance(result["unit_measurement_id"], str)

    def test_convert_factory_not_none(self):
        """Проверка что фабрика создается не None"""
        factory = ConvertFactory()
        self.assertIsNotNone(factory)

    def test_convert_factory_has_convertors(self):
        """Проверка что фабрика инициализирует конверторы"""
        self.assertIsNotNone(self.factory._convertors)
        self.assertTrue(len(self.factory._convertors) > 0)

if __name__ == '__main__':
    unittest.main()