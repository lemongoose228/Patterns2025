import json
from datetime import datetime
from src.core.observe_service import ObserveService
from src.core.event_type import EventType
from src.core.validator import Validator
from src.start_service import StartService
from src.logics.convert_factory import ConvertFactory

class ExportService:
    """
    Сервис для экспорта данных в файл
    """
    
    def __init__(self, start_service):
        self.start_service = start_service
        self.convert_factory = ConvertFactory()
        ObserveService.add(self)
        
    
    def export_all_data(self, file_path: str):
        """
        Экспортировать все данные в JSON файл
        
        Args:
            file_path (str): Путь к файлу для сохранения
            
        Returns:
            bool: True если экспорт успешен
        """
        Validator.validate(file_path, str)
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "units_measure": self._convert_entities_to_dict(list(self.start_service.units_measure.values())),
            "groups_nomenclature": self._convert_entities_to_dict(list(self.start_service.groups_nomenclature.values())),
            "nomenclatures": self._convert_entities_to_dict(list(self.start_service.nomenclatures.values())),
            "storages": self._convert_entities_to_dict(list(self.start_service.storages.values())),
            "recipes": self._convert_entities_to_dict(list(self.start_service.recipes.values())),
            "transactions": self._convert_entities_to_dict(list(self.start_service.transactions.values()))
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            raise Exception(f"Ошибка при экспорте данных: {str(e)}")
    
    def _convert_entities_to_dict(self, entities):
        """Преобразовать список сущностей в словарь с использованием ConvertFactory"""
        result = []
        for entity in entities:
            # Используем ConvertFactory для преобразования объекта в словарь
            entity_dict = self.convert_factory.convert(entity)
            result.append(entity_dict)
        return result
    
    
    def handle(self, event: str, params):
        """
        Обработчик событий
        """
        if event == EventType.change_reference_type_key():
            # При изменении справочников автоматически обновляем data.json
            self.export_all_data("data/data.json")