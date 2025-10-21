import unittest

from src.core.validator import ArgumentException
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.models.nomenclature_model import NomenclatureModel
from src.models.unit_measurement_model import UnitMeasurement


class TestNomenclatureModel(unittest.TestCase):

    def test_create_nomenclature_model_all_fields_set_correctly(self):
        # Подготовка
        group = GroupNomenclatureModel()
        unit = UnitMeasurement("грамм", 1)
        
        # Действие
        nomenclature_model = NomenclatureModel("Хлеб", "Хлебобулочные изделия", group, unit)

        # Проверка
        assert nomenclature_model.name == "Хлеб"
        assert nomenclature_model.group_nomenclature is not None
        assert nomenclature_model.unit_measurement is not None
        assert nomenclature_model.full_name == "Хлебобулочные изделия"

    def test_set_nomenclature_name_int_value_throws_argument_exception(self):
        # Подготовка
        group = GroupNomenclatureModel()
        unit = UnitMeasurement("грамм", 1)
        nomenclature_model = NomenclatureModel("Хлеб", "Хлебобулочные изделия", group, unit)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            nomenclature_model.name = 123

    def test_set_nomenclature_name_too_long_value_throws_argument_exception(self):
        # Подготовка
        group = GroupNomenclatureModel()
        unit = UnitMeasurement("грамм", 1)
        nomenclature_model = NomenclatureModel("Хлеб", "Хлебобулочные изделия", group, unit)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            nomenclature_model.name = "1" * 51

    def test_set_nomenclature_group_int_value_throws_argument_exception(self):
        # Подготовка
        group = GroupNomenclatureModel()
        unit = UnitMeasurement("грамм", 1)
        nomenclature_model = NomenclatureModel("Хлеб", "Хлебобулочные изделия", group, unit)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            nomenclature_model.group_nomenclature = 123

    def test_set_nomenclature_unit_int_value_throws_argument_exception(self):
        # Подготовка
        group = GroupNomenclatureModel()
        unit = UnitMeasurement("грамм", 1)
        nomenclature_model = NomenclatureModel("Хлеб", "Хлебобулочные изделия", group, unit)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            nomenclature_model.unit_measurement = 123

    def test_set_nomenclature_full_name_int_value_throws_argument_exception(self):
        # Подготовка
        group = GroupNomenclatureModel()
        unit = UnitMeasurement("грамм", 1)
        nomenclature_model = NomenclatureModel("Хлеб", "Хлебобулочные изделия", group, unit)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            nomenclature_model.full_name = 123

    def test_set_nomenclature_full_name_too_long_value_throws_argument_exception(self):
        # Подготовка
        group = GroupNomenclatureModel()
        unit = UnitMeasurement("грамм", 1)
        nomenclature_model = NomenclatureModel("Хлеб", "Хлебобулочные изделия", group, unit)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            nomenclature_model.full_name = "1" * 256