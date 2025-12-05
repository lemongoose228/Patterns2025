import unittest
import os
import tempfile
import json
from unittest.mock import patch

from src.logics.logger_service import LoggerService
from src.core.observe_service import ObserveService


class TestLogging(unittest.TestCase):
    """Тесты для быстрой проверки логирования"""

    def test_basic_logging(self):
        """Проверим базовое логирование в консоль"""
        # Создаем логгер
        logger = LoggerService()

        # Тестируем логирование с моком
        with patch.object(logger, '_log_to_console') as mock_log:
            logger.log("INFO", "Тестовое сообщение", "test")

            # Проверяем, что метод был вызван
            mock_log.assert_called_once()

            # Проверяем аргументы
            args, kwargs = mock_log.call_args
            self.assertIn("[INFO]", args[0], "Сообщение должно содержать уровень INFO")
            self.assertIn("Тестовое сообщение", args[0], "Сообщение должно содержать текст")


    def test_static_methods(self):
        """Проверим статические методы логирования"""
        with patch.object(ObserveService, 'create_event') as mock_create_event:
            # Тестируем логирование API
            LoggerService.log_api_call("POST", "/api/test", 201)

            # Проверяем вызов
            self.assertTrue(mock_create_event.called, "ObserveService.create_event должен быть вызван")


    def test_error_logging_static(self):
        """Проверим статическое логирование ошибок"""
        with patch.object(ObserveService, 'create_event') as mock_create_event:
            LoggerService.log_error("Тестовая ошибка", "test_module")

            # Проверяем параметры
            args, kwargs = mock_create_event.call_args
            self.assertIsNotNone(args, "Аргументы должны быть переданы")
            self.assertEqual(len(args), 2, "Должно быть 2 аргумента")


    def test_info_logging_static(self):
        """Проверим статическое логирование информации"""
        with patch.object(ObserveService, 'create_event') as mock_create_event:
            LoggerService.log_info("Тестовая информация", "test_module")

            # Проверяем, что метод был вызван
            self.assertTrue(mock_create_event.called, "Метод должен быть вызван")

    def test_not_none_logger(self):
        """Проверим, что логгер не None"""
        logger = LoggerService()
        self.assertIsNotNone(logger, "Логгер не должен быть None")


    def test_debug_logging_static(self):
        """Проверим статическое логирование отладки"""
        with patch.object(ObserveService, 'create_event') as mock_create_event:
            LoggerService.log_debug("Тестовая отладка", "test_module")

            # Проверяем вызов
            mock_create_event.assert_called_once()

    def test_reference_logging(self):
        """Проверим логирование операций со справочниками"""
        with patch.object(ObserveService, 'create_event') as mock_create_event:
            LoggerService.log_reference_operation('add', 'nomenclatures', 'item_123', {'name': 'test'})

            # Проверяем вызов
            self.assertTrue(mock_create_event.called)


    def test_settings_logging(self):
        """Проверим логирование изменения настроек"""
        with patch.object(ObserveService, 'create_event') as mock_create_event:
            LoggerService.log_settings_change('log_level', 'INFO', 'DEBUG')

            # Проверяем вызов
            mock_create_event.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)