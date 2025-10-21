from src.core.abstract_response import AbstractResponse
from src.core.common import common

class ResponseCsv(AbstractResponse):

    def __init__(self):
        super().__init__()

    # Сформировать CSV 
    def build(self, format: str, data: list):
        text = super().build(format, data)

        # Шапка
        item = data[0]

        fields = common.get_fields(item)

        for field in fields:
            text += f"{field};"

        # Данные
        return text