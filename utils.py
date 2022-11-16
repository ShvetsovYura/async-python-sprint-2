import asyncio

import json
import random
import ssl
from time import sleep
from typing import Any, Generator, Union
import urllib.request

from task import Task


def coroutine(func):

    def wrap(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.send(None)
        return gen

    return wrap


def request(url: str, num: int):
    ssl._create_default_https_context = ssl._create_unverified_context
    # url = yield
    response = None
    try:
        with urllib.request.urlopen(url) as req:
            yield None
            response = req.read().decode('utf-8')
            yield print(f"{num} - middle")
            response = json.loads(response)
            yield print(f"{num} - end")
            response = num

    except StopIteration:
        print('Stop iter')

    return response


d = {
    "name":
    "t1",
    "dep": [{
        "name": "t2",
        "dep": [{
            "name": 't3',
            "dep": []
        }, {
            "name": 't4',
            "dep": []
        }]
    }, {
        "name": 't5',
        "dep": []
    }],
}


def unpack_dependencies(t):
    if not t.get('dep'):
        return t

    for dep in t.get('dep'):
        unpack_dependencies(dep)


def flatten(lst: Union[list, int, str]) -> list:
    if not lst:
        return lst

    if isinstance(lst[0], list):
        return flatten(lst[0]) + flatten(lst[1:])

    return lst[:1] + flatten(lst[1:])


if __name__ == '__main__':
    flat = flatten([[1, 3, 4, ['a']], 11, 12, [], [[1, [2, [3]]]]])
    print(flat)
