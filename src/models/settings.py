from src.models.company_model import CompanyModel
from src.core.validator import ArgumentException


class Settings:
    """
    Класс настроек приложения.
    
    Содержит конфигурационные параметры приложения, включая данные компании
    и предпочтительный формат ответов для экспорта данных.
    Обеспечивает валидацию устанавливаемых значений.
    
    Attributes:
        __company (CompanyModel): Данные компании (реквизиты, контактная информация)
        __response_format (str): Предпочтительный формат ответов для экспорта данных
    """
    
    __company: CompanyModel = None
    __response_format: str = ""

    def __init__(self):
        """
        Инициализирует настройки со значениями по умолчанию.
        
        Создает экземпляр CompanyModel и устанавливает формат ответов по умолчанию в CSV.
        """
        self.company = CompanyModel()
        self.response_format = "CSV"

    @property
    def company(self) -> CompanyModel:
        """
        Получить данные компании.
        
        Returns:
            CompanyModel: Объект с данными компании (реквизиты, название, контакты)
        """
        return self.__company

    @company.setter
    def company(self, value: CompanyModel|None):
        """
        Установить данные компании.
        
        Args:
            value (CompanyModel|None): Объект с данными компании или None для сброса
            
        Raises:
            ArgumentException: Если переданный объект не является экземпляром CompanyModel
        """
        if isinstance(value, CompanyModel) or value is None:
            self.__company = value
        else:
            raise ArgumentException("Ожидается экземпляр CompanyModel")

    @property
    def response_format(self) -> str:
        """
        Получить предпочтительный формат ответов.
        
        Определяет в каком формате будут экспортироваться данные при использовании
        фабрики сущностей без явного указания формата.
        
        Returns:
            str: Название формата (CSV, Markdown, Json, XML)
        """
        return self.__response_format
    
    @response_format.setter
    def response_format(self, value: str):
        """
        Установить предпочтительный формат ответов.
        
        Проверяет что устанавливаемый формат находится в списке поддерживаемых.
        
        Args:
            value (str): Название формата (CSV, Markdown, Json, XML)
            
        Raises:
            ArgumentException: Если указан неподдерживаемый формат
        """
        # Список поддерживаемых форматов экспорта данных
        valid_formats = ["CSV", "Markdown", "Json", "XML"]
        
        # Валидация устанавливаемого формата
        if value not in valid_formats:
            raise ArgumentException(f"Недопустимый формат ответа. Допустимые значения: {valid_formats}")
        
        self.__response_format = value