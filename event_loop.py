from collections import deque
import logging
import time
from typing import Optional
from task import Task

logger = logging.getLogger(__name__)


class EventLoop:

    def __init__(self) -> None:
        self._queue: deque[Task] = deque()

    def add_task(self, task: Task):

        self._queue.append(task)
        t = task.dependencies
        if 
        self._queue.extend(task.dependencies)

    def _get_task(self) -> Optional[Task]:
        if not self._queue:
            return

        return self._queue.popleft()

    def run_task(self, task: Optional[Task]):

        if not task:
            return
        if task.complite:
            return
        result = task.run()
        self.add_task(task)

        return result

    def run(self):
        while True:
            task = self._get_task()
            if not task:
                time.sleep(.5)
                continue
            self.run_task(task)
            time.sleep(0.6)