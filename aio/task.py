import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Generator, Optional

from aio.promise import Promise
from exceptions import LimitAttemptsExhausted, TaskExecutionTimeout
from state_saver import StateSaver

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    INIT = "INIT"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETE = "COMPLETE"


class Task:
    result = Promise()

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
        self._origin_coro = coro

        self._status = TaskStatus.INIT
        self._id = uuid.uuid4()
        self._dependencies = dependencies

        self._start_at = start_at

        self._tries = tries
        self._timeout_between_trying = timedelta(seconds=2.1)
        self._current_attempts = 0
        self._steps: list[Any] = []

        # При инициализации таски - проворачиваем ее один раз со значпением None,
        # т.е. инициализация

        self.result = None

    @property
    def is_done(self) -> bool:
        return True if self._status == TaskStatus.COMPLETE else False

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def dependencies(self):
        return self._dependencies

    def restart(self):
        self._recreate_coro_from_origin()

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

    def _recreate_coro_from_origin(self):

        # если количество попыток исчерпалось - прибить корутину
        self._coro.close()
        # ...и создать новую из оригинальной
        self._coro = self._origin_coro(*self._args, **self._kwargs)

    def _planning_trying_task(self):
        """
        Проверка на наличие доступных поптыок к задаче
        если есть попытки, то планируем эту задачу к запуску на отложенное время
        """

        if self._tries != -1 and self._current_attempts >= self._tries:
            raise LimitAttemptsExhausted()

        self._start_at += self._timeout_between_trying
        self._current_attempts += 1
        self._recreate_coro_from_origin()

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

    def run_step(self) -> None:

        self._status = TaskStatus.RUNNING
        # если время для запуска еще не наступило
        if not self._start_dt:
            self._start_dt = datetime.now()

        try:
            # если превышено вермя выполениня
            if self._timeout and self.running_duration > self._timeout:
                self._coro.throw(TaskExecutionTimeout())
            logger.debug(f"tid:{self.id} {self.result}")
            # результат пироворачивания генератора - общеание -
            # объект, содержащий результат выполения
            self.result = self._coro.send(self.result)

            # self._steps.append(self.result)
        except StopIteration as e:
            self.result = e.value
            logger.info(f"value tid:{self.id} = {self.result}")
            # self._steps.append(e.value)
            self._status = TaskStatus.COMPLETE
            StateSaver.save_task(self)
            return
        except TaskExecutionTimeout:
            self._planning_trying_task()

        except Exception as e:
            if hasattr(e, 'message'):
                logger.error(e.message)  # type: ignore
            else:
                logger.error(e)
            self._planning_trying_task()
