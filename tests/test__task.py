from unittest import TestCase

from aio.task import Task, TaskStatus
from exceptions import LimitAttemptsExhausted


class TestTask(TestCase):

    def _coro(self):
        yield 1
        return 2

    def _coro_exeption(self):
        yield 1
        raise Exception("Что-то пошло не так")
        return 2

    def test__subtasks_is_done__no_subtasks(self):

        t = Task(coro=self._coro)
        result = t._check_subtasks_is_done()

        self.assertEqual(True, result)

    def test__subtasks_is_done__not_done_subtasks(self):

        t = Task(coro=self._coro, dependencies=[Task(coro=self._coro)], tries=-1)
        result = t._check_subtasks_is_done()

        self.assertEqual(False, result)

    def test__subtasks_is_done__one_not_done_subtasks(self):
        ''' Если хотя бы одна задача не выполнена '''

        done_subtask = Task(coro=self._coro)
        done_subtask._status == TaskStatus.COMPLETE
        t = Task(coro=self._coro, dependencies=[Task(coro=self._coro)], tries=-1)
        result = t._check_subtasks_is_done()

        self.assertEqual(False, result)

    def test__unlimited_trying_task(self):
        """ Проверка бесконечного запуска таска """

        t = Task(coro=self._coro_exeption, tries=-1)
        for i in range(1000):
            t.run_step()

        self.assertEqual(TaskStatus.RUNNING, t._status)
        self.assertEqual(500, t._current_attempts)

    def test__zero_trying_task(self):
        t = Task(coro=self._coro_exeption, tries=0)
        t.run_step()

        self.assertRaises(LimitAttemptsExhausted)

    def test__once_trying_task(self):
        t = Task(coro=self._coro_exeption, tries=1)
        with self.assertRaises(LimitAttemptsExhausted):
            t.run_step()
            t.run_step()
            t.run_step()
            t.run_step()

        # self.assertRaises(LimitAttemptsExhausted)
