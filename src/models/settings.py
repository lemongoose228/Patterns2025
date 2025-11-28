from src.models.company_model import CompanyModel
from datetime import datetime

class Settings:
    __company: CompanyModel = CompanyModel()
    __response_format: str = "CSV"
    __first_start: bool = True
    __blocking_date: datetime = None 

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
