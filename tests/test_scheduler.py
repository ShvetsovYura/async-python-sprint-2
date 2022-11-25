from unittest import TestCase

from aio.scheduler import Scheduler
from exceptions import NegativePoolSizeException, PoolSizeNotReducedException


class TestScheduler(TestCase):

    def setUp(self) -> None:

        self._sched = Scheduler()

    def test__increase_pool_size_to__success(self):
        self._sched.increase_pool_size_to(20)

        self.assertEqual(20, self._sched._pool_size)

    def test__increase_pool_size_to__reduce(self):
        self._sched.increase_pool_size_to(15)

        self.assertRaises(PoolSizeNotReducedException)

    def test__create__with_negative_pool_size(self):
        Scheduler(pool_size=-1)
        self.assertRaises(NegativePoolSizeException)
