from src.logics.response_csv import ResponseCsv
from src.logics.response_markdown import ResponseMarkdown
from src.logics.response_json import ResponseJson
from src.logics.response_xml import ResponseXml
from src.core.abstract_response import AbstractResponse
from src.core.abstract_model import AbstractModel
from src.core.validator import Validator, OperationException
from src.models.settings import Settings


class FactoryEntities:
    """
    Фабрика для создания объектов формирования ответов в различных форматах.
    
    Класс инкапсулирует логику создания форматтеров ответов на основе 
    настроек приложения или явно указанного формата.
    
    Attributes:
        __match (dict): Словарь соответствия форматов классам форматтеров
        __settings (Settings): Настройки приложения для определения формата по умолчанию
    """
    
    # Словарь соответствия форматов классам форматтеров ответов
    __match = {
        "CSV": ResponseCsv,        # Формат CSV
        "Markdown": ResponseMarkdown,  # Формат Markdown
        "Json": ResponseJson,      # Формат JSON
        "XML": ResponseXml         # Формат XML
    }

    def __init__(self, settings: Settings = None):
        """
        Инициализирует фабрику сущностей.
        
        Args:
            settings (Settings, optional): Настройки приложения для определения 
                                         формата ответа по умолчанию. Defaults to None.
        """
        super().__init__()
        self.__settings = settings

    @property
    def settings(self) -> Settings:
        """
        Получить текущие настройки приложения.
        
        Returns:
            Settings: Объект настроек приложения
        """
        return self.__settings

    @settings.setter
    def settings(self, value: Settings):
        """
        Установить настройки приложения.
        
        Args:
            value (Settings): Объект настроек приложения
            
        Raises:
            ArgumentException: Если переданный объект не является экземпляром Settings
        """
        Validator.validate(value, Settings)
        self.__settings = value

    def create(self, format: str) -> AbstractResponse:
        """
        Создать форматтер ответа для указанного формата.
        
        Args:
            format (str): Название формата (CSV, Markdown, Json, XML)
            
        Returns:
            AbstractResponse: Экземпляр класса форматтера для указанного формата
            
        Raises:
            OperationException: Если указанный формат не поддерживается
        """
        if format not in self.__match.keys():
            raise OperationException("Формат не верный")
        
        return self.__match[format]()

    def create_default(self) -> AbstractResponse:
        """
        Создать форматтер ответа на основе настроек приложения.
        
        Использует формат ответа, указанный в настройках приложения.
        
        Returns:
            AbstractResponse: Экземпляр класса форматтера для формата по умолчанию
            
        Raises:
            OperationException: Если настройки не установлены или формат не поддерживается
        """
        if self.__settings is None:
            raise OperationException("Настройки не установлены")
        
        format = self.__settings.response_format
        if format not in self.__match.keys():
            raise OperationException(f"Формат {format} не поддерживается")
        
        return self.__match[format]()