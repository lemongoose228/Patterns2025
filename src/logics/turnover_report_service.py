from datetime import datetime
from src.logics.convert_factory import ConvertFactory
from src.core.validator import Validator, ArgumentException
from src.models.transaction_model import TransactionModel
from src.models.storage_model import StorageModel
from src.repository import Repository
from src.start_service import StartService
from src.core.prototype import Prototype
from src.dtos.filter_dto import FilterDto

class TurnoverReportService:
    """
    Сервис для формирования оборотно-сальдовой ведомости
    """
    
    def __init__(self, start_service):
        self.start_service = start_service
        self.convert_factory = ConvertFactory()
    
    def generate_turnover_report(self, start_date: datetime, end_date: datetime, storage: StorageModel = None, filters: list[FilterDto] = None):
        """
        Сформировать оборотно-сальдовую ведомость с использованием прототипа
        
        Args:
            start_date (datetime): Дата начала периода
            end_date (datetime): Дата окончания периода
            storage (StorageModel): Склад (опционально)
            filters (list[FilterDto]): Фильтры для транзакций (опционально)
            
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
        
        # Создаем прототип для транзакций
        transaction_prototype = Prototype(all_transactions)
        
        # Применяем базовые фильтры по дате и складу
        filtered_transactions = self._apply_base_filters(transaction_prototype, start_date, end_date, storage)
        
        # Применяем пользовательские фильтры если есть
        if filters:
            filtered_transactions = Prototype.filter(filtered_transactions, filters)
        else:
            filtered_transactions = filtered_transactions
        
        # Формируем ОСВ на основе отфильтрованных транзакций
        report_data = self._build_turnover_report_from_transactions(filtered_transactions, start_date)
        
        return report_data
    
    def _apply_base_filters(self, prototype: Prototype, start_date: datetime, end_date: datetime, storage: StorageModel = None):
        """Применить базовые фильтры по дате и складу через прототип"""
        filters = []
        
        # Фильтр по дате (транзакции внутри периода)
        filters.append(FilterDto.from_dict({
            "field_name": "date",
            "value": start_date.isoformat(),
            "type": "GREATER_EQUAL"
        }))
        
        filters.append(FilterDto.from_dict({
            "field_name": "date", 
            "value": end_date.isoformat(),
            "type": "LESS_EQUAL"
        }))
        
        # Фильтр по складу если указан
        if storage:
            filters.append(FilterDto.from_dict({
                "field_name": "storage/id",
                "value": storage.id,
                "type": "EQUALS"
            }))
        
        # Возвращаем отфильтрованный список, а не объект Prototype
        return Prototype.filter(prototype.data, filters)
    
    def _build_turnover_report_from_transactions(self, transactions: list, start_date: datetime):
        """Построить ОСВ на основе отфильтрованных транзакций"""
        # Группируем транзакции по номенклатуре
        nomenclature_data = {}
        
        for transaction in transactions:
            nom_id = transaction.nomenclature.id
            if nom_id not in nomenclature_data:
                nomenclature_data[nom_id] = {
                    'nomenclature': transaction.nomenclature,
                    'transactions': []
                }
            nomenclature_data[nom_id]['transactions'].append(transaction)
        
        # Рассчитываем показатели для каждой номенклатуры
        report_data = []
        
        for nom_id, data in nomenclature_data.items():
            nomenclature = data['nomenclature']
            nom_transactions = data['transactions']
            
            # Начальный остаток (транзакции до start_date)
            opening_balance = self._calculate_opening_balance(nomenclature, start_date)
            
            # Обороты за период
            income = sum(
                t.get_quantity_in_base_units() 
                for t in nom_transactions 
                if t.transaction_type == "in"
            )
            
            outcome = sum(
                t.get_quantity_in_base_units() 
                for t in nom_transactions 
                if t.transaction_type == "out"
            )
            
            # Конечный остаток
            closing_balance = opening_balance + income - outcome
            
            report_data.append({
                "nomenclature_id": nomenclature.id,
                "nomenclature_name": self.convert_factory.convert(nomenclature),
                "unit_measurement": self.convert_factory.convert(nomenclature.unit_measurement),
                "opening_balance": round(opening_balance, 2),
                "income": round(income, 2),
                "outcome": round(outcome, 2),
                "closing_balance": round(closing_balance, 2),
                "transaction_count": len(nom_transactions)
            })
        
        return report_data
    
    def _calculate_opening_balance(self, nomenclature, start_date: datetime):
        """Рассчитать начальный остаток до указанной даты"""
        all_transactions = list(self.start_service.transactions.values())
        
        balance = 0
        for transaction in all_transactions:
            if (transaction.nomenclature.id == nomenclature.id and 
                transaction.date < start_date):
                
                quantity = transaction.get_quantity_in_base_units()
                if transaction.transaction_type == "in":
                    balance += quantity
                else:
                    balance -= quantity
        
        return balance
    
    # Старый метод для обратной совместимости
    def generate_turnover_report_old(self, start_date: datetime, end_date: datetime, storage: StorageModel = None):
        """
        Старая версия метода для обратной совместимости
        """
        # Используем старую логику без прототипа
        Validator.validate(start_date, datetime)
        Validator.validate(end_date, datetime)
        if storage:
            Validator.validate(storage, StorageModel)
        
        if start_date > end_date:
            raise ArgumentException("Дата начала не может быть позже даты окончания")
        
        # Получаем все номенклатуры для учета новых
        all_nomenclatures = list(self.start_service.nomenclatures.values())
        
        # Получаем все транзакции
        all_transactions = list(self.start_service.transactions.values())
        
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