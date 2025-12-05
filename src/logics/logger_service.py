import os
from datetime import datetime
from src.core.observe_service import ObserveService
from src.core.event_type import EventType
from src.settings_manager import SettingsManager
from src.core.validator import Validator
import json
from threading import Lock


class LoggerService:
    """
    Сервис логирования на основе шаблона "Наблюдатель"
    """

    __instance = None
    __lock = Lock()

    # Уровни логирования
    LEVELS = {
        'DEBUG': 10,
        'INFO': 20,
        'ERROR': 30
    }

    def __new__(cls):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super(LoggerService, cls).__new__(cls)
                cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return

        self.__settings_manager = None
        self.__current_log_file = None
        self.__log_buffer = []
        self.__buffer_size = 10
        self.__initialized = True
        ObserveService.add(self)

    def set_settings_manager(self, settings_manager: SettingsManager):
        """Установить менеджер настроек для логгера"""
        Validator.validate(settings_manager, SettingsManager)
        self.__settings_manager = settings_manager

    @property
    def settings(self):
        """Получить текущие настройки"""
        if self.__settings_manager:
            return self.__settings_manager.settings
        return None

    def handle(self, event: str, params):
        """Обработчик событий логирования"""
        if event.startswith("log_"):
            level = event[4:].upper().split('_')[0]  # Извлекаем уровень из события

            if level not in ['DEBUG', 'INFO', 'ERROR', 'REFERENCE', 'BALANCE', 'REPORT', 'STORAGE', 'API',
                             'SETTINGS']:
                level = 'INFO'  # По умолчанию

            # Преобразуем кастомные события в стандартные уровни
            level_mapping = {
                'REFERENCE': 'INFO',
                'BALANCE': 'INFO',
                'REPORT': 'INFO',
                'STORAGE': 'INFO',
                'API': 'INFO',
                'SETTINGS': 'INFO'
            }

            actual_level = level_mapping.get(level, level)

            # Формируем сообщение
            message = self._format_message(event, params)
            self.log(actual_level, message, params.get('module', 'unknown'))


    def _format_message(self, event: str, params: dict) -> str:
        """Форматирование сообщения для лога"""
        if params and 'message' in params:
            return params['message']

        # Форматирование по типу события
        event_formatters = {
            EventType.log_reference_add_key(): lambda
                p: f"Добавлен элемент справочника '{p.get('reference_type', 'unknown')}': {p.get('item_data', {})}",
            EventType.log_reference_update_key(): lambda
                p: f"Обновлен элемент справочника '{p.get('reference_type', 'unknown')}' (ID: {p.get('item_id', 'unknown')}): {p.get('item_data', {})}",
            EventType.log_reference_delete_key(): lambda
                p: f"Удален элемент справочника '{p.get('reference_type', 'unknown')}' (ID: {p.get('item_id', 'unknown')})",
            EventType.log_balance_calculation_key(): lambda
                p: f"Расчет остатков на дату: {p.get('date', 'unknown')}, склад: {p.get('storage', 'all')}",
            EventType.log_report_generation_key(): lambda
                p: f"Сформирован отчет ОСВ с {p.get('start_date', 'unknown')} по {p.get('end_date', 'unknown')}",
            EventType.log_storage_operation_key(): lambda
                p: f"Складская операция: {p.get('operation', 'unknown')}, номенклатура: {p.get('nomenclature', 'unknown')}, количество: {p.get('quantity', 0)}",
            EventType.log_api_call_key(): lambda
                p: f"API вызов: {p.get('method', 'unknown')} {p.get('endpoint', 'unknown')}, статус: {p.get('status', 'unknown')}",
            EventType.log_settings_change_key(): lambda
                p: f"Изменение настроек: {p.get('setting', 'unknown')} = {p.get('value', 'unknown')}",
            EventType.log_error_key(): lambda p: f"Ошибка: {p.get('error', 'unknown')}",
            EventType.log_info_key(): lambda p: f"Информация: {p.get('info', 'unknown')}",
            EventType.log_debug_key(): lambda p: f"Отладка: {p.get('debug', 'unknown')}"
        }

        formatter = event_formatters.get(event, lambda p: str(p) if p else event)
        return formatter(params) if params else event

    def log(self, level: str, message: str, module: str = "system"):
        """
        Основной метод логирования
        """
        if not self.settings:
            # Если нет настроек, пишем в консоль
            self._log_to_console(level, message, module)
            return

        # Проверяем уровень логирования
        current_level = self.settings.log_level.upper()
        if self.LEVELS.get(level.upper(), 0) < self.LEVELS.get(current_level, 0):
            return

        # Форматируем сообщение
        formatted_message = self._format_log_message(level, message, module)

        # Логируем в зависимости от режима
        if self.settings.log_mode.upper() == "FILE":
            self._log_to_file(formatted_message)
        else:
            self._log_to_console(formatted_message)

    def _format_log_message(self, level: str, message: str, module: str) -> str:
        """Форматирование сообщения по шаблону"""
        timestamp = datetime.now().strftime(self.settings.log_date_format)

        # Заменяем плейсхолдеры в формате
        log_message = self.settings.log_format
        log_message = log_message.replace('{level}', level.upper())
        log_message = log_message.replace('{timestamp}', timestamp)
        log_message = log_message.replace('{module}', module)
        log_message = log_message.replace('{message}', message)

        return log_message

    def _log_to_console(self, formatted_message: str):
        """Логирование в консоль"""
        print(formatted_message) 

    def _log_to_file(self, formatted_message: str):
        """Логирование в файл (с созданием файла на каждый день)"""
        try:
            # Проверяем и создаем директорию если нужно
            log_dir = self.settings.log_directory
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Формируем имя файла на основе текущей даты
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(log_dir, f"app_{today}.log")

            # Проверяем, нужно ли создать новый файл
            if self.__current_log_file != log_file:
                self.__current_log_file = log_file
                self.__flush_buffer()  # Сбрасываем буфер при смене файла

            # Добавляем в буфер и сбрасываем если нужно
            self.__log_buffer.append(formatted_message)
            if len(self.__log_buffer) >= self.__buffer_size:
                self.__flush_buffer()

        except Exception as e:
            # Если не удалось записать в файл, пишем в консоль
            self._log_to_console(formatted_message)

    def __flush_buffer(self):
        """Сброс буфера в файл"""
        if not self.__current_log_file or not self.__log_buffer:
            return

        with open(self.__current_log_file, 'a', encoding='utf-8') as f:
            for message in self.__log_buffer:
                f.write(message + '\n')
        self.__log_buffer.clear()

    def flush(self):
        """Принудительный сброс буфера"""
        self.__flush_buffer()

    # Вспомогательные методы для разных типов логирования

    @staticmethod
    def log_reference_operation(operation: str, reference_type: str, item_id: str = None, item_data: dict = None):
        """Логирование операций со справочниками"""
        params = {
            'reference_type': reference_type,
            'item_id': item_id,
            'item_data': item_data,
            'operation': operation,
            'module': 'reference_service'
        }

        if operation == 'add':
            ObserveService.create_event(EventType.log_reference_add_key(), params)
        elif operation == 'update':
            ObserveService.create_event(EventType.log_reference_update_key(), params)
        elif operation == 'delete':
            ObserveService.create_event(EventType.log_reference_delete_key(), params)

    @staticmethod
    def log_balance_calculation(date: datetime, storage: str = None):
        """Логирование расчета остатков"""
        ObserveService.create_event(EventType.log_balance_calculation_key(), {
            'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
            'storage': storage,
            'module': 'balance_service'
        })

    @staticmethod
    def log_report_generation(report_type: str, start_date: datetime, end_date: datetime):
        """Логирование формирования отчетов"""
        ObserveService.create_event(EventType.log_report_generation_key(), {
            'report_type': report_type,
            'start_date': start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date),
            'end_date': end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date),
            'module': 'turnover_report_service'
        })

    @staticmethod
    def log_storage_operation(operation: str, nomenclature: str, quantity: float):
        """Логирование складских операций"""
        ObserveService.create_event(EventType.log_storage_operation_key(), {
            'operation': operation,
            'nomenclature': nomenclature,
            'quantity': quantity,
            'module': 'storage'
        })

    @staticmethod
    def log_api_call(method: str, endpoint: str, status: int, request_data: dict = None):
        """Логирование вызовов API"""
        params = {
            'method': method,
            'endpoint': endpoint,
            'status': status,
            'module': 'api'
        }

        # Для изменяющих операций добавляем данные запроса
        if method in ['DELETE', 'PUT', 'PATCH'] and request_data:
            params['request_data'] = request_data

        ObserveService.create_event(EventType.log_api_call_key(), params)

    @staticmethod
    def log_settings_change(setting: str, old_value, new_value):
        """Логирование изменения настроек"""
        ObserveService.create_event(EventType.log_settings_change_key(), {
            'setting': setting,
            'old_value': old_value,
            'new_value': new_value,
            'module': 'settings_manager'
        })

    @staticmethod
    def log_error(error_message: str, module: str = "system", exception: Exception = None):
        """Логирование ошибок"""
        params = {
            'error': error_message,
            'module': module
        }

        if exception:
            params['exception'] = str(exception)

        ObserveService.create_event(EventType.log_error_key(), params)

    @staticmethod
    def log_info(info_message: str, module: str = "system"):
        """Логирование информационных сообщений"""
        ObserveService.create_event(EventType.log_info_key(), {
            'info': info_message,
            'module': module
        })

    @staticmethod
    def log_debug(debug_message: str, module: str = "system", data: dict = None):
        """Логирование отладочных сообщений"""
        params = {
            'debug': debug_message,
            'module': module
        }

        if data:
            params['data'] = data

        ObserveService.create_event(EventType.log_debug_key(), params)