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
from src.logics.logger_service import LoggerService

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

    # Инициализация логгера
    logger = LoggerService()
    logger.set_settings_manager(settings_manager)
    LoggerService.log_info("Загружены настройки приложения", "main")

    # Если первый старт, инициализируем данные
    if settings.first_start:
        LoggerService.log_info("Первый запуск приложения, инициализация данных", "main")
        start_service.start()
        settings.first_start = False
        settings_manager.save()
        LoggerService.log_info("Данные успешно инициализированы", "main")
except Exception as e:
    settings = Settings()
    start_service.start()
    LoggerService.log_error(f"Ошибка загрузки настроек: {str(e)}", "main")

factory = FactoryEntities(settings)

# Инициализация сервисов
turnover_service = TurnoverReportService(start_service)
export_service = ExportService(start_service)
balance_service = BalanceService(start_service, settings_manager)

LoggerService.log_info("Все сервисы инициализированы, приложение готово к работе", "main")

"""
Проверить доступность REST API
"""
@app.route("/api/accessibility", methods=['GET'])
def accessibility():
    # Логируем вызов API
    LoggerService.log_api_call("GET", "/api/accessibility", 200)
    return "SUCCESS"

"""
Получить список доступных моделей
"""
@app.route("/api/models", methods=['GET'])
def get_models():
    try:
        models = common.get_models()
        # Добавляем новые модели
        models.extend(["storages", "transactions"])

        # Логируем успешный вызов API
        LoggerService.log_api_call("GET", "/api/models", 200)
        LoggerService.log_debug(f"Получен список моделей: {len(models)} шт.", "api")

        return {"models": models}
    except Exception as e:
        # Логируем ошибку
        LoggerService.log_api_call("GET", "/api/models", 500)
        LoggerService.log_error(f"Ошибка получения списка моделей: {str(e)}", "api")
        return {"error": str(e)}, 500


"""
Получить данные в указанном формате
"""


@app.route("/api/data/<model_type>/<format_type>", methods=['GET'])
def get_data(model_type: str, format_type: str):
    try:
        # Логируем начало обработки запроса
        LoggerService.log_info(f"Запрос данных: {model_type} в формате {format_type}", "api")

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
            error_msg = f"Неизвестный тип модели: {model_type}"
            LoggerService.log_api_call("GET", f"/api/data/{model_type}/{format_type}", 400)
            LoggerService.log_error(error_msg, "api")
            return {"error": error_msg}, 400

        data = data_map[model_type]

        # Создаем форматтер
        format_map = {
            "csv": "CSV",
            "markdown": "Markdown",
            "json": "Json",
            "xml": "XML"
        }

        if format_type not in format_map:
            error_msg = f"Неизвестный формат: {format_type}"
            LoggerService.log_api_call("GET", f"/api/data/{model_type}/{format_type}", 400)
            LoggerService.log_error(error_msg, "api")
            return {"error": error_msg}, 400

        formatter = factory.create(format_map[format_type])
        result = formatter.build(format_type, data)

        # Логируем успешный результат
        LoggerService.log_api_call("GET", f"/api/data/{model_type}/{format_type}", 200)
        LoggerService.log_info(f"Получены данные {model_type} в формате {format_type}: {len(data)} записей", "api")

        # Возвращаем результат в соответствующем Content-Type
        return Response(
            status=200,
            response=json.dumps({"result": result}),
            content_type="application/json"
        )

    except Exception as e:
        # Логируем ошибку
        LoggerService.log_api_call("GET", f"/api/data/{model_type}/{format_type}", 500)
        LoggerService.log_error(f"Ошибка получения данных {model_type}: {str(e)}", "api")
        return {"error": str(e)}, 500


"""
Получить список всех рецептов в JSON формате
"""


@app.route("/api/recipes", methods=['GET'])
def get_recipes():
    try:
        # Логируем начало обработки
        LoggerService.log_info("Запрос списка рецептов", "api")

        # Получаем все рецепты
        recipes = list(start_service.recipes.values())

        # Создаем JSON форматтер
        formatter = factory.create("Json")
        result = formatter.build("json", recipes)

        # Логируем успешный результат
        LoggerService.log_api_call("GET", "/api/recipes", 200)
        LoggerService.log_info(f"Получены рецепты: {len(recipes)} шт.", "api")

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
        # Логируем ошибку
        LoggerService.log_api_call("GET", "/api/recipes", 500)
        LoggerService.log_error(f"Ошибка получения рецептов: {str(e)}", "api")
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
        # Логируем начало обработки
        LoggerService.log_info(f"Запрос рецепта с ID: {recipe_id}", "api")

        # Валидация ID
        Validator.validate(recipe_id, str, name="recipe_id")

        # Ищем рецепт по ID
        data = list(start_service.data["recipe"].values())

        recipe = list(filter(lambda recipe: recipe.id == recipe_id, data))

        if not recipe:
            error_msg = f"Рецепт с ID '{recipe_id}' не найден"
            LoggerService.log_api_call("GET", f"/api/recipes/{recipe_id}", 404)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=404,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
                }),
                content_type="application/json"
            )

        # Создаем JSON форматтер
        formatter = factory.create("Json")
        result = formatter.build("json", [recipe[0]])

        # Логируем успешный результат
        LoggerService.log_api_call("GET", f"/api/recipes/{recipe_id}", 200)
        LoggerService.log_info(f"Получен рецепт с ID: {recipe_id}", "api")

        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "recipe": result
            }),
            content_type="application/json"
        )

    except ArgumentException as e:
        # Логируем ошибку валидации
        LoggerService.log_api_call("GET", f"/api/recipes/{recipe_id}", 400)
        LoggerService.log_error(f"Ошибка валидации при получении рецепта: {str(e)}", "api")
        return Response(
            status=400,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )
    except Exception as e:
        # Логируем общую ошибку
        LoggerService.log_api_call("GET", f"/api/recipes/{recipe_id}", 500)
        LoggerService.log_error(f"Ошибка получения рецепта: {str(e)}", "api")
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
"""


@app.route("/api/reports/turnover", methods=['GET'])
def get_turnover_report():
    try:
        # Получаем параметры из строки запроса
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        storage_id = request.args.get('storage_id')

        # Логируем начало обработки
        LoggerService.log_info(f"Запрос отчета ОСВ с {start_date_str} по {end_date_str}", "api")

        # Валидация обязательных параметров
        if not start_date_str or not end_date_str:
            error_msg = "Обязательные параметры: start_date, end_date"
            LoggerService.log_api_call("GET", "/api/reports/turnover", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
                }),
                content_type="application/json"
            )

        # Парсинг дат
        try:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError:
            error_msg = "Неверный формат даты. Используйте ISO формат: YYYY-MM-DDTHH:MM:SS"
            LoggerService.log_api_call("GET", "/api/reports/turnover", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
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
                error_msg = f"Склад с ID '{storage_id}' не найден"
                LoggerService.log_api_call("GET", "/api/reports/turnover", 404)
                LoggerService.log_error(error_msg, "api")
                return Response(
                    status=404,
                    response=json.dumps({
                        "success": False,
                        "error": error_msg
                    }),
                    content_type="application/json"
                )

        # Генерация отчета
        report_data = turnover_service.generate_turnover_report(start_date, end_date, storage)

        # Логируем успешный результат
        LoggerService.log_api_call("GET", "/api/reports/turnover", 200)
        LoggerService.log_info(f"Сформирован отчет ОСВ с {start_date} по {end_date}", "api")

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
        # Логируем ошибку аргументов
        LoggerService.log_api_call("GET", "/api/reports/turnover", 400)
        LoggerService.log_error(f"Ошибка при формировании отчета ОСВ: {str(e)}", "api")
        return Response(
            status=400,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )
    except Exception as e:
        # Логируем общую ошибку
        LoggerService.log_api_call("GET", "/api/reports/turnover", 500)
        LoggerService.log_error(f"Ошибка при формировании отчета ОСВ: {str(e)}", "api")
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
"""


@app.route("/api/export/data", methods=['POST'])
def export_all_data():
    try:
        # Получаем путь к файлу из строки запроса
        file_path = request.args.get('file_path')

        # Логируем начало обработки
        LoggerService.log_info(f"Запрос экспорта данных в файл: {file_path}", "api")

        if not file_path:
            error_msg = "Не указан путь к файлу (file_path) в строке запроса"
            LoggerService.log_api_call("POST", "/api/export/data", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
                }),
                content_type="application/json"
            )

        # Получаем данные запроса для логирования (для DELETE, PUT, PATCH)
        request_data = None
        if request.is_json:
            request_data = request.get_json(silent=True) or "Empty or invalid JSON"

        # Логируем данные запроса для изменяющих операций
        if request_data:
            LoggerService.log_api_call("POST", "/api/export/data", 200, request_data)
        else:
            LoggerService.log_api_call("POST", "/api/export/data", 200)

        # Экспортируем данные
        success = export_service.export_all_data(file_path)

        if success:
            LoggerService.log_info(f"Данные успешно экспортированы в файл: {file_path}", "api")
            return Response(
                status=200,
                response=json.dumps({
                    "success": True,
                    "message": f"Данные успешно экспортированы в файл: {file_path}"
                }),
                content_type="application/json"
            )
        else:
            error_msg = "Ошибка при экспорте данных"
            LoggerService.log_api_call("POST", "/api/export/data", 500)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=500,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
                }),
                content_type="application/json"
            )

    except Exception as e:
        # Логируем ошибку
        LoggerService.log_api_call("POST", "/api/export/data", 500)
        LoggerService.log_error(f"Ошибка экспорта данных: {str(e)}", "api")
        return Response(
            status=500,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )


"""
POST - Получить отфильтрованные данные
"""


@app.route("/api/data/<model_type>/<format_type>/filter", methods=['POST'])
def get_filtered_data(model_type: str, format_type: str):
    try:
        # Логируем начало обработки
        LoggerService.log_info(f"Запрос фильтрации данных {model_type} в формате {format_type}", "api")

        # Получаем данные из тела запроса
        request_data = request.get_json()

        # Логируем данные запроса
        if request_data:
            LoggerService.log_api_call("POST", f"/api/data/{model_type}/{format_type}/filter", 200, request_data)
        else:
            LoggerService.log_api_call("POST", f"/api/data/{model_type}/{format_type}/filter", 200)

        if not request_data or 'filters' not in request_data:
            error_msg = "Не указаны фильтры в теле запроса"
            LoggerService.log_api_call("POST", f"/api/data/{model_type}/{format_type}/filter", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
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
            error_msg = f"Неизвестный тип модели: {model_type}"
            LoggerService.log_api_call("POST", f"/api/data/{model_type}/{format_type}/filter", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
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
            error_msg = f"Неизвестный формат: {format_type}"
            LoggerService.log_api_call("POST", f"/api/data/{model_type}/{format_type}/filter", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
                }),
                content_type="application/json"
            )

        formatter = factory.create(format_map[format_type])
        result = formatter.build(format_type, filtered_data)

        LoggerService.log_info(
            f"Применены фильтры к {model_type}: {len(filters)} фильтров, результат: {len(filtered_data)} записей",
            "api")

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
        # Логируем ошибку
        LoggerService.log_api_call("POST", f"/api/data/{model_type}/{format_type}/filter", 500)
        LoggerService.log_error(f"Ошибка фильтрации данных: {str(e)}", "api")
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

        # Логируем начало обработки
        LoggerService.log_info("Запрос отчета ОСВ с фильтрацией", "api")

        # Логируем данные запроса
        if request_data:
            LoggerService.log_api_call("POST", "/api/reports/turnover/filter", 200, request_data)
        else:
            LoggerService.log_api_call("POST", "/api/reports/turnover/filter", 200)

        if not request_data:
            error_msg = "Не указаны параметры в теле запроса"
            LoggerService.log_api_call("POST", "/api/reports/turnover/filter", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
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
            error_msg = "Обязательные параметры: start_date, end_date"
            LoggerService.log_api_call("POST", "/api/reports/turnover/filter", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
                }),
                content_type="application/json"
            )

        # Парсинг дат
        try:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError:
            error_msg = "Неверный формат даты. Используйте ISO формат: YYYY-MM-DDTHH:MM:SS"
            LoggerService.log_api_call("POST", "/api/reports/turnover/filter", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
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
                error_msg = f"Склад с ID '{storage_id}' не найден"
                LoggerService.log_api_call("POST", "/api/reports/turnover/filter", 404)
                LoggerService.log_error(error_msg, "api")
                return Response(
                    status=404,
                    response=json.dumps({
                        "success": False,
                        "error": error_msg
                    }),
                    content_type="application/json"
                )

        # Преобразуем фильтры в DTO
        filters = [FilterDto.from_dict(f) for f in filters_data]

        # Генерация отчета с использованием прототипа
        report_data = turnover_service.generate_turnover_report(start_date, end_date, storage, filters)

        LoggerService.log_info(f"Сформирован отчет ОСВ с фильтрацией: {len(filters)} фильтров", "api")

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
        # Логируем ошибку аргументов
        LoggerService.log_api_call("POST", "/api/reports/turnover/filter", 400)
        LoggerService.log_error(f"Ошибка при формировании отчета ОСВ: {str(e)}", "api")
        return Response(
            status=400,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )
    except Exception as e:
        # Логируем общую ошибку
        LoggerService.log_api_call("POST", "/api/reports/turnover/filter", 500)
        LoggerService.log_error(f"Ошибка при формировании отчета ОСВ: {str(e)}", "api")
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

        # Логируем успешный запрос
        LoggerService.log_api_call("GET", "/api/settings/blocking-date", 200)
        LoggerService.log_debug("Получена дата блокировки", "api")

        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "blocking_date": blocking_date.isoformat() if blocking_date else None
            }),
            content_type="application/json"
        )

    except Exception as e:
        # Логируем ошибку
        LoggerService.log_api_call("GET", "/api/settings/blocking-date", 500)
        LoggerService.log_error(f"Ошибка получения даты блокировки: {str(e)}", "api")
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

        # Логируем начало обработки
        LoggerService.log_info("Запрос установки даты блокировки", "api")

        # Логируем данные запроса
        if request_data:
            LoggerService.log_api_call("POST", "/api/settings/blocking-date", 200, request_data)
        else:
            LoggerService.log_api_call("POST", "/api/settings/blocking-date", 200)

        if not request_data or 'blocking_date' not in request_data:
            error_msg = "Не указана дата блокировки в теле запроса"
            LoggerService.log_api_call("POST", "/api/settings/blocking-date", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
                }),
                content_type="application/json"
            )

        blocking_date_str = request_data['blocking_date']
        old_blocking_date = settings_manager.settings.blocking_date

        try:
            if blocking_date_str:
                blocking_date = datetime.fromisoformat(blocking_date_str)
            else:
                blocking_date = None
        except ValueError:
            error_msg = "Неверный формат даты. Используйте ISO формат: YYYY-MM-DDTHH:MM:SS"
            LoggerService.log_api_call("POST", "/api/settings/blocking-date", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
                }),
                content_type="application/json"
            )

        # Устанавливаем дату блокировки
        settings_manager.settings.blocking_date = blocking_date

        # Логируем изменение настроек
        LoggerService.log_settings_change(
            setting="blocking_date",
            old_value=old_blocking_date.isoformat() if old_blocking_date else None,
            new_value=blocking_date_str
        )

        # Сохраняем настройки
        settings_manager.save()

        # Если установлена дата блокировки, пересчитываем обороты
        if blocking_date:
            balance_service.calculate_turnovers_until_blocking_date()

        message = f"Дата блокировки установлена: {blocking_date_str}" if blocking_date_str else "Дата блокировки сброшена"
        LoggerService.log_info(message, "api")

        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "message": message,
                "blocking_date": blocking_date_str
            }),
            content_type="application/json"
        )

    except Exception as e:
        # Логируем ошибку
        LoggerService.log_api_call("POST", "/api/settings/blocking-date", 500)
        LoggerService.log_error(f"Ошибка установки даты блокировки: {str(e)}", "api")
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
"""


@app.route("/api/reports/balances", methods=['GET'])
def get_balances_report():
    try:
        date_str = request.args.get('date')
        storage_id = request.args.get('storage_id')

        # Логируем начало обработки
        LoggerService.log_info(f"Запрос отчета по остаткам на дату: {date_str}", "api")

        if not date_str:
            error_msg = "Обязательный параметр: date"
            LoggerService.log_api_call("GET", "/api/reports/balances", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
                }),
                content_type="application/json"
            )

        # Парсинг даты
        try:
            target_date = datetime.fromisoformat(date_str)
        except ValueError:
            error_msg = "Неверный формат даты. Используйте ISO формат: YYYY-MM-DDTHH:MM:SS"
            LoggerService.log_api_call("GET", "/api/reports/balances", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
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
                error_msg = f"Склад с ID '{storage_id}' не найден"
                LoggerService.log_api_call("GET", "/api/reports/balances", 404)
                LoggerService.log_error(error_msg, "api")
                return Response(
                    status=404,
                    response=json.dumps({
                        "success": False,
                        "error": error_msg
                    }),
                    content_type="application/json"
                )

        # Получаем отчет по остаткам
        report_data = balance_service.get_balance_report(target_date, storage)

        LoggerService.log_info(f"Сформирован отчет по остаткам на {date_str}", "api")

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
        # Логируем ошибку
        LoggerService.log_api_call("GET", "/api/reports/balances", 500)
        LoggerService.log_error(f"Ошибка получения отчета по остаткам: {str(e)}", "api")
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
        # Логируем начало обработки
        LoggerService.log_info(f"Запрос элемента справочника {reference_type} с ID: {item_id}", "api")

        Validator.validate(reference_type, str)
        Validator.validate(item_id, str)

        item = reference_service.get_reference_item(reference_type, item_id)

        # Создаем JSON форматтер
        formatter = factory.create("Json")
        result = formatter.build("json", [item])

        # Логируем успешный запрос
        LoggerService.log_api_call("GET", f"/api/{reference_type}/{item_id}", 200)
        LoggerService.log_debug(f"Получен элемент справочника {reference_type}: {item_id}", "api")

        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "item": result
            }),
            content_type="application/json"
        )

    except ArgumentException as e:
        # Логируем ошибку аргументов
        LoggerService.log_api_call("GET", f"/api/{reference_type}/{item_id}", 400)
        LoggerService.log_error(f"Ошибка получения элемента справочника: {str(e)}", "api")
        return Response(
            status=400,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )
    except Exception as e:
        # Логируем общую ошибку
        LoggerService.log_api_call("GET", f"/api/{reference_type}/{item_id}", 500)
        LoggerService.log_error(f"Ошибка получения элемента справочника: {str(e)}", "api")
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
        # Логируем начало обработки
        LoggerService.log_info(f"Запрос добавления элемента в справочник {reference_type}", "api")

        Validator.validate(reference_type, str)

        request_data = request.get_json()

        # Логируем данные запроса (особенно важно для PUT)
        if request_data:
            LoggerService.log_api_call("PUT", f"/api/{reference_type}", 201, request_data)
        else:
            LoggerService.log_api_call("PUT", f"/api/{reference_type}", 201)

        if not request_data:
            error_msg = "Не указаны данные элемента в теле запроса"
            LoggerService.log_api_call("PUT", f"/api/{reference_type}", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
                }),
                content_type="application/json"
            )

        item = reference_service.add_reference_item(reference_type, request_data)

        # Создаем JSON форматтер
        formatter = factory.create("Json")
        result = formatter.build("json", [item])

        LoggerService.log_info(f"Добавлен элемент в справочник {reference_type}", "api")

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
        # Логируем ошибку аргументов
        LoggerService.log_api_call("PUT", f"/api/{reference_type}", 400)
        LoggerService.log_error(f"Ошибка добавления элемента в справочник: {str(e)}", "api")
        return Response(
            status=400,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )
    except Exception as e:
        # Логируем общую ошибку
        LoggerService.log_api_call("PUT", f"/api/{reference_type}", 500)
        LoggerService.log_error(f"Ошибка добавления элемента в справочник: {str(e)}", "api")
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
        # Логируем начало обработки
        LoggerService.log_info(f"Запрос обновления элемента справочника {reference_type} с ID: {item_id}", "api")

        Validator.validate(reference_type, str)
        Validator.validate(item_id, str)

        request_data = request.get_json()

        # Логируем данные запроса (особенно важно для PATCH)
        if request_data:
            LoggerService.log_api_call("PATCH", f"/api/{reference_type}/{item_id}", 200, request_data)
        else:
            LoggerService.log_api_call("PATCH", f"/api/{reference_type}/{item_id}", 200)

        if not request_data:
            error_msg = "Не указаны данные для обновления в теле запроса"
            LoggerService.log_api_call("PATCH", f"/api/{reference_type}/{item_id}", 400)
            LoggerService.log_error(error_msg, "api")
            return Response(
                status=400,
                response=json.dumps({
                    "success": False,
                    "error": error_msg
                }),
                content_type="application/json"
            )

        item = reference_service.update_reference_item(reference_type, item_id, request_data)

        # Создаем JSON форматтер
        formatter = factory.create("Json")
        result = formatter.build("json", [item])

        LoggerService.log_info(f"Обновлен элемент справочника {reference_type}: {item_id}", "api")

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
        # Логируем ошибку аргументов
        LoggerService.log_api_call("PATCH", f"/api/{reference_type}/{item_id}", 400)
        LoggerService.log_error(f"Ошибка обновления элемента справочника: {str(e)}", "api")
        return Response(
            status=400,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )
    except Exception as e:
        # Логируем общую ошибку
        LoggerService.log_api_call("PATCH", f"/api/{reference_type}/{item_id}", 500)
        LoggerService.log_error(f"Ошибка обновления элемента справочника: {str(e)}", "api")
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
        # Логируем начало обработки
        LoggerService.log_info(f"Запрос удаления элемента справочника {reference_type} с ID: {item_id}", "api")

        Validator.validate(reference_type, str)
        Validator.validate(item_id, str)

        # Логируем данные запроса (особенно важно для DELETE)
        LoggerService.log_api_call("DELETE", f"/api/{reference_type}/{item_id}", 200)

        reference_service.delete_reference_item(reference_type, item_id)

        LoggerService.log_info(f"Удален элемент справочника {reference_type}: {item_id}", "api")

        return Response(
            status=200,
            response=json.dumps({
                "success": True,
                "message": "Элемент успешно удален"
            }),
            content_type="application/json"
        )

    except ArgumentException as e:
        # Логируем ошибку аргументов
        LoggerService.log_api_call("DELETE", f"/api/{reference_type}/{item_id}", 400)
        LoggerService.log_error(f"Ошибка удаления элемента справочника: {str(e)}", "api")
        return Response(
            status=400,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )
    except Exception as e:
        # Логируем общую ошибку
        LoggerService.log_api_call("DELETE", f"/api/{reference_type}/{item_id}", 500)
        LoggerService.log_error(f"Ошибка удаления элемента справочника: {str(e)}", "api")
        return Response(
            status=500,
            response=json.dumps({
                "success": False,
                "error": str(e)
            }),
            content_type="application/json"
        )


# Обработчик для закрытия приложения (сброс буфера логов)
import atexit


@atexit.register
def shutdown():
    logger = LoggerService()
    logger.flush()
    LoggerService.log_info("Приложение завершает работу", "main")


if __name__ == '__main__':
    LoggerService.log_info("Запуск Flask приложения", "main")
    app.run(host="0.0.0.0", port=8080)