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
    PAUSED = "PAUSED"
    COMPLETE = "COMPLETE"


class Task(Promise):

    def __init__(
        self,
        coro: Generator,
        start_at: datetime = datetime.now(),
        dependencies: list['Task'] = [],
        max_working_time: Optional[timedelta] = None,
        tries: int = -1,
    ):
        super().__init__()
        self._init_dt = datetime.now()
        self._start_dt: Optional[datetime] = None
        self._timeout = max_working_time
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
    def is_done(self) -> bool:
        return True if self._status == TaskStatus.COMPLETE else False

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def dependencies(self):
        return self._dependencies

    def _check_subtasks_is_done(self) -> bool:
        # если хотя бы одна из подзадач не готова - значит текущая таска не готова к работе
        for subtask in self._dependencies:
            if not subtask.is_done:
                return False
        return True

    @property
    def time_left_to_running(self) -> float:
        ''' Сколько времени осталось до запуска '''

        return (datetime.now() - self._start_at).total_seconds()

    @property
    def running_duration(self) -> timedelta:
        if not self._start_dt:
            return timedelta(seconds=0)

        return (datetime.now() - self._start_dt)

    def awailable_to_run(self) -> bool:
        """ Проверяет, готова ли задача для выполнения """

        if self.time_left_to_running >= 0 and self._check_subtasks_is_done():
            return True
        else:
            return False

    def pause(self) -> None:
        self._status = TaskStatus.PAUSED

    def stop(self) -> None:
        self._status = TaskStatus.COMPLETE

    def run_step(self, promise: Optional[Promise] = None) -> None:
        if not self._start_dt:
            self._start_dt = datetime.now()

        if self._timeout and self.running_duration > self._timeout:
            self._coro.throw(TaskExecutionTimeout("Время на выполнение задачи истекло"))

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
