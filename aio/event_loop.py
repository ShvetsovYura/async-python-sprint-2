import time
from aio.promise import Promise
from aio.task import Task

import threading


class SingletonType(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonType._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


class EventLoop(metaclass=SingletonType):

    def __init__(self) -> None:
        self._tasks: list[Task] = []

    def add_task(self, task: Task):
        self._tasks.append(task)

    def run(self):

        while self._tasks:
            tasks = self._tasks.copy()
            for task in tasks:
                task.run_step()
                if task.is_done:
                    self._tasks.remove(task)
