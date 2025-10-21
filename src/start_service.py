from src.core.validator import Validator
from src.models.group_nomenclature_model import GroupNomenclatureModel
from src.repository import Repository
from src.models.unit_measurement_model import UnitMeasurement
from src.models.nomenclature_model import NomenclatureModel
from src.models.recipe_model import RecipeModel

class StartService():
    __repository: Repository = Repository()
    
    def __init__(self):
        self.data[Repository.unit_measure_key] = {}
        self.data[Repository.group_nomenclature_key] = {}
        self.data[Repository.nomenclature_key] = {}
        self.data[Repository.recipe_key] = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StartService, cls).__new__(cls)

        return cls.instance
    

    '''
    Метод для генерации эталонных единиц измерения
    '''
    def __default_create_units_measure(self):
        gramm = UnitMeasurement.create_gramm()
        self.units_measure["gramm"] = gramm
        self.units_measure["kg"] = UnitMeasurement.create_kilo(gramm)


    '''
    Метод для генерации эталонных групп номенклатур
    '''
    def __default_create_group_nomenclature(self):
        ingredients = GroupNomenclatureModel()
        self.groups_nomenclature["ingredients"] = ingredients


    '''
    Метод для генерации эталонных номенклатур
    '''
    def __default_create_nomenclature(self):
        ingredients = self.groups_nomenclature["ingredients"]
        gramm = self.units_measure["gramm"]

        wheat_flour = NomenclatureModel("wheat flour", "wheat flour", ingredients, gramm)
        oatmeal = NomenclatureModel("oatmeal", "oatmeal", ingredients, gramm)
        sugar = NomenclatureModel("sugar", "granulated sugar", ingredients, gramm)
        butter = NomenclatureModel("butter", "butter", ingredients, gramm)
        chicken_egg = NomenclatureModel("chicken egg", "chicken egg", ingredients, gramm)
        dark_chocolate = NomenclatureModel("dark chocolate", "dark chocolate", ingredients, gramm)
        baking_powder = NomenclatureModel("baking powder", "baking powder", ingredients, gramm)
        salt = NomenclatureModel("salt", "salt", ingredients, gramm)

        self.nomenclatures["wheat_flour"] = wheat_flour
        self.nomenclatures["oatmeal"] = oatmeal
        self.nomenclatures["sugar"] = sugar
        self.nomenclatures["butter"] = butter
        self.nomenclatures["chicken_egg"] = chicken_egg
        self.nomenclatures["dark_chocolate"] = dark_chocolate
        self.nomenclatures["baking_powder"] = baking_powder
        self.nomenclatures["salt"] = salt

    '''
    Метод для создания рецепта печенья
    '''
    def create_cookies_recipe(self, wheat_flour, 
                              oatmeal, sugar, 
                              butter, chicken_egg, 
                              dark_chocolate, baking_powder, 
                              salt):
        
        Validator.validate_models(wheat_flour, NomenclatureModel, "wheat flour")
        Validator.validate_models(oatmeal, NomenclatureModel, "oatmeal")
        Validator.validate_models(sugar, NomenclatureModel, "sugar")
        Validator.validate_models(butter, NomenclatureModel, "butter")
        Validator.validate_models(chicken_egg, NomenclatureModel, "chicken egg")
        Validator.validate_models(dark_chocolate, NomenclatureModel, "dark chocolate")
        Validator.validate_models(baking_powder, NomenclatureModel, "baking powder")
        Validator.validate_models(salt, NomenclatureModel, "salt")


        description = """
            Время приготовления: 25 минут
            Духовку разогрейте до 180°C. Противень застелите бумагой для выпечки.
            Шоколад измельчите на небольшие кусочки ножом.
            Масло комнатной температуры взбейте с сахаром до легкой пены.
            Добавьте яйцо и взбивайте еще 1-2 минуты до однородности.
            В отдельной миске смешайте овсяные хлопья, муку, разрыхлитель и соль.
            Соедините сухие ингредиенты с масляной смесью, добавьте измельченный шоколад.
            Замесите тесто ложкой до однородной консистенции.
            Сформируйте небольшие шарики (примерно по 30-40 гр), выложите на противень и слегка приплюсните.
            Выпекайте 12-15 минут до золотистого края. Дайте печенью остыть на противне 5 минут перед подачей.
            Приятного аппетита!
        """

        cookies = RecipeModel("cookies", description)
        self.add_ingredient(cookies, wheat_flour, 100)
        self.add_ingredient(cookies, oatmeal, 200)
        self.add_ingredient(cookies, sugar, 150)
        self.add_ingredient(cookies, butter, 180)
        self.add_ingredient(cookies, chicken_egg, 55)
        self.add_ingredient(cookies, dark_chocolate, 100)
        self.add_ingredient(cookies, baking_powder, 5)
        self.add_ingredient(cookies, salt, 2)

        return cookies

    '''
    Метод для генерации эталонных рецептов
    '''
    def __default_create_recipes(self):
        cookies = self.create_cookies_recipe(
            self.nomenclatures["wheat_flour"],
            self.nomenclatures["oatmeal"],
            self.nomenclatures["sugar"],
            self.nomenclatures["butter"],
            self.nomenclatures["chicken_egg"],
            self.nomenclatures["dark_chocolate"],
            self.nomenclatures["baking_powder"],
            self.nomenclatures["salt"],
        )

        self.recipes["cookies"] = cookies

    '''
    Добавление ингредиента в модель рецепта
    '''
    def add_ingredient(self, recipe: RecipeModel, ingredient: NomenclatureModel, count: int):
        Validator.validate_models(recipe, RecipeModel)
        Validator.validate_models(ingredient, NomenclatureModel)
        Validator.validate(count, int)

        recipe.ingredients[ingredient.name] = count

    '''
    Основной метод для генерации эталонных данных
    '''
    def start(self):
        self.__default_create_units_measure()
        self.__default_create_group_nomenclature()
        self.__default_create_nomenclature()
        self.__default_create_recipes()

    '''
    Стартовый набор данных
    '''
    @property
    def data(self):
        return self.__repository.data
    
    """Список номенклатур"""
    @property
    def nomenclatures(self):
        return self.data[Repository.nomenclature_key]
    
    """Список единиц измерения"""
    @property
    def units_measure(self):
        return self.data[Repository.unit_measure_key]

    """Список групп номенклатур"""
    @property
    def groups_nomenclature(self):
        return self.data[Repository.group_nomenclature_key]
    
    """Список рецептов"""
    @property
    def recipes(self):
        return self.data[Repository.recipe_key]