from src.core.validator import Validator
from src.core.entity_model import EntityModel

class StorageModel(EntityModel):
    
    def __init__(self, name: str = ""):
        super().__init__()
        if name:
            self.name = name

        


        

