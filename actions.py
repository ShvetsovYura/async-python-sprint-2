from abc import ABC, abstractmethod
import json
import logging
import ssl
from typing import Any, Generator
import urllib.request

logger = logging.getLogger(__name__)


class Action(ABC):

    @abstractmethod
    def run_action(self, *args, **kwargs) -> Generator[None, None, Any]:
        pass


class RequestAction(Action):

    def run_action(self, url: str):
        ssl._create_default_https_context = ssl._create_unverified_context

        response = None
        yield
        logger.info("before request")
        with urllib.request.urlopen(url) as req:
            logger.info('step 1')
            yield
            response = req.read().decode('utf-8')
            logging.info('step 2')
            yield
            response: dict = json.loads(response)
            logging.info('step 3')
            yield

            return response


class SubtaskAction(Action):

    def run_action(self):
        logger.info("subtask step 1")
        result = yield from RequestAction().run_action(
            "https://code.s3.yandex.net/async-module/moscow-response.json")
        logger.info("subtask step 2")
        yield
        r = result.get('info')
        logger.info("subtask step 3")
        yield
        return r.get('tzinfo')
