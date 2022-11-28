from unittest import TestCase

from aio.task import Task
from exceptions import LimitAttemptsExhausted
from utils import RunningStatus


class TestTask(TestCase):

    def _coro(self):
        yield 1
        return 2

    def _coro_exeption(self):
        yield 1
        raise Exception("Что-то пошло не так")
        return 2

    def test_subtasks_is_done_no_subtasks(self):

        t = Task(coro=self._coro)
        result = t._check_subtasks_is_done()

        self.assertEqual(True, result)

    def test_subtasks_is_done_not_done_subtasks(self):
        t = Task(coro=self._coro,
                 dependencies=[Task(coro=self._coro)],
                 tries=-1)
        result = t._check_subtasks_is_done()

        self.assertEqual(False, result)

    def test_subtasks_is_done_one_not_done_subtasks(self):
        ''' Если хотя бы одна задача не выполнена '''

        done_subtask = Task(coro=self._coro)
        done_subtask._status == RunningStatus.COMPLETE
        t = Task(coro=self._coro,
                 dependencies=[Task(coro=self._coro)],
                 tries=-1)
        result = t._check_subtasks_is_done()

        self.assertEqual(False, result)

    def test_unlimited_trying_task(self):
        """ Проверка бесконечного запуска таска """

        t = Task(coro=self._coro_exeption, tries=-1)
        for i in range(1000):
            t.run_step()

        self.assertEqual(RunningStatus.RUNNING, t._status)
        self.assertEqual(999, t._current_attempts)

    def test_zero_trying_task(self):
        t = Task(coro=self._coro_exeption, tries=0)
        t.run_step()

        self.assertRaises(LimitAttemptsExhausted)

    def test_once_trying_task(self):
        t = Task(coro=self._coro_exeption, tries=1)
        with self.assertRaises(LimitAttemptsExhausted):
            t.run_step()
            t.run_step()
            t.run_step()
            t.run_step()
