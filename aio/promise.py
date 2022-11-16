from concurrent.futures import Future
from enum import Enum
from typing import Any, Callable


class PromiseStatus(Enum):
    PENDING = 0
    STARTED = 1
    FINISNED = 2


class Promise:
    """ Класс хранит состояние вызова """

    def __init__(self):
        self._callbacks: list[Callable] = []
        self._status: PromiseStatus = PromiseStatus.PENDING
        self._result = None

    def add_done_callback(self, callback: Callable) -> None:
        self._callbacks.append(callback)

    @property
    def result(self):
        return self._result

    def set_result(self, result: Any):
        self._result = result
        self._status = PromiseStatus.FINISNED

        for callback in self._callbacks:
            callback(self)
