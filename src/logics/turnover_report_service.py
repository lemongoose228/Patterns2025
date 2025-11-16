from datetime import datetime
from src.logics.convert_factory import ConvertFactory
from src.core.validator import Validator, ArgumentException
from src.models.transaction_model import TransactionModel
from src.models.storage_model import StorageModel
from src.repository import Repository
from src.start_service import StartService

class TurnoverReportService:
    """
    Сервис для формирования оборотно-сальдовой ведомости
    """
    
    def __init__(self, start_service):
        self.start_service = start_service
        self.convert_factory = ConvertFactory()
    
    def generate_turnover_report(self, start_date: datetime, end_date: datetime, storage: StorageModel = None):
        """
        Сформировать оборотно-сальдовую ведомость
        
        Args:
            start_date (datetime): Дата начала периода
            end_date (datetime): Дата окончания периода
            storage (StorageModel): Склад (опционально)
            
        Returns:
            list: Список словарей с данными ОСВ
        """
        Validator.validate(start_date, datetime)
        Validator.validate(end_date, datetime)
        if storage:
            Validator.validate(storage, StorageModel)
        
        if start_date > end_date:
            raise ArgumentException("Дата начала не может быть позже даты окончания")
        
        # Получаем все транзакции
        all_transactions = list(self.start_service.transactions.values())
        
        # Получаем все номенклатуры для учета новых
        all_nomenclatures = list(self.start_service.nomenclatures.values())
        
        report_data = []
        
        for nomenclature in all_nomenclatures:
            # Начальный остаток (все транзакции до start_date)
            opening_balance = self._calculate_balance_for_nomenclature(
                nomenclature, all_transactions, None, start_date, storage
            )
            
            # Обороты за период
            income = self._calculate_turnover_for_nomenclature(
                nomenclature, all_transactions, start_date, end_date, storage, "in"
            )
            
            outcome = self._calculate_turnover_for_nomenclature(
                nomenclature, all_transactions, start_date, end_date, storage, "out"
            )
            
            # Конечный остаток
            closing_balance = opening_balance + income - outcome
            
            # Добавляем в отчет только если есть движение или остатки
            if opening_balance != 0 or income != 0 or outcome != 0 or closing_balance != 0:
                report_data.append({
                    "nomenclature_name": self.convert_factory.convert(nomenclature),
                    "unit_measurement": self.convert_factory.convert(nomenclature.unit_measurement),
                    "opening_balance": round(opening_balance, 2),
                    "income": round(income, 2),
                    "outcome": round(outcome, 2),
                    "closing_balance": round(closing_balance, 2)
                })
        
        return report_data
    
    def _calculate_balance_for_nomenclature(self, nomenclature, transactions, start_date, end_date, storage):
        """Рассчитать остаток для номенклатуры за период"""
        balance = 0
        
        for transaction in transactions:
            if transaction.nomenclature.id != nomenclature.id:
                continue
                
            if storage and transaction.storage.id != storage.id:
                continue
                
            if start_date and transaction.date < start_date:
                continue
                
            if end_date and transaction.date > end_date:
                continue
            
            quantity = transaction.get_quantity_in_base_units()
            if transaction.transaction_type == "in":
                balance += quantity
            else:
                balance -= quantity
        
        return balance
    
    def _calculate_turnover_for_nomenclature(self, nomenclature, transactions, start_date, end_date, storage, transaction_type):
        """Рассчитать оборот для номенклатуры за период"""
        turnover = 0
        
        for transaction in transactions:
            if transaction.nomenclature.id != nomenclature.id:
                continue
                
            if storage and transaction.storage.id != storage.id:
                continue
                
            if transaction.date < start_date or transaction.date > end_date:
                continue
                
            if transaction.transaction_type != transaction_type:
                continue
            
            quantity = transaction.get_quantity_in_base_units()
            turnover += quantity
        
        return turnover