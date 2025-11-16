from src.core.validator import ArgumentException, OperationException, Validator
from src.models.settings import Settings
from src.models.company_model import CompanyModel
import json
import os


class SettingsManager:
    """
    Менеджер настроек приложения.
    
    Реализует паттерн Singleton для обеспечения единственного экземпляра менеджера.
    Обеспечивает загрузку, сохранение и управление настройками приложения из JSON файла.
    
    Attributes:
        __file_name (str): Полный путь к файлу настроек
        __settings (Settings): Объект с текущими настройками приложения
    """
    
    __file_name:str = ""
    

    def __new__(cls, file_name: str):
        """
        Реализация паттерна Singleton.
        
        Гарантирует создание только одного экземпляра SettingsManager.
        
        Args:
            file_name (str): Путь к файлу настроек
            
        Returns:
            SettingsManager: Единственный экземпляр класса SettingsManager
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(SettingsManager, cls).__new__(cls)

        return cls.instance

    def __init__(self, file_name: str):
        """
        Инициализирует менеджер настроек.
        
        Args:
            file_name (str): Путь к файлу настроек
        """
        self.file_name = file_name
        self.__settings = Settings()
        self.default_settings()

    @property
    def settings(self) -> Settings:
        """
        Получить текущие настройки приложения.
        
        Returns:
            Settings: Объект с текущими настройками приложения
        """
        return self.__settings
    

    @property
    def file_name(self) -> str:
        """
        Получить путь к файлу настроек.
        
        Returns:
            str: Полный путь к файлу настроек
        """
        return self.__file_name

    @file_name.setter
    def file_name(self, value: str):
        """
        Установить путь к файлу настроек.
        
        Проверяет существование файла перед установкой пути.
        
        Args:
            value (str): Путь к файлу настроек
            
        Raises:
            ArgumentException: Если файл не существует или путь некорректен
        """
        Validator.validate(value, str)
        full_file_name = os.path.abspath(value)        
        if os.path.exists(full_file_name):
            self.__file_name = full_file_name.strip()
        else:
            raise ArgumentException(f'Не найден файл настроек {full_file_name}')

    
    def load(self) -> bool:
        """
        Загрузить настройки из файла.
        
        Читает JSON файл и преобразует его данные в объект Settings.
        
        Returns:
            bool: True если загрузка успешна, False в случае ошибки
        """
        try:
            with open(self.__file_name, "r", encoding="utf-8") as f:
                data = json.load(f)

            return self.convert(data)
        except Exception:
            return False
        
    
    def convert(self, data: dict) -> bool:
        """
        Преобразовать данные из словаря в объект Settings.
        
        Args:
            data (dict): Словарь с данными настроек
            
        Returns:
            bool: True если преобразование успешно, False в случае ошибки
        """
        # Обработка данных компании
        if "company" in data:
            company_data = data["company"]
            self.__settings.company.name = company_data["name"]
            self.__settings.company.account = company_data["account"]
            self.__settings.company.correspondent_account = company_data["correspondent_account"]
            self.__settings.company.BIK = company_data["BIK"]
            self.__settings.company.ownership_type = company_data["ownership_type"]
            self.__settings.company.INN = company_data["INN"]
        
        # Обработка формата ответа
        if "response_format" in data:
            self.__settings.response_format = data["response_format"]
        
        # Обработка настройки первого старта
        if "first_start" in data:
            self.__settings.first_start = data["first_start"]
        
        return True


    def default_settings(self):
        """
        Установить настройки по умолчанию.
        
        Используется при инициализации или когда файл настроек недоступен.
        Устанавливает стандартные значения для всех параметров приложения.
        """
        self.__settings.company.name = "Рога и копыта"
        self.__settings.company.account = "40702810123"
        self.__settings.company.correspondent_account = "30101810123"
        self.__settings.company.BIK = "044525225"
        self.__settings.company.ownership_type = "ООО"
        self.__settings.company.INN = "123456789012"
        self.__settings.response_format = "CSV"
        self.__settings.first_start = True