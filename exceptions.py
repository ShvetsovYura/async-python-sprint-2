class PoolOverflowException(Exception):

    def __init__(
            self,
            message="Превышено количество одновренменно доступных к выполнению задач ") -> None:
        super().__init__(message)


class TaskExecutionTimeout(Exception):
    pass


class SubtasksNotDoneException():
    pass


class PoolSizeNotReducedException(Exception):

    def __init__(self,
                 message="Уменьшать количество одновременно выполняемых задач нельзя") -> None:
        super().__init__(message)


class NegativePoolSizeException(Exception):

    def __init__(
            self,
            message='Нельзя делать отрицательный размер одновременно выполняемых задач') -> None:

        super().__init__(message)


class LimitAttemptsExhausted(Exception):

    def __init__(self, task_id: str, message="Лимит попыток запуска задачи исчерпан") -> None:
        super().__init__(f"{message}:{task_id}")
