
from src.core.validator import Validator
from src.core.entity_model import EntityModel


class CompanyModel(EntityModel):
    __INN: int = 0
    __account: int = 0
    __correspondent_account: int = 0
    __BIK: int = 0
    __ownership_type: str = ""


    def __init__(self):
        super().__init__()

    @property
    def INN(self) -> str:
        return self.__INN
    
    @INN.setter
    def INN(self, value: str|int) -> str:
        Validator.validate(value, (str, int), 12)
        self.__INN = int(value)

    @property
    def account(self) -> str:
        return self.__account
    
    @account.setter
    def account(self, value: str|int) -> str:
        Validator.validate(value, (str, int), 11)
        self.__account = int(value)


    @property
    def correspondent_account(self) -> str:
        return self.__correspondent_account
    
    @correspondent_account.setter
    def correspondent_account(self, value: str|int) -> str:
        Validator.validate(value, (str, int), 11)
        self.__correspondent_account = int(value)
  

    @property
    def BIK(self) -> str:
        return self.__BIK
    
    @BIK.setter
    def BIK(self, value: str|int) -> str:
        Validator.validate(value, (str, int), 9)
        self.__BIK = int(value)

    @property
    def ownership_type(self) -> str:
        return self.__ownership_type
    
    @ownership_type.setter
    def ownership_type(self, value: str) -> str:
        Validator.validate(value, str, 5, ">")
        self.__ownership_type = value

