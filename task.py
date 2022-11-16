from datetime import datetime, timedelta
import logging
from typing import Callable, Coroutine, Generator, Optional
import uuid

from actions import Action

logger = logging.getLogger(__name__)


class Task:

    def __init__(self,
                 action: Action,
                 start_at: Optional[datetime] = None,
                 max_working_time: Optional[int] = None,
                 tries=0,
                 dependencies: list['Task']=[],
                 *args,
                 **kwargs) -> None:
        self._id = uuid.uuid4()
        self._action_coro: Generator = action.run_action(*args, **kwargs)
        self._defer = datetime.now() + timedelta(milliseconds=1)
        self._complite = False
        self._start_at = start_at
        self._paused = False
        self._depends = dependencies
        self._start_task: Optional[datetime] = None
        self._max_working_time = max_working_time

    @property
    def complite(self):
        return self._complite

    @property
    def paused(self):
        return self._paused

    @property
    def dependencies(self):
        return self._depends

    def pause(is_enable=False) -> None:
        self._paused = is_enable

    def _check_depends_is_complite(self) -> bool:

        if [depend_task for depend_task in self._depends if not depend_task.complite]:
            return False
        return True

    def _check_timeout(self):
        # Проверка на то вышел ли таймаут выполнения задачи
        if self._start_task:
            if self._max_working_time and (datetime.now() -
                                           self._start_task).seconds > self._max_working_time:
                self._action_coro.close()

    def _check_start_at(self):
        now_ts = int(datetime.now().timestamp())
        if not self.complite and now_ts == self._start_at:
            return true

    def run(self):

        #  Сохранение времени начала выполения задачи
        if not self._start_task:
            self._start_task = datetime.now()

        try:
            self._check_timeout()

            if not self._check_depends_is_complite:
                logger.info('Есть незавершенные задачи')
                return

            if self._defer and self._defer > datetime.now():
                logger.info('earler')
                return

            if not self._paused:
                result = next(self._action_coro)
                print(result)
                return result

        except StopIteration as e:
            logger.info("End task %s", self._id)
            self._complite = True
            return e.value

        except GeneratorExit:
            logger.info("exit generator %s", self._id)
            return