import os
from datetime import datetime
from src.core.observe_service import ObserveService
from src.core.event_type import EventType
from src.core.validator import Validator
from src.dtos.balance_cache_dto import BalanceCacheDto
from src.start_service import StartService
from src.models.transaction_model import TransactionModel
from src.models.storage_model import StorageModel
from src.logics.convert_factory import ConvertFactory
from src.core.prototype import Prototype
from src.dtos.filter_dto import FilterDto
from src.logics.response_json import ResponseJson
from src.core.common import common
from src.logics.logger_service import LoggerService


class BalanceService:
    """
    Сервис для расчета и сохранения остатков с оптимизацией через дату блокировки
    """

    def __init__(self, start_service, settings_manager):
        self.start_service = start_service
        self.settings_manager = settings_manager
        self.convert_factory = ConvertFactory()
        self.json_formatter = ResponseJson()
        self.balances_file = "balances_cache.json"
        ObserveService.add(self)

        LoggerService.log_info("Инициализирован BalanceService", "balance_service")

    def calculate_balances_until_date(self, target_date: datetime, storage: StorageModel = None):
        """
        Рассчитать остатки на указанную дату с использованием оптимизации через дату блокировки
        """
        Validator.validate(target_date, datetime)

        LoggerService.log_balance_calculation(target_date, storage.name if storage else "all")

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
                period_transactions = self._get_transactions_in_period_with_prototype(blocking_date, target_date,
                                                                                      storage)
                balances = self._apply_transactions_to_balances(balances, period_transactions)

                LoggerService.log_debug(
                    f"Использован кэш остатков на {blocking_date}. Рассчитаны остатки за период {blocking_date} - {target_date}",
                    "balance_service")
            else:
                # Если кэш не найден, рассчитываем полностью
                balances = self._calculate_full_balances_with_prototype(target_date, storage)
                LoggerService.log_debug(f"Полный расчет остатков до {target_date}", "balance_service")
        else:
            # Если блокировки нет или она позже целевой даты, рассчитываем полностью
            balances = self._calculate_full_balances_with_prototype(target_date, storage)
            LoggerService.log_debug(f"Полный расчет остатков до {target_date}", "balance_service")

        # Логируем количество рассчитанных остатков
        LoggerService.log_info(f"Рассчитаны остатки для {len(balances)} номенклатур на {target_date}",
                               "balance_service")
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

        LoggerService.log_debug(f"Отфильтровано {len(filtered_transactions)} транзакций до {target_date}",
                                "balance_service")

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

    def _get_transactions_in_period_with_prototype(self, start_date: datetime, end_date: datetime,
                                                   storage: StorageModel = None):
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

        LoggerService.log_debug(f"Получено {len(filtered_transactions)} транзакций за период {start_date} - {end_date}",
                                "balance_service")

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
            LoggerService.log_info("Дата блокировки не установлена, расчет не выполнен", "balance_service")
            return False

        LoggerService.log_info(f"Расчет оборотов до даты блокировки {blocking_date}", "balance_service")
        balances = self._calculate_full_balances_with_prototype(blocking_date)
        result = self._save_balances_to_cache(balances, blocking_date)

        if result:
            LoggerService.log_info(f"Обороты до {blocking_date} успешно сохранены в кэш", "balance_service")
        else:
            LoggerService.log_error(f"Ошибка сохранения оборотов до {blocking_date} в кэш", "balance_service")

        return result

    def _save_balances_to_cache(self, balances: dict, calculation_date: datetime):
        """
        Сохранить остатки в кэш с использованием единой сериализации
        """
        try:
            # Используем фабрику конверторов для сериализации
            cache_data = {
                "calculation_date": calculation_date.isoformat(),
                "balances": self._serialize_balances(balances)
            }

            # Используем JSON форматтер для сохранения
            json_data = self.json_formatter.build("json", [cache_data])

            with open(self.balances_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(json_data[0], f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            LoggerService.log_error(f"Ошибка сохранения кэша остатков: {str(e)}", "balance_service")
            return False

    def _serialize_balances(self, balances: dict) -> dict:
        """
        Сериализовать балансы с использованием DTO
        """
        serialized_balances = {}
        for nom_id, data in balances.items():
            # Создаем DTO для каждого баланса
            balance_dto = BalanceCacheDto()
            balance_dto.nomenclature_id = nom_id
            balance_dto.balance = data['balance']
            balance_dto.calculation_date = datetime.now()
            balance_dto.nomenclature_data = self.convert_factory.convert(data['nomenclature'])

            serialized_balances[nom_id] = balance_dto.to_dict()

        return serialized_balances

    def _load_cached_balances(self, target_date: datetime):
        """
        Загрузить остатки из кэша с использованием единой десериализации
        """
        try:
            if not os.path.exists(self.balances_file):
                LoggerService.log_debug(f"Файл кэша {self.balances_file} не найден", "balance_service")
                return None

            with open(self.balances_file, 'r', encoding='utf-8') as f:
                import json
                cache_data = json.load(f)

            # Проверяем, что кэш соответствует нужной дате
            cached_date = datetime.fromisoformat(cache_data["calculation_date"])
            if cached_date != target_date:
                LoggerService.log_debug(f"Кэш устарел: {cached_date} != {target_date}", "balance_service")
                return None

            # Восстанавливаем структуру balances с использованием универсального подхода
            balances = self._deserialize_balances(cache_data["balances"])
            LoggerService.log_debug(f"Загружен кэш остатков на {target_date} ({len(balances)} записей)",
                                    "balance_service")
            return balances

        except Exception as e:
            LoggerService.log_error(f"Ошибка загрузки кэша остатков: {str(e)}", "balance_service")
            return None

    def _deserialize_balances(self, serialized_balances: dict):
        """
        Десериализовать балансы с использованием DTO
        """
        balances = {}

        for nom_id, data in serialized_balances.items():
            # Создаем DTO из словаря
            balance_dto = BalanceCacheDto.from_dict(data)

            # Находим номенклатуру по ID
            nomenclature = self._find_nomenclature_by_id(balance_dto.nomenclature_id)

            if nomenclature:
                balances[nom_id] = {
                    'nomenclature': nomenclature,
                    'balance': balance_dto.balance
                }

        return balances

    def _find_nomenclature_by_id(self, nom_id: str):
        """
        Универсальный поиск номенклатуры по ID с использованием Prototype
        """
        filters = [
            FilterDto.from_dict({
                "field_name": "id",
                "value": nom_id,
                "type": "EQUALS"
            })
        ]

        all_nomenclatures = list(self.start_service.nomenclatures.values())
        filtered_nomenclatures = Prototype.filter(all_nomenclatures, filters)

        return filtered_nomenclatures[0] if filtered_nomenclatures else None

    def get_balance_report(self, target_date: datetime, storage: StorageModel = None):
        """
        Получить отчет по остаткам на указанную дату
        """
        balances = self.calculate_balances_until_date(target_date, storage)

        report_data = []
        for nom_id, data in balances.items():
            if data['balance'] != 0:  # Показываем только ненулевые остатки
                # Используем фабрику конверторов для сериализации
                nom_dict = self.convert_factory.convert(data['nomenclature'])
                unit_dict = self.convert_factory.convert(data['nomenclature'].unit_measurement)

                report_data.append({
                    "nomenclature_id": nom_id,
                    "nomenclature_name": nom_dict.get('name', ''),
                    "unit_measurement": unit_dict.get('name', ''),
                    "balance": round(data['balance'], 2),
                    "calculation_date": target_date.isoformat()
                })

        LoggerService.log_info(f"Сформирован отчет по остаткам на {target_date}: {len(report_data)} позиций",
                               "balance_service")
        return report_data

    def get_transactions_with_complex_filters(self, filters: list[FilterDto]):
        """
        Получить транзакции с комплексной фильтрацией через Prototype
        """
        all_transactions = list(self.start_service.transactions.values())
        filtered_transactions = Prototype.filter(all_transactions, filters)
        LoggerService.log_debug(f"Применены комплексные фильтры, результат: {len(filtered_transactions)} транзакций",
                                "balance_service")
        return filtered_transactions

    def handle(self, event: str, params):
        """
        Обработчик событий
        """
        if event == EventType.change_nomenclature_unit_key():
            LoggerService.log_info("Пересчет оборотов из-за изменения справочников", "balance_service")
            self.calculate_turnovers_until_blocking_date()