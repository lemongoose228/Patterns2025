import unittest
from datetime import datetime
from uuid import uuid4

from src.logics.basic_convertor import BasicConvertor
from src.logics.date_convertor import DateTimeConvertor
from src.logics.reference_convertor import ReferenceConvertor
from src.logics.list_convertor import ListConvertor
from src.logics.convert_factory import ConvertFactory
from src.core.validator import ArgumentException
from src.models.nomenclature_model import NomenclatureModel
from src.models.unit_measurement_model import UnitMeasurement
from src.core.entity_model import EntityModel


class TestBasicConvertor(unittest.TestCase):

    def setUp(self):
        self.convertor = BasicConvertor()

    def test_can_convert_string(self):
        # Действие & Проверка
        assert self.convertor.can_convert("test string") == True

    def test_can_convert_integer(self):
        # Действие & Проверка
        assert self.convertor.can_convert(123) == True

    def test_can_convert_float(self):
        # Действие & Проверка
        assert self.convertor.can_convert(123.45) == True

    def test_can_convert_boolean(self):
        # Действие & Проверка
        assert self.convertor.can_convert(True) == True
        assert self.convertor.can_convert(False) == True

    def test_can_convert_none(self):
        # Действие & Проверка
        assert self.convertor.can_convert(None) == True

    def test_cannot_convert_object(self):
        # Действие & Проверка
        assert self.convertor.can_convert(UnitMeasurement("test", 1)) == False

    def test_convert_string(self):
        # Подготовка
        value = "test string"
        
        # Действие
        result = self.convertor.convert(value)
        
        # Проверка
        assert result == value

    def test_convert_integer(self):
        # Подготовка
        value = 123
        
        # Действие
        result = self.convertor.convert(value)
        
        # Проверка
        assert result == value

    def test_convert_none(self):
        # Действие
        result = self.convertor.convert(None)
        
        # Проверка
        assert result is None

    def test_convert_invalid_type_raises_exception(self):
        # Подготовка
        value = UnitMeasurement("test", 1)
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            self.convertor.convert(value)


class TestDateTimeConvertor(unittest.TestCase):

    def setUp(self):
        self.convertor = DateTimeConvertor()

    def test_can_convert_datetime(self):
        # Действие & Проверка
        assert self.convertor.can_convert(datetime.now()) == True

    def test_cannot_convert_string(self):
        # Действие & Проверка
        assert self.convertor.can_convert("test") == False



class TestReferenceConvertor(unittest.TestCase):

    def setUp(self):
        self.convertor = ReferenceConvertor()

    def test_can_convert_unit_measurement_model(self):
        # Подготовка
        model = UnitMeasurement("кг", 1)
        
        # Действие & Проверка
        assert self.convertor.can_convert(model) == True


    def test_cannot_convert_string(self):
        # Действие & Проверка
        assert self.convertor.can_convert("test") == False

    def test_convert_unit_measurement_model(self):
        # Подготовка
        model = UnitMeasurement("кг", 1)
        expected_id = model.id
        
        # Действие
        result = self.convertor.convert(model)
        
        # Проверка
        assert result == expected_id


class TestListConvertor(unittest.TestCase):

    def setUp(self):
        self.factory = ConvertFactory()
        self.convertor = ListConvertor(self.factory)

    def test_can_convert_list(self):
        # Действие & Проверка
        assert self.convertor.can_convert([1, 2, 3]) == True
        assert self.convertor.can_convert([]) == True

    def test_cannot_convert_string(self):
        # Действие & Проверка
        assert self.convertor.can_convert("test") == False

