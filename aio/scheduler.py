from enum import Enum
from aio.task import Task

from datetime import datetime
import time
from aio.task import Task

import threading

from exceptions import (NegativePoolSizeException, PoolOverflowException,
                        PoolSizeNotReducedException, TaskExecutionTimeout)


class SchedulerStatus(Enum):
    INIT = 'INIT'
    RUNING = 'RUNNING'
    PAUSED = 'PAUSED'


class SingletonType(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonType._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


class Scheduler(metaclass=SingletonType):

    def __init__(self, pool_size=3):
        if pool_size <= 0:
            raise NegativePoolSizeException()

        self._pool_size = pool_size
        self._status = SchedulerStatus.INIT
        self._tasks: list[Task] = []

    def increase_pool_size_to(self, new_pool_size: int) -> None:
        if new_pool_size < self._pool_size:
            raise PoolSizeNotReducedException()

        self._pool_size = new_pool_size

    def schedule_task(self, task: Task):
        if len(self._tasks) >= self._pool_size:
            raise PoolOverflowException()

        subtasks = self._unpack_subtaskstasks(task.dependencies)

        if sum([len(self._tasks), len(subtasks)]) > self._pool_size:
            raise PoolOverflowException()

        self._tasks.append(task)
        self._tasks.extend(subtasks)
        self._tasks.sort(key=lambda task: task._start_at, reverse=False)

    def _unpack_subtaskstasks(self, tasks: list[Task]):
        result = []
        for t in tasks:
            if len(t.dependencies) > 0:
                result.extend(self._unpack_subtaskstasks(t.dependencies))
            result.append(t)
        return result

    def run(self):
        self._status = SchedulerStatus.RUNING
        self._run_event_loop()

    def restart(self):
        pass

    def stop(self):
        self._status = SchedulerStatus.PAUSED

    def _run_event_loop(self):

        # важно смотреть на все задачи, а не только на те, которые готовы
        while self._tasks and self._status == SchedulerStatus.RUNING:
            tasks = self._tasks.copy()
            # фильтрация задач, которые уже должны быть исполнены
            tasks_ready_to_run = filter(lambda t: t.awailable_to_run(), self._tasks)
            # если есть задачи, которые должны быть выполнены - то yeld'имся по-ним
            # в противном случае - ждем (гасим поток) на время до первой ожидающей задачи
            # нужно не забывать, что при добавлении таска в очередь шедулера - они сотрируются
            # по возростанию планируемого времени выполнения
            if tasks_ready_to_run:
                for task in tasks_ready_to_run:
                    try:
                        task.run_step()
                    except TaskExecutionTimeout as e:
                        print(e)
                        self._tasks.remove(task)

                    if task.is_done:
                        self._tasks.remove(task)
            else:
                tm = (tasks[0]._start_at - datetime.now()).total_seconds()
                time.sleep(tm)


def get_scheduler():
    return Scheduler()
