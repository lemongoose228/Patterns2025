import connexion
from flask import request, Response
import json

from src.start_service import StartService
from src.logics.factory_entities import FactoryEntities
from src.models.settings import Settings
from src.core.common import common
from src.core.validator import Validator, ArgumentException

app = connexion.FlaskApp(__name__)

# Инициализация сервисов
start_service = StartService()
start_service.start()

# Настройки по умолчанию
settings = Settings()
factory = FactoryEntities(settings)

"""
Проверить доступность REST API
"""
@app.route("/api/accessibility", methods=['GET'])
def accessibility():
    return "SUCCESS"

"""
Получить список доступных моделей
"""
@app.route("/api/models", methods=['GET'])
def get_models():
    models = common.get_models()
    return {"models": models}

"""
Получить данные в указанном формате
"""
@app.route("/api/data/<model_type>/<format_type>", methods=['GET'])
def get_data(model_type: str, format_type: str):
    try:
        # Получаем данные в зависимости от типа модели
        data_map = {
            "units": list(start_service.units_measure.values()),
            "groups": list(start_service.groups_nomenclature.values()),
            "nomenclatures": list(start_service.nomenclatures.values()),
            "recipes": list(start_service.recipes.values())
        }
        
        if model_type not in data_map:
            return {"error": f"Неизвестный тип модели: {model_type}"}, 400
        
        data = data_map[model_type]
        
        # Создаем форматтер
        format_map = {
            "csv": "CSV",
            "markdown": "Markdown", 
            "json": "Json",
            "xml": "XML"
        }
        
        if format_type not in format_map:
            return {"error": f"Неизвестный формат: {format_type}"}, 400
        
        formatter = factory.create(format_map[format_type])
        result = formatter.build(format_type, data)
        
        # Возвращаем результат в соответствующем Content-Type
        return Response(
            status=200,
            response=json.dumps({"result": result}),
            content_type="application/json"
        )
        
    except Exception as e:
        return {"error": str(e)}, 500

"""
Получить список всех рецептов в JSON формате
"""
@app.route("/api/recipes", methods=['GET'])
def get_recipes():
    try:
        # Получаем все рецепты
        recipes = list(start_service.recipes.values())
        
        # Создаем JSON форматтер
        formatter = factory.create("Json")
        result = formatter.build("json", recipes)
    
        
        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "count": len(recipes),
                "recipes": result
            }),
            content_type="application/json"
        )
        
    except Exception as e:
        return Response(
            status=500,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )

"""
Получить конкретный рецепт по ID в JSON формате
"""
@app.route("/api/recipes/<recipe_id>", methods=['GET'])
def get_recipe(recipe_id: str):
    try:
        # Валидация ID
        Validator.validate(recipe_id, str, name="recipe_id")
        
        # Ищем рецепт по ID
        data = list(start_service.data["recipe"].values())
        
        recipe = list(filter(lambda recipe: recipe.id == recipe_id, data))
        
        if not recipe:
            return Response(
                status=404,
                response=json.dumps({
                    "success": False,
                    "error": f"Рецепт с ID '{recipe_id}' не найден"
                }),
                content_type="application/json"
            )
        
        # Создаем JSON форматтер
        formatter = factory.create("Json")
        result = formatter.build("json", [recipe[0]])
        
        
        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "recipe": result
            }),
            content_type="application/json"
        )
        
    except ArgumentException as e:
        return Response(
            status=400,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )
    except Exception as e:
        return Response(
            status=500,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)