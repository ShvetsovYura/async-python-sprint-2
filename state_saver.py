from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
import types
from typing import Any

from uuid import UUID

from aio.promise import Promise


class EnhancedJsonEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, date):
            return o.strftime("%Y-%m-%d")
        if isinstance(o, Enum):
            return o.name
        if isinstance(o, types.GeneratorType):
            return o.__name__
        if isinstance(o, types.FunctionType):
            return o.__name__
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, timedelta):
            return o.total_seconds()
        if isinstance(o, Promise):
            return 'promise'
        return super().default(o)


class StateSaver:

    @staticmethod
    def save_task(task: 'Task'):
        with open('task_.json', 'w+') as t:
            json.dump(task.__dict__, t, cls=EnhancedJsonEncoder)


class StateDeserializer:

    @staticmethod
    def restore_task() -> 'Task':

        # как восстанавливать задачи - я так и не понял, ведь есть зависимости, статус корутин и т.д
        # как заставить это работаь - не вкурил
        # чатик и ментор слабо помогают в этом, если есть возможность - подскажите, я не против сделать, главное понять как
        pass
