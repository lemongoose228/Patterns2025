from src.core.validator import ArgumentException, OperationException, Validator
from src.models.settings import Settings
from src.models.company_model import CompanyModel
import json
import os

class SettingsManager:
    __file_name:str = ""
    

    def __new__(cls, file_name: str):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SettingsManager, cls).__new__(cls)

        return cls.instance

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.__settings = Settings()
        self.default_settings()


    @property
    def settings(self) -> Settings:
        return self.__settings
    

    @property
    def file_name(self) -> str:
        return self.__file_name

    @file_name.setter
    def file_name(self, value: str):
        Validator.validate(value, str)
        full_file_name = os.path.abspath(value)        
        if os.path.exists(full_file_name):
            self.__file_name = full_file_name.strip()
        else:
            raise ArgumentException(f'Не найден файл настроек {full_file_name}')

    
    def load(self):
        try:
            with open(self.__file_name, "r", encoding="utf-8") as f:
                data = json.load(f)

            return self.convert(data)
        except Exception:
            return False
        
    
    def convert(self, data: dict) -> bool:
        if "company" in data:
            company_data = data["company"]
            self.__settings.company.name = company_data["name"]
            self.__settings.company.account = company_data["account"]
            self.__settings.company.correspondent_account = company_data["correspondent_account"]
            self.__settings.company.BIK = company_data["BIK"]
            self.__settings.company.ownership_type = company_data["ownership_type"]
            self.__settings.company.INN = company_data["INN"]
        
            return True

        return False

    def default_settings(self):
        self.__settings.company.name = "Рога и копыта"
        self.__settings.company.account = "40702810123"
        self.__settings.company.correspondent_account = "30101810123"
        self.__settings.company.BIK = "044525225"
        self.__settings.company.ownership_type = "ООО"
        self.__settings.company.INN = "123456789012"