import logging
import random
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


def fetch_data(city: str):

    result = yield from fetch_weather_forecast(city)

    return result


def extract_data(city):
    result_by_city = yield from fetch_data(city)
    temps = []

    for forecast_by_date in result_by_city.get('forecasts'):
        _temps_by_date = [
            hour_forecast.get('temp')
            for hour_forecast in forecast_by_date.get('hours')
        ]
        yield
        temps.extend(_temps_by_date)
        yield
    return temps


def calc_data(city: str):
    temps_data = yield from extract_data(city)
    yield
    mean_temp = round(sum(temps_data) / len(temps_data))
    return mean_temp


def pipe_by_city(city: str):

    res = yield from calc_data(city)

    return res


def subtask():
    a = random.randint(1, 100)
    yield
    b = random.randint(1, 100)
    yield
    c = a + b

    return c


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
