from src.core.event_type import EventType
from src.core.observe_service import ObserveService
from src.core.prototype import Prototype
from src.dtos.filter_dto import FilterDto
from src.models.filter_type import FilterType
from src.core.validator import Validator, ArgumentException
from src.start_service import StartService

class ReferenceService:
    __start_service: StartService = None
    
    def __init__(self, start_service: StartService):
        Validator.validate(start_service, StartService)
        self.__start_service = start_service
    
    @property
    def start_service(self) -> StartService:
        return self.__start_service
    
    def get_reference_data(self, reference_type: str):
        """Получить данные справочника по типу"""
        Validator.validate(reference_type, str)
        
        data_map = {
            "nomenclatures": list(self.start_service.nomenclatures.values()),
            "units": list(self.start_service.units_measure.values()),
            "groups": list(self.start_service.groups_nomenclature.values()),
            "storages": list(self.start_service.storages.values())
        }
        
        if reference_type not in data_map:
            raise ArgumentException(f"Неизвестный тип справочника: {reference_type}")
        
        return data_map[reference_type]
    
    
    def get_reference_item(self, reference_type: str, item_id: str):
        """Получить один элемент справочника по ID"""
        Validator.validate(reference_type, str)
        Validator.validate(item_id, str)
        
        data = self.get_reference_data(reference_type)
        
        # Используем прототип для поиска по ID
        filters = [FilterDto()]
        filters[0].field_name = "id"
        filters[0].value = item_id
        filters[0].type = FilterType.EQUALS
        
        result = Prototype.filter(data, filters)
        
        if len(result) == 0:
            raise ArgumentException(f"Элемент с ID '{item_id}' не найден в справочнике '{reference_type}'")
        
        return result[0]
    
    
    def add_reference_item(self, reference_type: str, item_data: dict):
        """Добавить новый элемент в справочник"""
        Validator.validate(reference_type, str)
        Validator.validate(item_data, dict)
        
        if reference_type == "nomenclatures":
            item = self._add_nomenclature(item_data)
        elif reference_type == "units":
            item = self._add_unit_measurement(item_data)
        elif reference_type == "groups":
            item = self._add_group_nomenclature(item_data)
        elif reference_type == "storages":
            item = self._add_storage(item_data)
        else:
            raise ArgumentException(f"Неизвестный тип справочника: {reference_type}")
        
        ObserveService.create_event(EventType.change_reference_type_key(), None)
        return item

    def update_reference_item(self, reference_type: str, item_id: str, item_data: dict):
        """Обновить элемент справочника"""
        Validator.validate(reference_type, str)
        Validator.validate(item_id, str)
        Validator.validate(item_data, dict)
        
        # Находим существующий элемент
        existing_item = self.get_reference_item(reference_type, item_id)
        
        if reference_type == "nomenclatures":
            item = self._update_nomenclature(existing_item, item_data)
        elif reference_type == "units":
            item = self._update_unit_measurement(existing_item, item_data)
        elif reference_type == "groups":
            item = self._update_group_nomenclature(existing_item, item_data)
        elif reference_type == "storages":
            item = self._update_storage(existing_item, item_data)
        else:
            raise ArgumentException(f"Неизвестный тип справочника: {reference_type}")
        
        ObserveService.create_event(EventType.change_reference_type_key(), None)
        return item
    

    def delete_reference_item(self, reference_type: str, item_id: str):
        """Удалить элемент справочника"""
        Validator.validate(reference_type, str)
        Validator.validate(item_id, str)
        
        # Находим элемент
        item = self.get_reference_item(reference_type, item_id)
        
        if reference_type == "nomenclatures":
            self._delete_nomenclature(item)
        elif reference_type == "units":
            self._delete_unit_measurement(item)
        elif reference_type == "groups":
            self._delete_group_nomenclature(item)
        elif reference_type == "storages":
            self._delete_storage(item)
        else:
            raise ArgumentException(f"Неизвестный тип справочника: {reference_type}")
        
        ObserveService.create_event(EventType.change_reference_type_key(), None)

    
    # Методы для работы с номенклатурами
    def _add_nomenclature(self, item_data: dict):
        from src.models.nomenclature_model import NomenclatureModel
        
        Validator.validate(item_data.get('name'), str, name="name")
        Validator.validate(item_data.get('full_name'), str, name="full_name")
        
        # Поиск группы номенклатуры
        group_id = item_data.get('group_id')
        group = None
        if group_id:
            groups = list(self.start_service.groups_nomenclature.values())
            group = next((g for g in groups if g.id == group_id), None)
            if not group:
                raise ArgumentException(f"Группа номенклатуры с ID '{group_id}' не найдена")
        
        # Поиск единицы измерения
        unit_id = item_data.get('unit_id')
        unit = None
        if unit_id:
            units = list(self.start_service.units_measure.values())
            unit = next((u for u in units if u.id == unit_id), None)
            if not unit:
                raise ArgumentException(f"Единица измерения с ID '{unit_id}' не найдена")
        
        # Создание новой номенклатуры
        nomenclature = NomenclatureModel(
            name=item_data['name'],
            fullname=item_data['full_name'],
            group=group,
            unit=unit
        )
        
        # Добавление в хранилище
        key = f"nomenclature_{len(self.start_service.nomenclatures)}"
        self.start_service.nomenclatures[key] = nomenclature
        
        return nomenclature
    
    def _update_nomenclature(self, existing_item, item_data: dict):
        
        if 'name' in item_data:
            Validator.validate(item_data['name'], str, name="name")
            existing_item.name = item_data['name']
        
        if 'full_name' in item_data:
            Validator.validate(item_data['full_name'], str, name="full_name")
            existing_item.full_name = item_data['full_name']
        
        if 'group_id' in item_data:
            group_id = item_data['group_id']
            groups = list(self.start_service.groups_nomenclature.values())
            group = next((g for g in groups if g.id == group_id), None)
            if not group:
                raise ArgumentException(f"Группа номенклатуры с ID '{group_id}' не найдена")
            existing_item.group_nomenclature = group
        
        if 'unit_id' in item_data:
            unit_id = item_data['unit_id']
            units = list(self.start_service.units_measure.values())
            unit = next((u for u in units if u.id == unit_id), None)
            if not unit:
                raise ArgumentException(f"Единица измерения с ID '{unit_id}' не найдена")
            
            ObserveService.create_event(EventType.change_nomenclature_unit_key(), None)
            existing_item.unit_measurement = unit
        
        return existing_item
    
    def _delete_nomenclature(self, item):
        # Проверяем использование номенклатуры
        ObserveService.create_event(EventType.delete_nomenclature_key(), {"nomenclature": item})
        
        # Находим ключ в словаре
        for key, value in self.start_service.nomenclatures.items():
            if value == item:
                del self.start_service.nomenclatures[key]
                return True
        
        raise ArgumentException("Номенклатура не найдена в хранилище")
    
    # Методы для работы с единицами измерения
    def _add_unit_measurement(self, item_data: dict):
        from src.models.unit_measurement_model import UnitMeasurement
        
        Validator.validate(item_data.get('name'), str, name="name")
        Validator.validate(item_data.get('coefficient'), int, name="coefficient")
        
        # Поиск базовой единицы измерения
        base_unit_id = item_data.get('base_unit_id')
        base_unit = None
        if base_unit_id:
            units = list(self.start_service.units_measure.values())
            base_unit = next((u for u in units if u.id == base_unit_id), None)
            if not base_unit:
                raise ArgumentException(f"Базовая единица измерения с ID '{base_unit_id}' не найдена")
        
        # Создание новой единицы измерения
        unit = UnitMeasurement.create(
            name=item_data['name'],
            coefficient=item_data['coefficient'],
            base_unit=base_unit
        )
        
        # Добавление в хранилище
        key = f"unit_{len(self.start_service.units_measure)}"
        self.start_service.units_measure[key] = unit
        
        return unit
    
    def _update_unit_measurement(self, existing_item, item_data: dict):
        
        if 'name' in item_data:
            Validator.validate(item_data['name'], str, name="name")
            existing_item.name = item_data['name']
        
        if 'coefficient' in item_data:
            Validator.validate(item_data['coefficient'], int, name="coefficient")
            existing_item.coefficient = item_data['coefficient']
        
        if 'base_unit_id' in item_data:
            base_unit_id = item_data['base_unit_id']
            if base_unit_id is None:
                existing_item.base_unit = None
            else:
                units = list(self.start_service.units_measure.values())
                base_unit = next((u for u in units if u.id == base_unit_id), None)
                if not base_unit:
                    raise ArgumentException(f"Базовая единица измерения с ID '{base_unit_id}' не найдена")
                existing_item.base_unit = base_unit
        
        return existing_item
    
    def _delete_unit_measurement(self, item):
        # Проверяем использование единицы измерения
        ObserveService.create_event(EventType.delete_unit_key(), {"unit": item})
        
        # Находим ключ в словаре
        for key, value in self.start_service.units_measure.items():
            if value == item:
                del self.start_service.units_measure[key]
                return True
        
        raise ArgumentException("Единица измерения не найдена в хранилище")
    
    # Методы для работы с группами номенклатур
    def _add_group_nomenclature(self, item_data: dict):
        from src.models.group_nomenclature_model import GroupNomenclatureModel
        
        Validator.validate(item_data.get('name'), str, name="name")
        
        # Создание новой группы
        group = GroupNomenclatureModel()
        group.name = item_data['name']
        
        # Добавление в хранилище
        key = f"group_{len(self.start_service.groups_nomenclature)}"
        self.start_service.groups_nomenclature[key] = group
        
        return group
    
    def _update_group_nomenclature(self, existing_item, item_data: dict):
        if 'name' in item_data:
            Validator.validate(item_data['name'], str, name="name")
            existing_item.name = item_data['name']
        
        return existing_item
    
    def _delete_group_nomenclature(self, item):
        # Проверяем использование группы номенклатуры
        ObserveService.create_event(EventType.delete_group_nomenclature_key(), {"group": item})
        
        # Находим ключ в словаре
        for key, value in self.start_service.groups_nomenclature.items():
            if value == item:
                del self.start_service.groups_nomenclature[key]
                return True
        
        raise ArgumentException("Группа номенклатуры не найдена в хранилище")
    
    # Методы для работы со складами
    def _add_storage(self, item_data: dict):
        from src.models.storage_model import StorageModel
        
        Validator.validate(item_data.get('name'), str, name="name")
        
        # Создание нового склада
        storage = StorageModel(item_data['name'])
        
        # Добавление в хранилище
        key = f"storage_{len(self.start_service.storages)}"
        self.start_service.storages[key] = storage
        
        return storage
    
    def _update_storage(self, existing_item, item_data: dict):
        if 'name' in item_data:
            Validator.validate(item_data['name'], str, name="name")
            existing_item.name = item_data['name']
        
        return existing_item
    
    def _delete_storage(self, item):
        # Проверяем использование склада
        ObserveService.create_event(EventType.delete_storage_key(), {"storage": item})
        
        # Находим ключ в словаре
        for key, value in self.start_service.storages.items():
            if value == item:
                del self.start_service.storages[key]
                return True
        
        raise ArgumentException("Склад не найден в хранилище")
