import unittest

from src.core.validator import ArgumentException
from src.settings_manager import SettingsManager


class TestCompanySettingsValidation(unittest.TestCase):

    def setUp(self):
        self.filename = "settings.json"
        self.manager = SettingsManager(self.filename)
        self.manager.load()

    def test_set_company_name_valid_value_value_set_correctly(self):
        # Действие
        self.manager.settings.company.name = "Ромашка"

        # Проверка
        assert self.manager.settings.company.name == "Ромашка"

    def test_set_company_name_none_value_throws_argument_exception(self):
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            self.manager.settings.company.name = None

    def test_set_company_inn_valid_string_value_value_set_correctly(self):
        # Действие
        self.manager.settings.company.INN = "123456789012"

        # Проверка
        assert self.manager.settings.company.INN == 123456789012

    def test_set_company_inn_valid_int_value_value_set_correctly(self):
        # Действие
        self.manager.settings.company.INN = 123456789012

        # Проверка
        assert self.manager.settings.company.INN == 123456789012

    def test_set_company_inn_none_value_throws_argument_exception(self):
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            self.manager.settings.company.INN = None

    def test_set_company_inn_invalid_string_length_throws_argument_exception(self):
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            self.manager.settings.company.INN = "12345678901"

    def test_set_company_account_valid_string_value_value_set_correctly(self):
        # Действие
        self.manager.settings.company.account = "40702810000"

        # Проверка
        assert self.manager.settings.company.account == 40702810000

    def test_set_company_account_valid_int_value_value_set_correctly(self):
        # Действие
        self.manager.settings.company.account = 40702810000

        # Проверка
        assert self.manager.settings.company.account == 40702810000

    def test_set_company_account_invalid_string_length_throws_argument_exception(self):
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            self.manager.settings.company.account = "4070281000"

    def test_set_company_correspondent_account_valid_int_value_value_set_correctly(self):
        # Действие
        self.manager.settings.company.correspondent_account = 30101810000

        # Проверка
        assert self.manager.settings.company.correspondent_account == 30101810000

    def test_set_company_correspondent_account_invalid_string_length_throws_argument_exception(self):
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            self.manager.settings.company.correspondent_account = "3010181000"

    def test_set_company_bik_valid_string_value_value_set_correctly(self):
        # Действие
        self.manager.settings.company.BIK = "144525225"

        # Проверка
        assert self.manager.settings.company.BIK == 144525225

    def test_set_company_bik_valid_int_value_value_set_correctly(self):
        # Действие
        self.manager.settings.company.BIK = 144525225

        # Проверка
        assert self.manager.settings.company.BIK == 144525225

    def test_set_company_bik_invalid_string_length_throws_argument_exception(self):
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            self.manager.settings.company.BIK = "04452522"

    def test_set_company_ownership_type_valid_value_value_set_correctly(self):
        # Действие
        self.manager.settings.company.ownership_type = "АО"

        # Проверка
        assert self.manager.settings.company.ownership_type == "АО"

    def test_set_company_ownership_type_invalid_value_throws_argument_exception(self):
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            self.manager.settings.company.ownership_type = "000 А0О"