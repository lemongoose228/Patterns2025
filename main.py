import connexion
from flask import request, Response
import json
from datetime import datetime

from src.logics.balance_service import BalanceService
from src.core.prototype import Prototype
from src.dtos.filter_dto import FilterDto
from src.start_service import StartService
from src.logics.factory_entities import FactoryEntities
from src.models.settings import Settings
from src.core.common import common
from src.core.validator import Validator, ArgumentException
from src.logics.turnover_report_service import TurnoverReportService
from src.logics.export_service import ExportService
from src.settings_manager import SettingsManager
import os
from src.logics.reference_service import ReferenceService

app = connexion.FlaskApp(__name__)

# Инициализация сервисов
start_service = StartService()
reference_service = ReferenceService(start_service)

# Загрузка настроек
settings_manager = None
try:
    settings_manager = SettingsManager("settings.json")
    settings_manager.load()
    settings = settings_manager.settings
    
    # Если первый старт, инициализируем данные
    if settings.first_start:
        start_service.start()
        settings.first_start = False
except Exception as e:
    settings = Settings()
    start_service.start()

factory = FactoryEntities(settings)

# Инициализация сервисов
turnover_service = TurnoverReportService(start_service)
export_service = ExportService(start_service)
balance_service = BalanceService(start_service, settings_manager)

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
    # Добавляем новые модели
    models.extend(["storages", "transactions"])
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
            "recipes": list(start_service.recipes.values()),
            "storages": list(start_service.storages.values()),
            "transactions": list(start_service.transactions.values())
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

"""
GET Отчет - Оборотно-сальдовая ведомость
Параметры в строке запроса: start_date, end_date, storage_id (опционально)
"""
@app.route("/api/reports/turnover", methods=['GET'])
def get_turnover_report():
    try:
        # Получаем параметры из строки запроса
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        storage_id = request.args.get('storage_id')
        
        # Валидация обязательных параметров
        if not start_date_str or not end_date_str:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Обязательные параметры: start_date, end_date"
                }),
                content_type="application/json"
            )
        
        # Парсинг дат
        try:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Неверный формат даты. Используйте ISO формат: YYYY-MM-DDTHH:MM:SS"
                }),
                content_type="application/json"
            )
        
        # Поиск склада если указан
        storage = None
        if storage_id:
            storage = start_service.storages.get(storage_id)
            if not storage:
                storage_list = list(start_service.storages.values())
                storage = next((s for s in storage_list if s.id == storage_id), None)
            
            if not storage:
                return Response(
                    status=404,
                    response=json.dumps({
                        "success": False,
                        "error": f"Склад с ID '{storage_id}' не найден"
                    }),
                    content_type="application/json"
                )
        
        # Генерация отчета
        report_data = turnover_service.generate_turnover_report(start_date, end_date, storage)
        
        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "report": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "storage": storage.name if storage else "Все склады",
                    "data": report_data
                }
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

"""
POST - Сохранить все данные в файл
Параметр file_path передается в строке запроса
"""
@app.route("/api/export/data", methods=['POST'])
def export_all_data():
    try:
        # Получаем путь к файлу из строки запроса
        file_path = request.args.get('file_path')
        
        if not file_path:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Не указан путь к файлу (file_path) в строке запроса"
                }),
                content_type="application/json"
            )
        
        # Экспортируем данные
        success = export_service.export_all_data(file_path)
        
        if success:
            return Response(
                status=200,
                response=json.dumps({
                    "success": True,
                    "message": f"Данные успешно экспортированы в файл: {file_path}"
                }),
                content_type="application/json"
            )
        else:
            return Response(
                status=500,
                response=json.dumps({
                    "success": False,
                    "error": "Ошибка при экспорте данных"
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


@app.route("/api/data/<model_type>/<format_type>/filter", methods=['POST'])
def get_filtered_data(model_type: str, format_type: str):
    try:
        # Получаем данные из тела запроса
        request_data = request.get_json()
        
        if not request_data or 'filters' not in request_data:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Не указаны фильтры в теле запроса"
                }),
                content_type="application/json"
            )
        
        # Создаем DTO фильтры
        filters = [FilterDto.from_dict(f) for f in request_data['filters']]
        
        # Получаем данные в зависимости от типа модели
        data_map = {
            "units": list(start_service.units_measure.values()),
            "groups": list(start_service.groups_nomenclature.values()),
            "nomenclatures": list(start_service.nomenclatures.values()),
            "recipes": list(start_service.recipes.values()),
            "storages": list(start_service.storages.values()),
            "transactions": list(start_service.transactions.values())
        }
        
        if model_type not in data_map:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": f"Неизвестный тип модели: {model_type}"
                }),
                content_type="application/json"
            )
        
        data = data_map[model_type]
        
        # Применяем фильтрацию через прототип
        prototype = Prototype(data)
        filtered_data = Prototype.filter(data, filters)
        
        # Создаем форматтер
        format_map = {
            "csv": "CSV",
            "markdown": "Markdown", 
            "json": "Json",
            "xml": "XML"
        }
        
        if format_type not in format_map:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": f"Неизвестный формат: {format_type}"
                }),
                content_type="application/json"
            )
        
        formatter = factory.create(format_map[format_type])
        result = formatter.build(format_type, filtered_data)
        
        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "count": len(filtered_data),
                "result": result
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
POST - Отчет Оборотно-сальдовая ведомость с фильтрацией через прототип
"""
@app.route("/api/reports/turnover/filter", methods=['POST'])
def get_filtered_turnover_report():
    try:
        # Получаем параметры из тела запроса
        request_data = request.get_json()
        
        if not request_data:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Не указаны параметры в теле запроса"
                }),
                content_type="application/json"
            )
        
        # Получаем обязательные параметры
        start_date_str = request_data.get('start_date')
        end_date_str = request_data.get('end_date')
        storage_id = request_data.get('storage_id')
        filters_data = request_data.get('filters', [])
        
        # Валидация обязательных параметров
        if not start_date_str or not end_date_str:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Обязательные параметры: start_date, end_date"
                }),
                content_type="application/json"
            )
        
        # Парсинг дат
        try:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Неверный формат даты. Используйте ISO формат: YYYY-MM-DDTHH:MM:SS"
                }),
                content_type="application/json"
            )
        
        # Поиск склада если указан
        storage = None
        if storage_id:
            storage = start_service.storages.get(storage_id)
            if not storage:
                storage_list = list(start_service.storages.values())
                storage = next((s for s in storage_list if s.id == storage_id), None)
            
            if not storage:
                return Response(
                    status=404,
                    response=json.dumps({
                        "success": False,
                        "error": f"Склад с ID '{storage_id}' не найден"
                    }),
                    content_type="application/json"
                )
        
        # Преобразуем фильтры в DTO
        filters = [FilterDto.from_dict(f) for f in filters_data]
        
        # Генерация отчета с использованием прототипа
        report_data = turnover_service.generate_turnover_report(start_date, end_date, storage, filters)
        
        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "report": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "storage": storage.name if storage else "Все склады",
                    "filters_applied": len(filters),
                    "data": report_data
                }
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


"""
GET - Получить текущую дату блокировки
"""
@app.route("/api/settings/blocking-date", methods=['GET'])
def get_blocking_date():
    try:
        blocking_date = settings_manager.settings.blocking_date
        
        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "blocking_date": blocking_date.isoformat() if blocking_date else None
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
POST - Установить дату блокировки
"""
@app.route("/api/settings/blocking-date", methods=['POST'])
def set_blocking_date():
    try:
        request_data = request.get_json()
        
        if not request_data or 'blocking_date' not in request_data:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Не указана дата блокировки в теле запроса"
                }),
                content_type="application/json"
            )
        
        blocking_date_str = request_data['blocking_date']
        
        try:
            if blocking_date_str:
                blocking_date = datetime.fromisoformat(blocking_date_str)
            else:
                blocking_date = None
        except ValueError:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Неверный формат даты. Используйте ISO формат: YYYY-MM-DDTHH:MM:SS"
                }),
                content_type="application/json"
            )
        
        # Устанавливаем дату блокировки
        settings_manager.settings.blocking_date = blocking_date
        
        # Сохраняем настройки
        settings_manager.save()
        
        # Если установлена дата блокировки, пересчитываем обороты
        if blocking_date:
            balance_service.calculate_turnovers_until_blocking_date()
        
        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "message": f"Дата блокировки установлена: {blocking_date_str}" if blocking_date_str else "Дата блокировки сброшена",
                "blocking_date": blocking_date_str
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
GET - Получить остатки на указанную дату
Параметры: date (обязательный), storage_id (опционально)
"""
@app.route("/api/reports/balances", methods=['GET'])
def get_balances_report():
    try:
        date_str = request.args.get('date')
        storage_id = request.args.get('storage_id')
        
        if not date_str:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Обязательный параметр: date"
                }),
                content_type="application/json"
            )
        
        # Парсинг даты
        try:
            target_date = datetime.fromisoformat(date_str)
        except ValueError:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Неверный формат даты. Используйте ISO формат: YYYY-MM-DDTHH:MM:SS"
                }),
                content_type="application/json"
            )
        
        # Поиск склада если указан
        storage = None
        if storage_id:
            storage = start_service.storages.get(storage_id)
            if not storage:
                storage_list = list(start_service.storages.values())
                storage = next((s for s in storage_list if s.id == storage_id), None)
            
            if not storage:
                return Response(
                    status=404,
                    response=json.dumps({
                        "success": False,
                        "error": f"Склад с ID '{storage_id}' не найден"
                    }),
                    content_type="application/json"
                )
        
        # Получаем отчет по остаткам
        report_data = balance_service.get_balance_report(target_date, storage)
        
        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "report": {
                    "calculation_date": target_date.isoformat(),
                    "storage": storage.name if storage else "Все склады",
                    "data": report_data
                }
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
GET - Получить элемент справочника по ID
"""
@app.route("/api/<reference_type>/<item_id>", methods=['GET'])
def get_reference_item(reference_type: str, item_id: str):
    try:
        Validator.validate(reference_type, str)
        Validator.validate(item_id, str)
        
        item = reference_service.get_reference_item(reference_type, item_id)
        
        # Создаем JSON форматтер
        formatter = factory.create("Json")
        result = formatter.build("json", [item])
        
        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "item": result
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

"""
PUT - Добавить новый элемент в справочник
"""
@app.route("/api/<reference_type>", methods=['PUT'])
def add_reference_item(reference_type: str):
    try:
        Validator.validate(reference_type, str)
        
        request_data = request.get_json()
        if not request_data:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Не указаны данные элемента в теле запроса"
                }),
                content_type="application/json"
            )
        
        item = reference_service.add_reference_item(reference_type, request_data)
        
        # Создаем JSON форматтер
        formatter = factory.create("Json")
        result = formatter.build("json", [item])
        
        return Response(
            status=201,
            response=json.dumps({
                "success": True,
                "message": "Элемент успешно добавлен",
                "item": result
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

"""
PATCH - Обновить элемент справочника
"""
@app.route("/api/<reference_type>/<item_id>", methods=['PATCH'])
def update_reference_item(reference_type: str, item_id: str):
    try:
        Validator.validate(reference_type, str)
        Validator.validate(item_id, str)
        
        request_data = request.get_json()
        if not request_data:
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": "Не указаны данные для обновления в теле запроса"
                }),
                content_type="application/json"
            )
        
        item = reference_service.update_reference_item(reference_type, item_id, request_data)
        
        # Создаем JSON форматтер
        formatter = factory.create("Json")
        result = formatter.build("json", [item])
        
        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "message": "Элемент успешно обновлен",
                "item": result
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

"""
DELETE - Удалить элемент справочника
"""
@app.route("/api/<reference_type>/<item_id>", methods=['DELETE'])
def delete_reference_item(reference_type: str, item_id: str):
    try:
        Validator.validate(reference_type, str)
        Validator.validate(item_id, str)
        
        reference_service.delete_reference_item(reference_type, item_id)
        
        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "message": "Элемент успешно удален"
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