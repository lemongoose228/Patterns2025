import unittest

from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.models.nomenclature_model import NomenclatureModel
from src.models.recipe_model import RecipeModel
from src.models.unit_measurement_model import UnitMeasurement
from src.repository import Repository
from src.start_service import StartService


class TestStartService(unittest.TestCase):
    __start_service: StartService = StartService()
    
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.__start_service.start()

    def test_create_start_service_singleton_instance_created(self):
        # Подготовка & Действие
        service1 = StartService()
        service2 = StartService()

        # Проверка
        assert service1 is service2
        assert isinstance(service1, StartService)

    def test_start_service_initialization_empty_collections_created(self):
        # Подготовка
        service = StartService()

        # Действие
        # (инициализация уже выполнена)

        # Проверка
        assert hasattr(service, 'units_measure')
        assert hasattr(service, 'groups_nomenclature')
        assert hasattr(service, 'nomenclatures')
        assert hasattr(service, 'recipes')
        assert isinstance(service.units_measure, dict)
        assert isinstance(service.groups_nomenclature, dict)
        assert isinstance(service.nomenclatures, dict)
        assert isinstance(service.recipes, dict)

    def test_start_service_start_unit_not_empty(self):
        # Подготовка
        # Действие (уже выполнено в __init__)

        # Проверка
        assert len(self.__start_service.data[Repository.unit_measure_key]) > 0

    def test_start_service_eq_units(self):
        # Подготовка
        gram = self.__start_service.data[Repository.unit_measure_key]["gramm"]
        kilo = self.__start_service.data[Repository.unit_measure_key]["kg"]
        
        # Действие
        # (данные уже загружены)

        # Проверка
        assert kilo.base_unit.id == gram.id

    def test_full_start_process_all_collections_populated(self):
        # Подготовка
        service = StartService()

        # Действие
        service.start()

        # Проверка
        # Проверяем что коллекции не пустые
        assert len(service.units_measure) > 0
        assert len(service.groups_nomenclature) > 0
        assert len(service.nomenclatures) > 0
        assert len(service.recipes) > 0

        # Проверяем конкретные ожидаемые элементы
        assert "gramm" in service.units_measure
        assert "kg" in service.units_measure
        assert "ingredients" in service.groups_nomenclature
        assert "cookies" in service.recipes

    def test_units_measure_relationship_base_unit_set_correctly(self):
        # Подготовка
        service = StartService()

        # Действие
        service.start()

        # Проверка
        gramm = service.units_measure["gramm"]
        kg = service.units_measure["kg"]
        
        assert kg.base_unit == gramm
        assert gramm.base_unit is None
        assert kg.coefficient == 1000
        assert gramm.coefficient == 1

    def test_nomenclature_has_correct_group_and_unit(self):
        # Подготовка
        service = StartService()

        # Действие
        service.start()

        # Проверка
        wheat_flour = service.nomenclatures["wheat_flour"]
        ingredients_group = service.groups_nomenclature["ingredients"]
        gramm_unit = service.units_measure["gramm"]
        
        assert wheat_flour.group_nomenclature == ingredients_group
        assert wheat_flour.unit_measurement == gramm_unit
        assert isinstance(wheat_flour, NomenclatureModel)
        assert wheat_flour.name == "wheat flour"

    def test_default_create_units_measure_gramm_and_kg_created(self):
        # Подготовка

        # # Действие

        # Проверка
        assert "gramm" in self.__start_service.units_measure
        assert "kg" in self.__start_service.units_measure
        assert isinstance(self.__start_service.units_measure["gramm"], UnitMeasurement)
        assert isinstance(self.__start_service.units_measure["kg"], UnitMeasurement)
        assert self.__start_service.units_measure["gramm"].name == "грамм"
        assert self.__start_service.units_measure["kg"].name == "кг"

    def test_default_create_group_nomenclature_ingredients_group_created(self):
        # Подготовка

        # Действие

        # Проверка
        assert "ingredients" in self.__start_service.groups_nomenclature
        assert isinstance(self.__start_service.groups_nomenclature["ingredients"], GroupNomenclatureModel)

    def test_default_create_nomenclature_all_ingredients_created(self):
        # Подготовка

        # Действие

        # Проверка
        expected_ingredients = [
            "wheat_flour", "oatmeal", "sugar", "butter", 
            "chicken_egg", "dark_chocolate", "baking_powder", "salt"
        ]
        
        for ingredient in expected_ingredients:
            assert ingredient in self.__start_service.nomenclatures
            assert isinstance(self.__start_service.nomenclatures[ingredient], NomenclatureModel)

        # Проверяем конкретные поля
        assert self.__start_service.nomenclatures["wheat_flour"].name == "wheat flour"
        assert self.__start_service.nomenclatures["sugar"].full_name == "granulated sugar"

    def test_create_cookies_recipe_invalid_ingredient_type_throws_exception(self):
        # Подготовка
        service = StartService()
        service.start()

        # Действие & Проверка
        with self.assertRaises(Exception):
            service.create_cookies_recipe(
                "invalid_ingredient",  # Неправильный тип
                service.nomenclatures["oatmeal"],
                service.nomenclatures["sugar"],
                service.nomenclatures["butter"],
                service.nomenclatures["chicken_egg"],
                service.nomenclatures["dark_chocolate"],
                service.nomenclatures["baking_powder"],
                service.nomenclatures["salt"],
            )

    def test_data_property_returns_repository_data(self):
        # Подготовка
        service = StartService()
        service.start()

        # Действие
        result = service.data

        # Проверка
        assert result is not None
        assert isinstance(result, dict)

    def test_nomenclatures_property_returns_correct_data(self):
        # Подготовка
        service = StartService()
        service.start()

        # Действие
        result = service.nomenclatures

        # Проверка
        assert result is not None
        assert isinstance(result, dict)
        assert "wheat_flour" in result

    def test_units_measure_property_returns_correct_data(self):
        # Подготовка
        service = StartService()
        service.start()

        # Действие
        result = service.units_measure

        # Проверка
        assert result is not None
        assert isinstance(result, dict)
        assert "gramm" in result
        assert "kg" in result

    def test_groups_nomenclature_property_returns_correct_data(self):
        # Подготовка
        service = StartService()
        service.start()

        # Действие
        result = service.groups_nomenclature

        # Проверка
        assert result is not None
        assert isinstance(result, dict)
        assert "ingredients" in result

    def test_recipes_property_returns_correct_data(self):
        # Подготовка
        service = StartService()
        service.start()

        # Действие
        result = service.recipes

        # Проверка
        assert result is not None
        assert isinstance(result, dict)
        assert "cookies" in result

    def test_create_recipes_cookies_recipe_added_to_collection(self):
        # Подготовка

        # Действие

        # Проверка
        assert "cookies" in self.__start_service.recipes
        assert isinstance(self.__start_service.recipes["cookies"], RecipeModel)
        assert len(self.__start_service.recipes["cookies"].ingredients) > 0

    def test_start_service_start_all_data_populated(self):
        # Подготовка
        service = StartService()

        # Действие
        service.start()

        # Проверка
        # Проверяем все основные коллекции через data property
        data = service.data
        assert len(data[Repository.unit_measure_key]) > 0
        assert len(data[Repository.group_nomenclature_key]) > 0
        assert len(data[Repository.nomenclature_key]) > 0
        assert len(data[Repository.recipe_key]) > 0

        # Проверяем конкретное содержимое
        units = data[Repository.unit_measure_key]
        groups = data[Repository.group_nomenclature_key]
        nomenclatures = data[Repository.nomenclature_key]
        recipes = data[Repository.recipe_key]

        assert "gramm" in units
        assert "ingredients" in groups
        assert "wheat_flour" in nomenclatures
        assert "cookies" in recipes

