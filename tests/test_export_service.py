import unittest
import json
import os
import tempfile
from src.logics.export_service import ExportService
from src.start_service import StartService
from src.core.validator import Validator, ArgumentException

class TestExportService(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных"""
        self.start_service = StartService()
        self.start_service.start()  # Инициализируем тестовые данные
        self.export_service = ExportService(self.start_service)

    def test_not_none_export_service_initialization(self):
        """Проверка инициализации сервиса экспорта"""
        # Действие
        service = ExportService(self.start_service)
        
        # Проверка
        assert service is not None
        assert service.start_service is not None
        assert service.convert_factory is not None

    def test_export_all_data_success(self):
        """Проверка успешного экспорта данных"""
        # Подготовка
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Действие
            result = self.export_service.export_all_data(temp_path)
            
            # Проверка
            assert result is True
            
            # Проверяем что файл создан и содержит данные
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
            
            # Проверяем структуру JSON
            with open(temp_path, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            assert "export_date" in exported_data
            assert "units_measure" in exported_data
            assert "groups_nomenclature" in exported_data
            assert "nomenclatures" in exported_data
            assert "storages" in exported_data
            assert "recipes" in exported_data
            assert "transactions" in exported_data
            
        finally:
            # Очистка
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_all_data_structure(self):
        """Проверка структуры экспортированных данных"""
        # Подготовка
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Действие
            self.export_service.export_all_data(temp_path)
            
            # Проверка структуры данных
            with open(temp_path, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            # Проверяем что все разделы являются списками
            assert isinstance(exported_data["units_measure"], list)
            assert isinstance(exported_data["groups_nomenclature"], list)
            assert isinstance(exported_data["nomenclatures"], list)
            assert isinstance(exported_data["storages"], list)
            assert isinstance(exported_data["recipes"], list)
            assert isinstance(exported_data["transactions"], list)
            
            # Проверяем что данные не пустые (если есть тестовые данные)
            if len(self.start_service.nomenclatures) > 0:
                assert len(exported_data["nomenclatures"]) > 0
            
        finally:
            # Очистка
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_all_data_invalid_path(self):
        """Проверка обработки невалидного пути"""
        # Подготовка
        invalid_path = ""  # Пустой путь
        
        # Действие и Проверка
        with self.assertRaises((ArgumentException, Exception)):
            self.export_service.export_all_data(invalid_path)

    def test_export_all_data_none_path(self):
        """Проверка обработки None пути"""
        # Действие и Проверка
        with self.assertRaises((ArgumentException, Exception)):
            self.export_service.export_all_data(None)

    def test_convert_entities_to_dict_method(self):
        """Проверка метода преобразования сущностей в словарь"""
        # Подготовка
        nomenclatures = list(self.start_service.nomenclatures.values())
        
        # Действие
        result = self.export_service._convert_entities_to_dict(nomenclatures)
        
        # Проверка
        assert result is not None
        assert isinstance(result, list)
        
        if len(nomenclatures) > 0:
            # Проверяем структуру преобразованных данных
            converted_item = result[0]
            assert isinstance(converted_item, dict)
            # Проверяем наличие основных полей
            assert "id" in converted_item
            assert "name" in converted_item

    def test_export_all_data_permission_error(self):
        """Проверка обработки ошибок прав доступа"""
        # Подготовка - пытаемся записать в системную директорию
        system_path = "/root/test_export.json"  # Обычно недоступно без прав root
        
        # Действие и Проверка
        with self.assertRaises(Exception):
            self.export_service.export_all_data(system_path)

    def test_export_service_with_empty_data(self):
        """Проверка экспорта при пустых данных"""
        # Подготовка
        start_service_empty = StartService()
        # Не вызываем start() чтобы данные остались пустыми
        start_service_empty.data["units_measure"] = {}
        start_service_empty.data["nomenclature"] = {}
        start_service_empty.data["transaction"] = {}
        
        export_service_empty = ExportService(start_service_empty)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Действие
            result = export_service_empty.export_all_data(temp_path)
            
            # Проверка
            assert result is True
            
            # Проверяем что файл создан
            with open(temp_path, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            # Проверяем что все разделы присутствуют, даже если пустые
            assert "units_measure" in exported_data
            assert "nomenclatures" in exported_data
            assert "transactions" in exported_data
            
            # Проверяем что пустые разделы - пустые списки
            assert exported_data["units_measure"] == []
            assert exported_data["nomenclatures"] == []
            assert exported_data["transactions"] == []
            
        finally:
            # Очистка
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_data_contains_valid_json(self):
        """Проверка что экспортированные данные являются валидным JSON"""
        # Подготовка
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Действие
            self.export_service.export_all_data(temp_path)
            
            # Проверка - пытаемся загрузить JSON
            with open(temp_path, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            assert True
            
        except json.JSONDecodeError:
            self.fail("Экспортированные данные не являются валидным JSON")
            
        finally:
            # Очистка
            if os.path.exists(temp_path):
                os.unlink(temp_path)