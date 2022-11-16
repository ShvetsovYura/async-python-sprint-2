from abc import ABC, abstractmethod
from datetime import datetime
import json
import logging
import ssl
from typing import Any, Generator, Optional

import urllib.request
from utils import request

logger = logging.getLogger(__name__)


class AbstractJob(ABC):

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class Job:

    def __init__(self, start_at="", max_working_time=-1, tries=0, dependencies=[]):
        pass

    def run(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass




class RequestJob(AbstractJob):

    def __init__(self, start_at: Optional[datetime] = None, max_working_time=-1, tries=0, dependencies=[]):
        self._task = Task(action=RequestAction(), url="https://code.s3.yandex.net/async-module/moscow-response.json")

    # @coroutine
    def run(self):
        url = yield
        req = request()
        req.send(None)
        req.send(url)
        while True:
            # try:
            next(req)
            # yield
        # except StopIteration as e:
        #     return e.value

    def pause(self):
        pass

    def stop(self):
        pass
