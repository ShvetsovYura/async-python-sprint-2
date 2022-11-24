import logging
from multiprocessing.pool import ThreadPool
from pathlib import Path
from time import sleep
from typing import Union
from aio.promise import Promise

from utils import request

pool = ThreadPool()

logger = logging.getLogger(__name__)


def fetch_weather_forecast(city: str):
    if not city:
        raise Exception("Не указан параметр")
    p = Promise()

    def callback(f):
        # Если включить, то будет ValueError: generator already executing
        # наверно из-за того, что в while ниже уже yield-ится
        p.set_result(f)

    ar = pool.apply_async(request,
                          args=(f'https://jsonplaceholder.typicode.com/todos/{city}', ),
                          callback=callback)

    # не знаю, кмк по-другому заставить ждать выполнения зароса. Если не поставить, то выходит
    # раньше, чем успевает получить реузльтат
    while not ar.ready():
        yield p
        sleep(0.001)    # dirty hack

    return p.result


def fetch_all_data():

    result1 = yield from fetch_weather_forecast(city="1")
    result2 = yield from fetch_weather_forecast(city="2")

    return [result1, result2]


def calc_data():
    result = yield from fetch_all_data()
    return len(result)


def pipe():
    p = Promise()
    res = yield from calc_data()

    yield p
    return res


def subtask():
    p = Promise()
    b = 1 + 1
    yield p
    return b


def _check_path_type(path: Union[Path, str]) -> Path:

    if isinstance(path, Path):
        return path
    elif isinstance(path, str):
        return Path(path)
    else:
        raise Exception("Incorrect path type")


def create_directory(path: Union[Path, str]):
    p = Promise()
    _path = _check_path_type(path)
    yield p
    _path.mkdir(parents=True, exist_ok=True)
    yield p
    return p


def create_file(path: Union[Path, str], filename: str):
    p = Promise()
    _path = _check_path_type(path)
    yield p
    with open(Path.joinpath(_path, filename), 'w'):
        pass


def move_file_or_dir(src: Union[Path, str], target: Union[Path, str]):
    _src = _check_path_type(src)
    _target = _check_path_type(target)

    _src.rename(_target)


def delete_file_or_dir(path: Union[Path, str]):
    path = _check_path_type(path)
    if path.is_dir():
        path.rmdir()

    if path.is_file():
        path.unlink()


def read_file_line_by_line(path: Union[Path, str]):
    path = _check_path_type(path)
    if path.is_file():
        with open(path, 'r') as f:
            yield f.readline()
