import logging
import time
from datetime import datetime

from aio.task import Task
from exceptions import (LimitAttemptsExhausted, NegativePoolSizeException,
                        PoolOverflowException, PoolSizeNotReducedException,
                        TaskExecutionTimeout)
from utils import RunningStatus

logger = logging.getLogger(__name__)


class Scheduler:

    def __init__(self, pool_size: int = 10):
        if pool_size <= 0:
            raise NegativePoolSizeException()

        self._pool_size: int = pool_size
        self._status: RunningStatus = RunningStatus.INIT
        self._tasks: list[Task] = []

    def increase_pool_size_to(self, new_pool_size: int) -> None:
        if new_pool_size < self._pool_size:
            raise PoolSizeNotReducedException()

        self._pool_size = new_pool_size

    def schedule_task(self, task: Task):
        """
        Добавление задачи в общий спасиок задач
        """

        subtasks: list[Task] = self._unpack_subtasks(task.dependencies)

        if sum([len(self._tasks), len(subtasks)]) > self._pool_size:
            raise PoolOverflowException()

        self._tasks.append(task)
        self._tasks.extend(subtasks)
        self._sort_tasks()

    def _sort_tasks(self) -> None:
        self._tasks.sort(key=lambda task: task._start_at, reverse=False)

    def _unpack_subtasks(self, tasks: list[Task]) -> list[Task]:
        """
        Рекурсивно распаковывает подзадачи текущей задачи
        и их подзадачи (и т.д.) в плоский список
        """
        result: list[Task] = []
        for task in tasks:
            if len(task.dependencies) > 0:
                result.extend(self._unpack_subtasks(task.dependencies))
            result.append(task)
        return result

    def run(self) -> None:
        logger.info("Запуск расписания")
        self._status = RunningStatus.RUNNING
        self._run_event_loop()

    def restart(self) -> None:
        for task in self._tasks:
            task.restart()

    def pause(self) -> None:
        self._status = RunningStatus.PAUSED

    def stop(self) -> None:
        for task in self._tasks.copy():
            task.stop()
            self._tasks.remove(task)

    def get_tasks_ready_to_run(self) -> list[Task]:

        # нужно, чтобы ослеживать те таски, которые ушли на следующий круг
        # например, задача выполнилась с ошибкой (или у нее есть незавершенные зависимости)
        # то в таком случее ее повторное выполение откладывается на установленный интервал
        # соответственно время следующего выполения сдвинется
        # именно по-этому нжно еще раз отсортировать список задач
        self._sort_tasks()

        # фильтрация задач, которые уже должны быть исполнены
        return list(filter(lambda t: t.awailable_to_run(), self._tasks.copy()))

    def _run_event_loop(self) -> None:

        # важно смотреть на все задачи, а не только на те, которые готовы
        while self._tasks and self._status == RunningStatus.RUNNING:
            tasks_ready_to_run: list[Task] = self.get_tasks_ready_to_run()
            # если есть задачи, которые должны быть выполнены - то yeld'имся по-ним
            # в противном случае - ждем (гасим поток) на время до первой ожидающей задачи
            # нужно не забывать, что при добавлении таска в очередь шедулера - они сортируются
            # по возростанию планируемого времени выполнения
            if tasks_ready_to_run:
                for task in tasks_ready_to_run:
                    try:
                        task.run_step()
                    except TaskExecutionTimeout as e:
                        logger.error(e)
                        task.stop()
                    except LimitAttemptsExhausted as e:
                        logger.error(e.message)
                        task.stop()

                    if task.is_done:
                        self._tasks.remove(task)
            else:
                tm: float = (self._tasks[0]._start_at - datetime.now()) \
                    .total_seconds()
                time.sleep(tm)
