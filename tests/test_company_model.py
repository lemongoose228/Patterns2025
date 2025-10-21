import unittest

from src.models.company_model import CompanyModel


class TestCompanyModel(unittest.TestCase):

    def test_create_company_model_empty_data_after_creation(self):
        # Подготовка
        model = CompanyModel()
        
        # Действие
        # (создание модели уже выполнено)
        
        # Проверка
        assert model.name == ""

    def test_create_company_model_set_name_data_present(self):
        # Подготовка
        model = CompanyModel()
        
        # Действие
        model.name = "test"
        
        # Проверка
        assert model.name != ""