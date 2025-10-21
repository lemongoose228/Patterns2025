
class Repository:
    __data= {}
    
    unit_measure_key: str = "unit_measure"
    group_nomenclature_key: str = "group_nomenclature"
    nomenclature_key: str = "nomenclature"
    recipe_key: str = "recipe"

    @property
    def data(self):
        return self.__data
    
