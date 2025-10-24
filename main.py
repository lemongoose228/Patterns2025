import connexion
from flask import request, Response
import json

from src.start_service import StartService
from src.logics.factory_entities import FactoryEntities
from src.models.settings import Settings
from src.core.common import common

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
        content_types = {
            "csv": "text/csv",
            "markdown": "text/markdown",
            "json": "application/json",
            "xml": "application/xml"
        }
        
        return Response(
            result,
            content_type=content_types.get(format_type, "text/plain")
        )
        
    except Exception as e:
        return {"error": str(e)}, 500



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)