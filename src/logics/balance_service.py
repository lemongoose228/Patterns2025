import json
import os
from datetime import datetime
from src.core.validator import Validator
from src.start_service import StartService
from src.models.transaction_model import TransactionModel
from src.models.nomenclature_model import NomenclatureModel
from src.models.storage_model import StorageModel
from src.logics.convert_factory import ConvertFactory
from src.core.prototype import Prototype
from src.dtos.filter_dto import FilterDto

class BalanceService:
    """
    Сервис для расчета и сохранения остатков с оптимизацией через дату блокировки
    """
    
    def __init__(self, start_service, settings_manager):
        self.start_service = start_service
        self.settings_manager = settings_manager
        self.convert_factory = ConvertFactory()
        self.balances_file = "balances_cache.json"
    
    def calculate_balances_until_date(self, target_date: datetime, storage: StorageModel = None):
        """
        Рассчитать остатки на указанную дату с использованием оптимизации через дату блокировки
        """
        Validator.validate(target_date, datetime)
        
        blocking_date = self.settings_manager.settings.blocking_date
        balances = {}
        
        # Если есть дата блокировки и она раньше целевой даты
        if blocking_date and blocking_date < target_date:
            # Загружаем сохраненные остатки на дату блокировки
            cached_balances = self._load_cached_balances(blocking_date)
            
            if cached_balances:
                # Используем кэшированные остатки как начальные
                balances = cached_balances
                
                # Рассчитываем обороты только за период от блокировки до целевой даты
                period_transactions = self._get_transactions_in_period_with_prototype(blocking_date, target_date, storage)
                balances = self._apply_transactions_to_balances(balances, period_transactions)
            else:
                # Если кэш не найден, рассчитываем полностью
                balances = self._calculate_full_balances_with_prototype(target_date, storage)
        else:
            # Если блокировки нет или она позже целевой даты, рассчитываем полностью
            balances = self._calculate_full_balances_with_prototype(target_date, storage)
        
        return balances
    
    def _calculate_full_balances_with_prototype(self, target_date: datetime, storage: StorageModel = None):
        """
        Полный расчет остатков с начала времен до целевой даты с использованием Prototype
        """
        balances = {}
        
        # Получаем все транзакции до целевой даты
        filters = [
            FilterDto.from_dict({
                "field_name": "date",
                "value": target_date.isoformat(),
                "type": "LESS_EQUAL"
            })
        ]
        
        # Добавляем фильтр по складу если указан
        if storage:
            filters.append(FilterDto.from_dict({
                "field_name": "storage/id",
                "value": storage.id,
                "type": "EQUALS"
            }))
        
        # Применяем фильтры через Prototype
        all_transactions = list(self.start_service.transactions.values())
        filtered_transactions = Prototype.filter(all_transactions, filters)
        
        # Обрабатываем отфильтрованные транзакции
        for transaction in filtered_transactions:
            nom_id = transaction.nomenclature.id
            quantity = transaction.get_quantity_in_base_units()
            
            if nom_id not in balances:
                balances[nom_id] = {
                    'nomenclature': transaction.nomenclature,
                    'balance': 0
                }
            
            if transaction.transaction_type == "in":
                balances[nom_id]['balance'] += quantity
            else:
                balances[nom_id]['balance'] -= quantity
        
        return balances
    
    def _get_transactions_in_period_with_prototype(self, start_date: datetime, end_date: datetime, storage: StorageModel = None):
        """
        Получить транзакции за указанный период с использованием Prototype
        """
        filters = [
            FilterDto.from_dict({
                "field_name": "date",
                "value": start_date.isoformat(),
                "type": "GREATER_EQUAL"
            }),
            FilterDto.from_dict({
                "field_name": "date",
                "value": end_date.isoformat(),
                "type": "LESS_EQUAL"
            })
        ]
        
        # Добавляем фильтр по складу если указан
        if storage:
            filters.append(FilterDto.from_dict({
                "field_name": "storage/id",
                "value": storage.id,
                "type": "EQUALS"
            }))
        
        # Применяем фильтры через Prototype
        all_transactions = list(self.start_service.transactions.values())
        filtered_transactions = Prototype.filter(all_transactions, filters)
        
        return filtered_transactions
    
    def _apply_transactions_to_balances(self, balances: dict, transactions: list):
        """
        Применить транзакции к существующим остаткам
        """
        for transaction in transactions:
            nom_id = transaction.nomenclature.id
            quantity = transaction.get_quantity_in_base_units()
            
            if nom_id not in balances:
                balances[nom_id] = {
                    'nomenclature': transaction.nomenclature,
                    'balance': 0
                }
            
            if transaction.transaction_type == "in":
                balances[nom_id]['balance'] += quantity
            else:
                balances[nom_id]['balance'] -= quantity
        
        return balances
    
    def calculate_turnovers_until_blocking_date(self):
        """
        Рассчитать и сохранить обороты до даты блокировки с использованием Prototype
        """
        blocking_date = self.settings_manager.settings.blocking_date
        if not blocking_date:
            return False
        
        balances = self._calculate_full_balances_with_prototype(blocking_date)
        return self._save_balances_to_cache(balances, blocking_date)
    
    def _save_balances_to_cache(self, balances: dict, calculation_date: datetime):
        """
        Сохранить остатки в кэш
        """
        try:
            cache_data = {
                "calculation_date": calculation_date.isoformat(),
                "balances": {}
            }
            
            for nom_id, data in balances.items():
                cache_data["balances"][nom_id] = {
                    "nomenclature_id": nom_id,
                    "balance": data['balance'],
                    "calculation_date": calculation_date.isoformat()
                }
            
            with open(self.balances_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Ошибка сохранения кэша остатков: {e}")
            return False
    
    def _load_cached_balances(self, target_date: datetime):
        """
        Загрузить остатки из кэша
        """
        try:
            if not os.path.exists(self.balances_file):
                return None
            
            with open(self.balances_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Проверяем, что кэш соответствует нужной дате
            cached_date = datetime.fromisoformat(cache_data["calculation_date"])
            if cached_date != target_date:
                return None
            
            # Восстанавливаем структуру balances
            balances = {}
            for nom_id, data in cache_data["balances"].items():
                # Находим номенклатуру по ID
                nomenclature = None
                for nom in self.start_service.nomenclatures.values():
                    if nom.id == nom_id:
                        nomenclature = nom
                        break
                
                if nomenclature:
                    balances[nom_id] = {
                        'nomenclature': nomenclature,
                        'balance': data['balance']
                    }
            
            return balances
            
        except Exception as e:
            print(f"Ошибка загрузки кэша остатков: {e}")
            return None
    
    def get_balance_report(self, target_date: datetime, storage: StorageModel = None):
        """
        Получить отчет по остаткам на указанную дату
        """
        balances = self.calculate_balances_until_date(target_date, storage)
        
        report_data = []
        for nom_id, data in balances.items():
            if data['balance'] != 0:  # Показываем только ненулевые остатки
                report_data.append({
                    "nomenclature_id": nom_id,
                    "nomenclature_name": self.convert_factory.convert(data['nomenclature']),
                    "unit_measurement": self.convert_factory.convert(data['nomenclature'].unit_measurement),
                    "balance": round(data['balance'], 2),
                    "calculation_date": target_date.isoformat()
                })
        
        return report_data
    
    def get_transactions_with_complex_filters(self, filters: list[FilterDto]):
        """
        Получить транзакции с комплексной фильтрацией через Prototype
        """
        all_transactions = list(self.start_service.transactions.values())
        return Prototype.filter(all_transactions, filters)