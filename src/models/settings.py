from src.models.company_model import CompanyModel

class Settings:
    __company: CompanyModel = CompanyModel()
    __response_format: str = "CSV"
    __first_start: bool = True

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