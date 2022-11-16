from concurrent.futures import Future
import logging
from threading import Lock
from typing import Callable, Generator, Optional
import uuid

from aio.promise import Promise, PromiseStatus

logger = logging.getLogger(__name__)


class Task(Promise):

    def __init__(self, coro: Generator):
        super().__init__()
        self._coro = coro
        self._state = 0
        self._id = uuid.uuid4()
        # При инициализации таски - проворачиваем ее один раз со значпением None, т.е. инициализируем
        p = Promise()
        p.set_result(None)
        self.set_result(None)

    @property
    def is_done(self):
        return True if self._state else False

    @property
    def id(self):
        return self._id

    def run_step(self, promise: Optional[Promise] = None):
        res = promise.result if promise else None
        try:
            promise = self._coro.send(res)
        except StopIteration as e:
            logger.info(f"value: {e.value}")
            self.set_result(e.value)
            self._state = 1
            return

        # добавляем в колбэк проворачивание последний раз - чтобы получить StopIteration и зи него взять результат
        # Убрал - работает
        # promise.add_done_callback(self.run_step)
