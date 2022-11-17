from unittest import TestCase

from aio.task import Task, TaskStatus


class TestTask(TestCase):

    def _coro(self):
        yield 1
        return 2

    def test__subtasks_is_done__no_subtasks(self):

        t = Task(coro=self._coro())
        result = t._check_subtasks_is_done()

        self.assertEqual(True, result)

    def test__subtasks_is_done__not_done_subtasks(self):

        t = Task(coro=self._coro(), dependencies=[Task(coro=self._coro())])
        result = t._check_subtasks_is_done()

        self.assertEqual(False, result)

    def test__subtasks_is_done__one_not_done_subtasks(self):
        ''' Если хотя бы одна задача не выполнена '''

        done_subtask = Task(coro=self._coro())
        done_subtask._status == TaskStatus.COMPLETE
        t = Task(coro=self._coro(), dependencies=[Task(coro=self._coro())])
        result = t._check_subtasks_is_done()

        self.assertEqual(False, result)
