import logging
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Callable, Optional, Union
from aio.promise import Promise

from utils import request

pool = ThreadPool()

logger = logging.getLogger(__name__)


def fetch_weather_forecast(city: str):
    if not city:
        raise Exception("ytn")
    p = Promise()

    def callback(f):
        # Если включить, то будет ValueError: generator already executing
        # наверно из-за того, что в while ниже уже yield-ится
        p.set_result(f)

    ar = pool.apply_async(request,
                          args=('https://jsonplaceholder.typicode.com/todos/1', ),
                          callback=callback)

    # не знаю, кмк по-другому заставить ждать выполнения зароса. Если не поставить, то выходит
    # раньше, чем успевает получить реузльтат
    while not ar.ready():
        yield p

    return p.result


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
    with open(Path.joinpath(_path, filename), 'w') as file:
        pass


def move_file_or_dir(src: Union[Path, str], target: Union[Path, str]):
    _src = _check_path_type(src)
    _target = _check_path_type(target)
    # if not (_src.is_dir() and _target.is_dir()):
    #     raise Exception("One or more path is not dirs")

    _src.rename(_target)


def delete_file_or_dir(path: Union[Path, str]):
    path = _check_path_type(path)
    if path.is_dir():
        path.rmdir()

    if path.is_file():
        path.unlink()


def read_file_line_by_line(path: Union[Path, str]):
    pass
