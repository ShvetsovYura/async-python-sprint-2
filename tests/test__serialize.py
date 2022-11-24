import unittest
import pickle
from aio.promise import Promise
from aio.task import Task


def coro_t():
    p = Promise()
    a = 1
    yield p
    b = a * 2
    yield p

    return p


class TestSerialize(unittest.TestCase):
    pass
    # def test__serilalize(self):
    #     t = Task(coro=coro_t)
    #     with open('ttt.pkl', 'wb') as p:
    #         pickle.dump(t, p)

    #     self.assertEqual(1, 1)

    # def test__deserialize(self):
    #     with open('ttt.pkl', 'r') as p:
    #         t = pickle.load(p)

    #     self.assertEqual(1, 1)
