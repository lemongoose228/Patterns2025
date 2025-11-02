import unittest
from datetime import datetime, timedelta
from src.logics.turnover_report_service import TurnoverReportService
from src.start_service import StartService
from src.models.storage_model import StorageModel
from src.core.validator import Validator, ArgumentException

class TestTurnoverReportService(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных"""
        self.start_service = StartService()
        self.start_service.start()  # Инициализируем тестовые данные
        self.turnover_service = TurnoverReportService(self.start_service)

    def test_not_none_turnover_service_initialization(self):
        """Проверка инициализации сервиса ОСВ"""
        # Действие
        service = TurnoverReportService(self.start_service)
        
        # Проверка
        assert service is not None
        assert service.start_service is not None

    def test_generate_turnover_report_not_none(self):
        """Проверка формирования отчета ОСВ"""
        # Подготовка
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        # Действие
        result = self.turnover_service.generate_turnover_report(start_date, end_date)
        
        # Проверка
        assert result is not None
        assert isinstance(result, list)

    def test_generate_turnover_report_with_storage(self):
        """Проверка формирования отчета ОСВ с указанием склада"""
        # Подготовка
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        storage = list(self.start_service.storages.values())[0]  # Берем первый склад
        
        # Действие
        result = self.turnover_service.generate_turnover_report(start_date, end_date, storage)
        
        # Проверка
        assert result is not None
        assert isinstance(result, list)

    def test_generate_turnover_report_structure(self):
        """Проверка структуры данных отчета ОСВ"""
        # Подготовка
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        # Действие
        result = self.turnover_service.generate_turnover_report(start_date, end_date)
        
        # Проверка
        if len(result) > 0:
            report_item = result[0]
            assert "nomenclature_name" in report_item
            assert "unit_measurement" in report_item
            assert "opening_balance" in report_item
            assert "income" in report_item
            assert "outcome" in report_item
            assert "closing_balance" in report_item
            
            # Проверяем типы данных
            assert isinstance(report_item["opening_balance"], (int, float))
            assert isinstance(report_item["income"], (int, float))
            assert isinstance(report_item["outcome"], (int, float))
            assert isinstance(report_item["closing_balance"], (int, float))

    def test_generate_turnover_report_invalid_dates(self):
        """Проверка обработки невалидных дат"""
        # Подготовка
        start_date = datetime.now()
        end_date = datetime.now() - timedelta(days=1)  # start_date > end_date
        
        # Действие и Проверка
        with self.assertRaises(ArgumentException):
            self.turnover_service.generate_turnover_report(start_date, end_date)

    def test_generate_turnover_report_empty_data(self):
        """Проверка формирования отчета при отсутствии транзакций"""
        # Подготовка
        start_service_empty = StartService()
        # Не вызываем start() чтобы не создавать транзакции
        start_service_empty.data["nomenclature"] = {}
        start_service_empty.data["transaction"] = {}
        
        turnover_service_empty = TurnoverReportService(start_service_empty)
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        # Действие
        result = turnover_service_empty.generate_turnover_report(start_date, end_date)
        
        # Проверка
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

    def test_calculate_balance_method(self):
        """Проверка метода расчета баланса"""
        # Подготовка
        nomenclature = list(self.start_service.nomenclatures.values())[0]
        transactions = list(self.start_service.transactions.values())
        start_date = datetime.now() - timedelta(days=15)
        end_date = datetime.now()
        
        # Действие
        balance = self.turnover_service._calculate_balance_for_nomenclature(
            nomenclature, transactions, start_date, end_date, None
        )
        
        # Проверка
        assert isinstance(balance, (int, float))

    def test_calculate_turnover_method(self):
        """Проверка метода расчета оборота"""
        # Подготовка
        nomenclature = list(self.start_service.nomenclatures.values())[0]
        transactions = list(self.start_service.transactions.values())
        start_date = datetime.now() - timedelta(days=15)
        end_date = datetime.now()
        
        # Действие
        income = self.turnover_service._calculate_turnover_for_nomenclature(
            nomenclature, transactions, start_date, end_date, None, "in"
        )
        outcome = self.turnover_service._calculate_turnover_for_nomenclature(
            nomenclature, transactions, start_date, end_date, None, "out"
        )
        
        # Проверка
        assert isinstance(income, (int, float))
        assert isinstance(outcome, (int, float))
        assert income >= 0
        assert outcome >= 0