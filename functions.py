import logging
from pathlib import Path
from typing import Union

from exceptions import ArgumentNotPassed, IncorrentPathType

from utils import CITIES, request

logger = logging.getLogger(__name__)


def fetch_weather_forecast(city: str):
    if not city:
        raise ArgumentNotPassed()

    city_url = CITIES.get(city.upper())

    if not city_url:
        raise Exception("Такого города нет в списе")

    # Убрал работу с тредами (и колбеэками).
    # Но так код получается блокирующим, конечно.
    # Как сделать по-настоящему асинхронным запрос по http-
    # стандартными средствами - не понял и в этих ваших интернетах не нашел

    result = request(city_url)
    yield

    return result


def fetch_all_data():

    result1 = yield from fetch_weather_forecast(city="MOSCOW")
    yield None
    result2 = yield from fetch_weather_forecast(city="PARIS")

    return [result1, result2]


def calc_data():
    result = yield from fetch_all_data()
    return len(result)


def pipe():

    res = yield from calc_data()

    return res


def subtask():
    b = 1 + 1
    yield
    return b


def _check_path_type(path: Union[Path, str]) -> Path:

    if isinstance(path, Path):
        return path
    elif isinstance(path, str):
        return Path(path)
    else:
        raise IncorrentPathType()


def create_directory(path: Union[Path, str]):
    _path = _check_path_type(path)
    yield
    _path.mkdir(parents=True, exist_ok=True)
    yield
    return None


def create_file(path: Union[Path, str], filename: str):
    _path = _check_path_type(path)
    yield
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
