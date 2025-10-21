
from src.models.company_model import CompanyModel
from src.core.validator import ArgumentException

class Settings:
    __company: CompanyModel = None

    def __init__(self):
        self.company = CompanyModel()

    @property
    def company(self) -> CompanyModel:
        return self.__company

    @company.setter
    def company(self, value: CompanyModel|None):
        if isinstance(value, CompanyModel) or value is None:
            self.__company = value
        else:
            raise ArgumentException("Ожидается экземпляр CompanyModel")
    