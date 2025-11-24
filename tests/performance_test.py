import unittest
import time
import random
import os
from datetime import datetime, timedelta
from src.logics.balance_service import BalanceService
from src.start_service import StartService
from src.settings_manager import SettingsManager
from src.models.transaction_model import TransactionModel

class TestBalanceServicePerformance(unittest.TestCase):
    
    def setUp(self):
        self.start_service = StartService()
        self.settings_manager = SettingsManager("test_data/test_settings.json")
        self.balance_service = BalanceService(self.start_service, self.settings_manager)
        self.balance_service.balances_file = "test_data/test_balances_cache.json"
        
        # Создаем тестовые данные
        self.start_service.start()
        self._create_test_transactions(5000)
    
    def tearDown(self):
        if os.path.exists("test_data/test_balances_cache.json"):
            os.remove("test_data/test_balances_cache.json")
    
    def _create_test_transactions(self, num_transactions):
        """Создание тестовых транзакций"""
        nomenclatures = list(self.start_service.nomenclatures.values())
        storages = list(self.start_service.storages.values())
        gramm = self.start_service.units_measure["gramm"]
        
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(num_transactions):
            transaction_date = base_date + timedelta(days=random.randint(0, 365))
            nomenclature = random.choice(nomenclatures)
            storage = random.choice(storages)
            quantity = random.randint(100, 5000)
            transaction_type = random.choice(["in", "out"])
            
            transaction = TransactionModel(
                date=transaction_date,
                nomenclature=nomenclature,
                storage=storage,
                quantity=quantity,
                unit_measurement=gramm,
                transaction_type=transaction_type
            )
            
            self.start_service.transactions[transaction.id] = transaction

    def _create_test_transactions(self, num_transactions):
        """Создание тестовых транзакций"""
        nomenclatures = list(self.start_service.nomenclatures.values())
        storages = list(self.start_service.storages.values())
        gramm = self.start_service.units_measure["gramm"]

        # Создаем транзакции равномерно распределенные за последний год
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
        total_days = (end_date - start_date).days

        for i in range(num_transactions):
            # Равномерно распределяем транзакции по всему периоду
            days_offset = (i * total_days) // num_transactions
            transaction_date = start_date + timedelta(days=days_offset)

            nomenclature = random.choice(nomenclatures)
            storage = random.choice(storages)
            quantity = random.randint(100, 5000)
            transaction_type = random.choice(["in", "out"])

            transaction = TransactionModel(
                date=transaction_date,
                nomenclature=nomenclature,
                storage=storage,
                quantity=quantity,
                unit_measurement=gramm,
                transaction_type=transaction_type
            )

            self.start_service.transactions[transaction.id] = transaction

    def test_performance_with_progressive_blocking_dates(self):
        """Нагрузочный тест с постепенным отодвиганием даты блокировки"""
        target_date = datetime.now()

        # Начинаем с самой ранней даты в транзакциях и отодвигаем на месяц каждый раз
        all_transactions = list(self.start_service.transactions.values())
        if not all_transactions:
            self.skipTest("Нет транзакций для тестирования")

        # Находим самую раннюю дату среди транзакций
        earliest_date = min(transaction.date for transaction in all_transactions)
        current_blocking_date = earliest_date

        # Определяем конечную дату (текущая дата минус 1 день)
        end_date = datetime.now() - timedelta(days=1)

        print("Тестирование с постепенным отодвиганием даты блокировки:")
        print(f"Период транзакций: {earliest_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
        print(f"Целевая дата расчета: {target_date.strftime('%Y-%m-%d')}")
        print("=" * 80)

        month_count = 0
        results = []

        while current_blocking_date <= end_date:
            month_count += 1
            test_name = f"Блокировка месяц {month_count}"

            with self.subTest(test_name=test_name, month=month_count):
                # Устанавливаем дату блокировки
                self.settings_manager.settings.blocking_date = current_blocking_date

                # Предварительно рассчитываем кэш
                cache_start_time = time.time()
                cache_success = self.balance_service.calculate_turnovers_until_blocking_date()
                cache_time = time.time() - cache_start_time

                # Измеряем время расчета остатков
                calculation_start_time = time.time()
                balances = self.balance_service.calculate_balances_until_date(target_date)
                calculation_time = time.time() - calculation_start_time

                total_time = cache_time + calculation_time

                # Проверяем корректность
                self.assertTrue(cache_success, "Не удалось рассчитать кэш")
                self.assertIsInstance(balances, dict)
                self.assertEqual(len(balances), len(self.start_service.nomenclatures))

                # Проверяем производительность
                self.assertLess(total_time, 3.0, f"Тест '{test_name}' занял {total_time:.2f} сек")

                # Собираем статистику
                transactions_before = self._count_transactions_before_date(current_blocking_date)
                transactions_after = self._count_transactions_after_date(current_blocking_date, target_date)

                result = {
                    'blocking_date': current_blocking_date,
                    'cache_time': cache_time,
                    'calculation_time': calculation_time,
                    'total_time': total_time,
                    'transactions_before': transactions_before,
                    'transactions_after': transactions_after,
                    'balances_count': len(balances)
                }
                results.append(result)

                print(f"{test_name}:")
                print(f"  Дата блокировки: {current_blocking_date.strftime('%Y-%m-%d')}")
                print(f"  Время расчета: {calculation_time:.3f} сек")
                print(f"  Транзакций до блокировки: {transactions_before}")
                print(f"  Транзакций после блокировки: {transactions_after}")
                print("-" * 50)

                # Сдвигаем дату блокировки на следующий месяц
                current_blocking_date = self._add_months(current_blocking_date, 1)

                # Если вышли за пределы целевой даты, останавливаемся
                if current_blocking_date > target_date:
                    break

        # Выводим итоговую статистику
        print(results)

    def _count_transactions_before_date(self, target_date):
        """Подсчет транзакций до указанной даты (включительно)"""
        count = 0
        for transaction in self.start_service.transactions.values():
            if transaction.date <= target_date:
                count += 1
        return count

    def _count_transactions_after_date(self, start_date, end_date):
        """Подсчет транзакций после указанной даты до конечной даты"""
        count = 0
        for transaction in self.start_service.transactions.values():
            if start_date < transaction.date <= end_date:
                count += 1
        return count

    def _add_months(self, source_date, months):
        """Добавляет указанное количество месяцев к дате"""
        import calendar
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        day = min(source_date.day, calendar.monthrange(year, month)[1])
        return datetime(year, month, day, source_date.hour, source_date.minute, source_date.second)