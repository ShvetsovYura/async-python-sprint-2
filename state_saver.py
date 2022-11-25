from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
import types
from typing import Any

from uuid import UUID


class EnhancedJsonEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:

        serialized_types = {
            date: o.strftime("%Y-%m-%d"),
            datetime: o.strftime("%Y-%m-%d %H:%M:%S"),
            Decimal: str(o),
            Enum: o.name,
            timedelta: o.total_seconds(),
            types.GeneratorType: o.__name__,
            types.FunctionType: o.__name__,
            UUID: str(o)
        }

        for _type in serialized_types:
            if isinstance(o, _type):
                return serialized_types[_type]
        return super().default(o)


class StateSaver:

    @staticmethod
    def save_task(task):
        with open('task_.json', 'w+') as t:
            json.dump(task.__dict__, t, cls=EnhancedJsonEncoder)


class StateDeserializer:

    @staticmethod
    def restore_task():

        # как восстанавливать задачи - я так и не понял, ведь есть зависимости,
        # статус корутин и т.д
        # как заставить это работаь - не вкурил
        # чатик и ментор слабо помогают в этом, если есть возможность - подскажите,
        # я не против сделать, главное понять как
        pass
