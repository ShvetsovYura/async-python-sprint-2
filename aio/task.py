from enum import Enum
import logging
from typing import Generator, Optional
import uuid
from datetime import datetime, timedelta

from aio.promise import Promise
from exceptions import TaskExecutionTimeout

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    INIT = "INIT"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"


class Task(Promise):

    def __init__(
        self,
        coro: Generator,
        start_at: datetime = datetime.now(),
        dependencies: list['Task'] = [],
        timeout: Optional[timedelta] = None,
        tries: int = -1,
    ):
        super().__init__()
        self._init_dt = datetime.now()
        self._timeout = timeout
        self._coro = coro
        self._status = TaskStatus.INIT
        self._id = uuid.uuid4()
        self._dependencies = dependencies

        self._start_at = start_at

        # При инициализации таски - проворачиваем ее один раз со значпением None,
        # т.е. инициализация
        p = Promise()
        p.set_result(None)
        self.set_result(None)

    @property
    def is_done(self):
        return True if self._status == TaskStatus.COMPLETE else False

    @property
    def id(self):
        return self._id

    @property
    def dependencies(self):
        return self._dependencies

    def awailable_to_run(self) -> bool:
        """ Проверяет, готова ли задача для выполнения """
        # TODO: Добавить проверку на саб-задачи
        return True if (datetime.now() - self._start_at).total_seconds() >= 0 else False

    def run_step(self, promise: Optional[Promise] = None):
        if self._timeout and (datetime.now() - self._init_dt) > self._timeout:
            self._coro.throw(TaskExecutionTimeout("Времф истекло"))

        res = promise.result if promise else None

        try:
            # результат пироворачивания генератора - общеание -
            # объект, содержащий результат выполения
            promise = self._coro.send(res)
        except StopIteration as e:
            logger.info(f"value: {e.value}")
            self.set_result(e.value)
            self._status = TaskStatus.COMPLETE
            return

        # добавляем в колбэк проворачивание последний раз - чтобы получить StopIteration
        # и из него взять результат
        # Убрал - работает
        # promise.add_done_callback(self.run_step)
