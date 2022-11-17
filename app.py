from datetime import datetime, timedelta
from multiprocessing.pool import ThreadPool
import time
from typing import Callable
from aio.promise import Promise
from aio.scheduler import get_scheduler
from aio.task import Task
import yaml
import logging.config
import logging

from utils import request

with open('log.yml') as stream:
    config = yaml.safe_load(stream)

    logging.config.dictConfig(config.get('logging'))

logger = logging.getLogger(__name__)


def t0():

    p = Promise()

    # yield p
    yield p
    return 't0'


# def t4():
#     p = Promise()

#     yield p
#     return 't4'


def task(func: Callable):

    def wraper(*args, **kwargs):
        p = Promise()
        result = func(*args, **kwargs)
        yield p
        return result

    return wraper


@task
def t1():
    return 't1'


pool = ThreadPool()


def get():
    p = Promise()

    def callback(f):
        # Если включить, то будет ValueError: generator already executing
        # наверно из-за того, что в while ниже уже yield-ится
        p.set_result(f)

        # logger.info(f"f: {f}")

    ar = pool.apply_async(request,
                          args=('https://jsonplaceholder.typicode.com/todos/1', ),
                          callback=callback)

    # не знаю, кмк по-другому заставить ждать выполнения зароса. Если не поставить, то выходит
    # раньше, чем успевает получить реузльтат
    while not ar.ready():
        yield p

    return p.result


def t2():
    p = Promise()

    res = yield from t0()
    logger.info(f"res: {res}")
    ugu = yield from get()
    logger.info(f'ugu:{ugu}')
    res1 = yield from t1()
    logger.info(f'res1: {res1}')
    yield p
    return ugu


if __name__ == '__main__':
    logger.info(f'start: {time.time()}')
    time0 = time.time()
    get_scheduler().schedule_task(
        Task(coro=get(),
             start_at=datetime.now() + timedelta(seconds=3),
             max_working_time=timedelta(seconds=10),
             dependencies=[Task(coro=t0()), Task(coro=t0()),
                           Task(coro=t0())]))
    get_scheduler().schedule_task(Task(coro=t2()))
    # get_event_loop().add_task(Task(coro=get()))
    # get_event_loop().add_task(Task(coro=get()))
    # get_event_loop().add_task(Task(coro=get()))

    get_scheduler().run()
    print(time.time() - time0)
    pool.close()
    pool.join()
    logger.info('end loop')
