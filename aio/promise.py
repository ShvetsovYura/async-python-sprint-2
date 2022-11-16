from typing import Any, Callable


class Promise:
    """ Класс хранит состояние вызова """

    def __init__(self):
        self._callbacks: list[Callable] = []

        self._result = None

    def add_done_callback(self, callback: Callable) -> None:
        self._callbacks.append(callback)

    @property
    def result(self):
        return self._result

    def set_result(self, result: Any):
        self._result = result

        # оказалось лишним - одни проблемы
        # for callback in self._callbacks:
        #     callback(self)
