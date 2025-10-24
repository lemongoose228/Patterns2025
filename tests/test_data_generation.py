import unittest
import os
import json
import xml.etree.ElementTree as ET
from src.start_service import StartService
from src.logics.response_csv import ResponseCsv
from src.logics.response_markdown import ResponseMarkdown
from src.logics.response_json import ResponseJson
from src.logics.response_xml import ResponseXml

class TestDataGeneration(unittest.TestCase):

    def setUp(self):
        self.start_service = StartService()
        self.start_service.start()
        self.output_dir = "test_response_output"
        os.makedirs(self.output_dir, exist_ok=True)

    def test_generate_all_data_formats(self):
        # Получаем данные из сервиса
        data_sources = {
            "units_measure": list(self.start_service.units_measure.values()),
            "groups_nomenclature": list(self.start_service.groups_nomenclature.values()),
            "nomenclatures": list(self.start_service.nomenclatures.values()),
            "recipes": list(self.start_service.recipes.values())
        }

        # Форматы ответов
        formats = {
            "csv": ResponseCsv(),
            "markdown": ResponseMarkdown(),
            "json": ResponseJson(),
            "xml": ResponseXml()
        }

        # Генерируем файлы для каждого типа данных и каждого формата
        for data_name, data_list in data_sources.items():
            for format_name, formatter in formats.items():
                filename = f"{self.output_dir}/{data_name}.{format_name}"
                
                try:
                    result = formatter.build(format_name, data_list)
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(result)
                    
                    # Проверяем что файл создан и не пустой
                    self.assertTrue(os.path.exists(filename))
                    self.assertGreater(os.path.getsize(filename), 0)
                    
                    print(f"Создан файл: {filename}")
                    
                except Exception as e:
                    self.fail(f"Ошибка при создании файла {filename}: {e}")

    def tearDown(self):
        # Очистка тестовых файлов (опционально)
        pass