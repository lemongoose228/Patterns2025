import unittest

from src.core.validator import ArgumentException
from src.settings_manager import SettingsManager


class TestSettingsManager(unittest.TestCase):

    def test_load_company_settings_successful_load_returns_true(self):
        # Подготовка
        filename = "settings.json"
        manager = SettingsManager(filename)

        # Действие
        result = manager.load()

        # Проверка
        assert result is True

    def test_load_company_settings_all_company_fields_populated(self):
        # Подготовка
        filename = "settings.json"
        manager = SettingsManager(filename)

        # Действие
        manager.load()

        # Проверка
        assert manager.settings.company.name != ""
        assert manager.settings.company.INN != ""
        assert manager.settings.company.correspondent_account != ""
        assert manager.settings.company.BIK != ""
        assert manager.settings.company.ownership_type != ""
        assert manager.settings.company.account != ""

    def test_load_company_settings_multiple_managers_same_company_data(self):
        # Подготовка
        filename = "settings.json"
        manager1 = SettingsManager(filename)
        manager2 = SettingsManager(filename)

        # Действие
        manager1.load()
        manager2.load()

        # Проверка
        assert manager1.settings.company == manager2.settings.company

    def test_load_settings_different_location_correct_data_loaded(self):
        # Подготовка
        filepath = "tests/test_data/test_settings.json"
        manager = SettingsManager(filepath)

        # Действие
        manager.load()

        # Проверка
        assert manager.settings.company.name == "Тестовая Компания из другого места"
        assert manager.settings.company.INN == 123456789012

    def test_set_company_none_company_is_none(self):
        # Подготовка
        filename = "settings.json"
        manager = SettingsManager(filename)
        
        # Действие
        manager.settings.company = None

        # Проверка
        assert manager.settings.company is None

    def test_create_settings_manager_wrong_file_throws_argument_exception(self):
        # Подготовка
        filename = "settings.jsen"
        
        # Действие & Проверка
        with self.assertRaises(ArgumentException):
            SettingsManager(filename)