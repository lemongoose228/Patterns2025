import unittest

from src.core.validator import ArgumentException
from src.models.unit_measurement_model import UnitMeasurement


class TestUnitMeasurementModel(unittest.TestCase):

    def test_create_unit_measurement_with_base_unit_all_fields_set_correctly(self):
        # Подготовка
        base_unit = UnitMeasurement("грамм", 1)
        
        # Действие
        new_unit = UnitMeasurement("кг", 1000, base_unit)

        # Проверка
        assert base_unit.name == "грамм"
        assert new_unit.name == "кг"
        assert base_unit.coefficient == 1
        assert new_unit.coefficient == 1000
        assert base_unit.base_unit is None
        assert new_unit.base_unit == base_unit

    def test_set_unit_measurement_name_int_value_throws_argument_exception(self):
        # Подготовка
        base_unit = UnitMeasurement("грамм", 1)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            base_unit.name = 123

    def test_set_unit_measurement_name_none_value_throws_argument_exception(self):
        # Подготовка
        base_unit = UnitMeasurement("грамм", 1)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            base_unit.name = None

    def test_set_unit_measurement_coefficient_none_value_throws_argument_exception(self):
        # Подготовка
        base_unit = UnitMeasurement("грамм", 1)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            base_unit.coefficient = None

    def test_set_unit_measurement_coefficient_string_value_throws_argument_exception(self):
        # Подготовка
        base_unit = UnitMeasurement("грамм", 1)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            base_unit.coefficient = "123"

    def test_set_unit_measurement_base_unit_string_value_throws_argument_exception(self):
        # Подготовка
        base_unit = UnitMeasurement("грамм", 1)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            base_unit.base_unit = "123"