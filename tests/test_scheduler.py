from unittest import TestCase

from aio.scheduler import Scheduler
from exceptions import NegativePoolSizeException, PoolSizeNotReducedException
from state_worker import StateWorker


class TestScheduler(TestCase):

    def setUp(self) -> None:
        state_worker = StateWorker()
        self._sched = Scheduler(state_worker=state_worker)

    def test_increase_pool_size_to_success(self):

        self._sched.increase_pool_size_to(20)

        self.assertEqual(20, self._sched._pool_size)

    def test_increase_pool_size_to_reduce(self):
        self._sched.increase_pool_size_to(15)

        self.assertRaises(PoolSizeNotReducedException)

    def test_create_with_negative_pool_size(self):
        with self.assertRaises(NegativePoolSizeException):
            Scheduler(pool_size=-1, state_worker=StateWorker())
