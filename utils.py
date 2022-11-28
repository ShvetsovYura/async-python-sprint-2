import json
import logging.config
import ssl
import urllib.request
from enum import Enum
from urllib.error import HTTPError, URLError

import yaml

from exceptions import DataFetchingException

CITIES = {
    "MOSCOW": "https://code.s3.yandex.net/async-module/moscow-response.json",
    "PARIS": "https://code.s3.yandex.net/async-module/paris-response.json",
    "LONDON": "https://code.s3.yandex.net/async-module/london-response.json",
    "BERLIN": "https://code.s3.yandex.net/async-module/berlin-response.json",
    "BEIJING": "https://code.s3.yandex.net/async-module/beijing-response.json",
    "KAZAN": "https://code.s3.yandex.net/async-module/kazan-response.json",
    "SPETERSBURG":
    "https://code.s3.yandex.net/async-module/spetersburg-response.json",
    "VOLGOGRAD":
    "https://code.s3.yandex.net/async-module/volgograd-response.json",
    "NOVOSIBIRSK":
    "https://code.s3.yandex.net/async-module/novosibirsk-response.json",
    "KALININGRAD":
    "https://code.s3.yandex.net/async-module/kaliningrad-response.json",
    "ABUDHABI":
    "https://code.s3.yandex.net/async-module/abudhabi-response.json",
    "WARSZAWA":
    "https://code.s3.yandex.net/async-module/warszawa-response.json",
    "BUCHAREST":
    "https://code.s3.yandex.net/async-module/bucharest-response.json",
    "ROMA": "https://code.s3.yandex.net/async-module/roma-response.json",
    "CAIRO": "https://code.s3.yandex.net/async-module/cairo-response.json",
}


def coroutine(func):

    def wrap(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.send(None)
        return gen

    return wrap


def request(url: str):

    ssl._create_default_https_context = ssl._create_unverified_context

    response = None
    try:
        with urllib.request.urlopen(url) as req:
            response = req.read().decode('utf-8')
            response = json.loads(response)

            return response
    except HTTPError:
        raise DataFetchingException()
    except URLError:
        raise DataFetchingException()
    except ConnectionResetError:
        raise DataFetchingException()


def setup_log_config():
    with open('log-config.yml') as stream:
        config = yaml.safe_load(stream)

        logging.config.dictConfig(config.get('logging'))


class RunningStatus(Enum):
    INIT = 'INIT'
    RUNNING = 'RUNNING'
    PAUSED = 'PAUSED'
    COMPLETE = "COMPLETE"
    STOP_PENDING = "STOP_PENDING"
