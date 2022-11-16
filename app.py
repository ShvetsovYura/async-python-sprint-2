import asyncio
import json
import logging
import ssl
import sys
import time
from actions import RequestAction, SubtaskAction
from event_loop import EventLoop
from utils import coroutine, request
from task import Task
import urllib.request


def run_req(n: int):
    yield from asyncio.sleep(0)
    yield from request("https://code.s3.yandex.net/async-module/moscow-response.json", n)


def main():
    t0 = time.time()
    coros = [run_req(r) for r in range(10)]
    print('start while')
    while True:
        for coro in coros.copy():

            try:
                coro.send(None)
            except StopIteration:
                coros.remove(coro)
        if not coros:
            print(time.time() - t0)
            break


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


def do():
    logger.info("berfore yield")

    yield 1

    logger.info("after yield")


if __name__ == '__main__':

    logger.info("start app")
    ev = EventLoop()

    for i in range(2):

        ev.add_task(
            Task(action=RequestAction(),
                 dependencies=[
                     Task(action=SubtaskAction()),
                     Task(action=SubtaskAction()),
                     Task(action=SubtaskAction(), max_working_time=1)
                 ],
                 url="https://code.s3.yandex.net/async-module/moscow-response.json"))

    ev.run()

    # coros = [RequestJob().run() for _ in range(1)]

    # coro = RequestJob().run()
    # coro.send(None)
    # coro.send("https://code.s3.yandex.net/async-module/moscow-response.json")
    # while True:
    #     try:
    #         next(coro)
    #     except StopIteration as e:
    #         print(e.value)

    # while True:
    #     for coro in coros.copy():
    #         try:
    #             coro.send(None)
    #         except StopIteration:
    #             print('Stop ineration')
    #             coros.remove(coro)
