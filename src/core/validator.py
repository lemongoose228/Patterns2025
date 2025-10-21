class ArgumentException(Exception):
    pass     
    

class OperationException(Exception):
    pass    


class Validator:

    @staticmethod
    def validate(value, variable_type, variable_len=None, comparison_sign="=", name=None):
        if value is None:
            if isinstance(variable_type, tuple):
                if type(None) not in variable_type:
                    raise ArgumentException("Аргумент не может быть None")
                
            elif variable_type is not type(None):
                raise ArgumentException("Аргумент не может быть None")

        if not isinstance(value, variable_type):
            raise ArgumentException(f"Аргумент должен быть типа {variable_type}")
        
        if len(str(value).strip()) == 0:
            raise ArgumentException(f"Аргумент не должен быть пустым")

        if variable_len is not None:
            if comparison_sign == "=":
                if len(str(value).strip()) != variable_len:
                    raise ArgumentException("Некорректная длина аргумента")
            elif comparison_sign == ">":
                if len(str(value).strip()) > variable_len:
                    raise ArgumentException("Некорректная длина аргумента")   
            elif comparison_sign == "<":
                if len(str(value).strip()) < variable_len:
                    raise ArgumentException("Некорректная длина аргумента")        
                
        return True
    
    def validate_models(value, variable_type, variable_name=None):
        if value is None:
            if isinstance(variable_type, tuple):
                if type(None) not in variable_type:
                    raise ArgumentException("Аргумент не может быть None")
                
            elif variable_type is not type(None):
                raise ArgumentException("Аргумент не может быть None")

        if not isinstance(value, variable_type):
            raise ArgumentException(f"Аргумент должен быть типа {variable_type.__name__}")

        if variable_name is not None:
            if value.name != variable_name:
                raise ArgumentException("Неверное поле name")

        return True