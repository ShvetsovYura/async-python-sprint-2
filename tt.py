from typing import Any, Generator, Union


def gen_range(stop_value: int) -> Generator[Union[int, None], None, None]:
    stop_value = stop_value - 1
    current: int = -1
    param = yield
    while current < stop_value:
        current += 1
        yield current