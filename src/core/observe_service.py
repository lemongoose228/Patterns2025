
class ObserveService:
    handlers = []

    """
    Добавить объект под наблюдение
    """
    @staticmethod
    def add(instance):
        if instance is None:
            return

        if instance not in ObserveService.handlers:
            ObserveService.handlers.append(instance)

    """
    Убрать объект из под наблюдения
    """
    @staticmethod
    def delete(instance):
        if instance is None:
            return


        if instance not in ObserveService.handlers:
            ObserveService.handlers.remove(instance)

    """
    Вызвать события
    """
    @staticmethod
    def create_event(event: str, params):
        for instance in ObserveService.handlers:
            instance.handle(event, params)