from src.models.company_model import CompanyModel
from datetime import datetime

class Settings:
    __company: CompanyModel = CompanyModel()
    __response_format: str = "CSV"
    __first_start: bool = True
    __blocking_date: datetime = None 
    __log_level: str = "INFO"  # DEBUG, INFO, ERROR
    __log_mode: str = "FILE"  # CONSOLE, FILE
    __log_directory: str = "logs"
    __log_date_format: str = "%Y-%m-%d %H:%M:%S"
    __log_format: str = "[{level}] {timestamp} - {module}: {message}"

    @property
    def company(self) -> CompanyModel:
        return self.__company

    @property
    def response_format(self) -> str:
        return self.__response_format

    @response_format.setter
    def response_format(self, value: str):
        self.__response_format = value

    @property
    def first_start(self) -> bool:
        return self.__first_start

    @first_start.setter
    def first_start(self, value: bool):
        self.__first_start = value

    @property
    def blocking_date(self) -> datetime:
        return self.__blocking_date

    @blocking_date.setter
    def blocking_date(self, value: datetime):
        self.__blocking_date = value

    @property
    def log_level(self) -> str:
        return self.__log_level

    @log_level.setter
    def log_level(self, value: str):
        self.__log_level = value

    @property
    def log_mode(self) -> str:
        return self.__log_mode

    @log_mode.setter
    def log_mode(self, value: str):
        self.__log_mode = value

    @property
    def log_directory(self) -> str:
        return self.__log_directory

    @log_directory.setter
    def log_directory(self, value: str):
        self.__log_directory = value

    @property
    def log_date_format(self) -> str:
        return self.__log_date_format

    @log_date_format.setter
    def log_date_format(self, value: str):
        self.__log_date_format = value

    @property
    def log_format(self) -> str:
        return self.__log_format

    @log_format.setter
    def log_format(self, value: str):
        self.__log_format = value