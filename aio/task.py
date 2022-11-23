from enum import Enum
import logging
from typing import Callable, Generator, Optional
import uuid
from datetime import datetime, timedelta

from aio.promise import Promise
from exceptions import LimitAttemptsExhausted, TaskExecutionTimeout

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    INIT = "INIT"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETE = "COMPLETE"


class Task(Promise):

    def __init__(self,
                 coro: Callable,
                 start_at: datetime = datetime.now(),
                 dependencies: list['Task'] = [],
                 max_working_time: Optional[timedelta] = None,
                 tries: int = 0,
                 *args,
                 **kwargs):
        super().__init__()
        self._init_dt = datetime.now()
        self._start_dt: Optional[datetime] = None
        self._timeout = max_working_time

        self._args = args
        self._kwargs = kwargs

        # сохраняем корутину для создания новой если теущую задачу нужно перезапустить
        self._coro: Generator = coro(*self._args, **self._kwargs)
        self.__origin_coro = coro

        self._status = TaskStatus.INIT
        self._id = uuid.uuid4()
        self._dependencies = dependencies

        self._start_at = start_at

        self._tries = tries
        self._timeout_between_trying = timedelta(seconds=2.1)
        self._current_attempts = 0

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
                self._planning_trying_task()
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

    def __recreate_coro_from_origin(self):
        self._current_attempts += 1

        # если количество попыток исчерпалось - прибить корутину
        self._coro.close()
        # ...и создать новую из оригинальной
        self._coro = self.__origin_coro(*self._args, **self._kwargs)

    def _planning_trying_task(self):
        """
        Проверка на наличие доступных поптыок к задаче
        если есть попытки, то планируем эту задачу к запуску на отложенное время
        """

        if self._tries != -1 and self._current_attempts >= self._tries:
            raise LimitAttemptsExhausted(task_id=str(self._id))

        self._start_at += self._timeout_between_trying
        self.__recreate_coro_from_origin()

    def awailable_to_run(self) -> bool:
        """ Проверяет, готова ли задача для выполнения """

        if self.time_left_to_running >= 0 and self._check_subtasks_is_done():
            return True
        else:
            return False

    def pause(self) -> None:
        self._status = TaskStatus.PAUSED

    def stop(self) -> None:
        self._coro.close()
        self._status = TaskStatus.COMPLETE

    def run_step(self, promise: Optional[Promise] = None) -> None:

        self._status = TaskStatus.RUNNING
        # если время для запуска еще не наступило
        if not self._start_dt:
            self._start_dt = datetime.now()

        try:
            # если превышено вермя выполениня
            if self._timeout and self.running_duration > self._timeout:
                self._coro.throw(TaskExecutionTimeout("Время на выполнение задачи истекло"))

            res = promise.result if promise else None

            # результат пироворачивания генератора - общеание -
            # объект, содержащий результат выполения
            promise = self._coro.send(res)
        except StopIteration as e:
            logger.info(f"value: {e.value}")
            self.set_result(e.value)
            self._status = TaskStatus.COMPLETE
            return
        except TaskExecutionTimeout:
            self._planning_trying_task()
        except Exception:
            self._planning_trying_task()
