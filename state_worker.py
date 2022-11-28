import json
import os
import pickle
import types
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID

from aio.task import Task


class EnhancedJsonEncoder(json.JSONEncoder):

    def default(self, serialized_object: Any) -> Any:

        serialized_types = {
            date: lambda: serialized_object.strftime("%Y-%m-%d"),
            datetime: lambda: serialized_object.strftime("%Y-%m-%d %H:%M:%S"),
            Decimal: lambda: str(serialized_object),
            Enum: lambda: serialized_object.name,
            timedelta: lambda: serialized_object.total_seconds(),
            types.GeneratorType: lambda: serialized_object.__name__,
            types.FunctionType: lambda: serialized_object.__name__,
            UUID: lambda: str(serialized_object)
        }

        for _type in serialized_types:
            if isinstance(serialized_object, _type):
                return serialized_types[_type]()
        return super().default(serialized_object)


class StateWorker:

    def save_tasks(self, tasks: list[Task]):
        for pending_task in tasks.copy():
            with open(f'cached_tasks/{str(pending_task.id)}', 'wb+') as stream:
                pending_task._coro = None
                for d in pending_task._dependencies.copy():
                    d._coro = None

                pickle.dump(pending_task, stream)

    def restore_tasks(self) -> list[Task]:
        tasks = []

        path = Path(__file__).resolve().parent / 'cached_tasks'
        if not path.exists():
            path.mkdir()

        with os.scandir(path) as entities:
            for ent in entities:
                if ent.is_file():
                    with open(ent, 'rb') as stream:
                        tt = pickle.load(stream)
                        tasks.append(tt)

        return tasks


class StateDeserializer:

    @staticmethod
    def restore_task():
        pass
