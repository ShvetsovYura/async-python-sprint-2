from concurrent.futures import Future, ThreadPoolExecutor, as_completed
import json
from multiprocessing.pool import ThreadPool
import ssl
from threading import Lock
import time
from aio.event_loop import EventLoop
from aio.promise import Promise
from aio.task import Task
import urllib.request
import yaml
import logging.config
import logging

with open('log.yml') as stream:
    config = yaml.safe_load(stream)

    logging.config.dictConfig(config.get('logging'))

logger = logging.getLogger(__name__)


def get_event_loop():
    return EventLoop()


def t0():
    p = Promise()

    # yield p
    yield p
    return 't0'


# def t4():
#     p = Promise()

#     yield p
#     return 't4'


def t1():
    p = Promise()

    yield p
    return 't1'


def run_action(url: str):

    ssl._create_default_https_context = ssl._create_unverified_context

    response = None
    t0 = time.time()
    with urllib.request.urlopen(url) as req:

        response = req.read().decode('utf-8')
        response = json.loads(response)
        time.sleep(1)
        logger.info(f'request time: {time.time() - t0}')
        return response


pl = ThreadPool()


def get():
    p = Promise()

    def callback(f):
        # Если влкючить, то будет ValueError: generator already executing
        # наверно из-за того, что в while ниже уже yield-ится
        p.set_result(f)
        # logger.info(f"f: {f}")

    ar = pl.apply_async(run_action,
                        args=('https://jsonplaceholder.typicode.com/todos/1', ),
                        callback=callback)
    # не знаю, кмк по-другому заставить ждать выполнения зароса. Если не поставить, то выходит раньше, чем успевает получить реузльтат
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


# def main():
#     p = Promise()

#     r = yield from t2()
#     yield p
#     return 'end'

if __name__ == '__main__':
    logger.info(f'start: {time.time()}')
    time0 = time.time()
    get_event_loop().add_task(Task(coro=t0()))
    # get_event_loop().add_task(Task(coro=get()))
    # get_event_loop().add_task(Task(coro=get()))
    # get_event_loop().add_task(Task(coro=get()))

    get_event_loop().run()
    print(time.time() - time0)
    logger.info('end loop')
