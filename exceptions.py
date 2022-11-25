class BaseException(Exception):

    def __init__(self) -> None:
        super().__init__()


class PoolOverflowException(BaseException):
    message = "Превышено количество одновренменно доступных к выполнению задач "


class TaskExecutionTimeout(BaseException):
    message = "Превышено время выполнения задачи"


class SubtasksNotDoneException(BaseException):
    message = "Подзадачи еще не выполнены"


class PoolSizeNotReducedException(BaseException):
    message = "Уменьшать количество одновременно выполняемых задач нельзя"


class NegativePoolSizeException(BaseException):
    message = 'Нельзя делать отрицательный размер одновременно выполняемых задач'


class LimitAttemptsExhausted(BaseException):
    message = "Лимит попыток запуска задачи исчерпан"


class DataFetchingException(BaseException):
    message = "Ошибка во время выполенния HTTP запроса"
