import json
import ssl

import urllib.request


def coroutine(func):

    def wrap(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.send(None)
        return gen

    return wrap


def request(url: str):

    ssl._create_default_https_context = ssl._create_unverified_context

    response = None
    with urllib.request.urlopen(url) as req:
        response = req.read().decode('utf-8')
        response = json.loads(response)

        return response
