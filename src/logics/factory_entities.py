from src.logics.response_csv import ResponseCsv
from src.core.abstract_model import AbstractModel
from src.core.validator import Validator, OperationException

class FactoryEntities:
    __match = {
        "csv": ResponseCsv
    }


    def create(self, format: str) -> AbstractModel:
        if format not in self.__match.keys():
            raise OperationException("Формат не верный")
        
        return self.__match[format]