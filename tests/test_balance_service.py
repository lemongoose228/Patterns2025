import unittest
import os
from datetime import datetime, timedelta

from src.dtos.filter_dto import FilterDto
from src.logics.balance_service import BalanceService
from src.start_service import StartService
from src.settings_manager import SettingsManager
from src.models.storage_model import StorageModel

class TestBalanceService(unittest.TestCase):
    
    def setUp(self):
        self.start_service = StartService()
        self.settings_manager = SettingsManager("test_data/test_settings.json")
        self.settings_manager.load()
        self.balance_service = BalanceService(self.start_service, self.settings_manager)
        self.balance_service.balances_file = "test_data/test_balances_cache.json"

        # Создаем тестовые данные
        self.start_service.start()

    def tearDown(self):
        # Очищаем тестовые файлы
        if os.path.exists("test_data/test_balances_cache.json"):
            os.remove("test_data/test_balances_cache.json")

    def test_calculate_full_balances_with_prototype(self):
        """Тест полного расчета остатков с использованием Prototype"""
        target_date = datetime.now()
        balances = self.balance_service._calculate_full_balances_with_prototype(target_date)

        self.assertIsInstance(balances, dict)
        # Проверяем, что для каждой номенклатуры есть запись
        self.assertEqual(len(balances), len(self.start_service.nomenclatures))

    def test_get_transactions_in_period_with_prototype(self):
        """Тест получения транзакций за период с использованием Prototype"""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        transactions = self.balance_service._get_transactions_in_period_with_prototype(start_date, end_date)

        self.assertIsInstance(transactions, list)
        # Проверяем, что все транзакции в указанном периоде
        for transaction in transactions:
            self.assertTrue(start_date <= transaction.date <= end_date)

    def test_get_transactions_with_storage_filter(self):
        """Тест фильтрации транзакций по складу с использованием Prototype"""
        storage = list(self.start_service.storages.values())[0]
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        transactions = self.balance_service._get_transactions_in_period_with_prototype(
            start_date, end_date, storage
        )

        for transaction in transactions:
            self.assertEqual(transaction.storage.id, storage.id)
            self.assertTrue(start_date <= transaction.date <= end_date)

    def test_get_transactions_with_complex_filters(self):
        """Тест комплексной фильтрации транзакций"""
        # Создаем комплексные фильтры
        filters = [
            FilterDto.from_dict({
                "field_name": "transaction_type",
                "value": "in",
                "type": "EQUALS"
            }),
            FilterDto.from_dict({
                "field_name": "quantity",
                "value": "500",
                "type": "GREATER"
            })
        ]

        transactions = self.balance_service.get_transactions_with_complex_filters(filters)

        self.assertIsInstance(transactions, list)
        for transaction in transactions:
            self.assertEqual(transaction.transaction_type, "in")
            self.assertGreater(transaction.quantity, 500)

    def test_calculate_turnovers_with_blocking_date(self):
        """Тест расчета с датой блокировки"""
        # Устанавливаем дату блокировки
        blocking_date = datetime.now() - timedelta(days=15)
        self.settings_manager.settings.blocking_date = blocking_date

        # Рассчитываем и сохраняем обороты
        result = self.balance_service.calculate_turnovers_until_blocking_date()
        self.assertTrue(result)

        # Проверяем, что файл кэша создан
        self.assertTrue(os.path.exists(self.balance_service.balances_file))

    def test_balance_calculation_with_caching(self):
        """Тест расчета остатков с использованием кэша"""
        # Устанавливаем дату блокировки
        blocking_date = datetime.now() - timedelta(days=15)
        self.settings_manager.settings.blocking_date = blocking_date

        # Сохраняем кэш
        self.balance_service.calculate_turnovers_until_blocking_date()

        # Рассчитываем остатки на дату после блокировки
        target_date = datetime.now()
        balances = self.balance_service.calculate_balances_until_date(target_date)

        self.assertIsInstance(balances, dict)
        self.assertEqual(len(balances), len(self.start_service.nomenclatures))

    def test_get_balance_report(self):
        """Тест получения отчета по остаткам"""
        target_date = datetime.now()
        report = self.balance_service.get_balance_report(target_date)

        self.assertIsInstance(report, list)
        for item in report:
            self.assertIn('nomenclature_name', item)
            self.assertIn('balance', item)
            self.assertIn('calculation_date', item)


if __name__ == '__main__':
    unittest.main()