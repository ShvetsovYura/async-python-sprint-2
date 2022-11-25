import json
import pickle
import types
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID


class EnhancedJsonEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:

        serialized_types = {
            date: lambda: o.strftime("%Y-%m-%d"),
            datetime: lambda: o.strftime("%Y-%m-%d %H:%M:%S"),
            Decimal: lambda: str(o),
            Enum: lambda: o.name,
            timedelta: lambda: o.total_seconds(),
            types.GeneratorType: lambda: o.__name__,
            types.FunctionType: lambda: o.__name__,
            UUID: lambda: str(o)
        }

        for _type in serialized_types:
            if isinstance(o, _type):
                return serialized_types[_type]()
        return super().default(o)


class StateSaver:

    @staticmethod
    def save_task(task):
        bt = pickle.dumps(task, protocol=5)
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
