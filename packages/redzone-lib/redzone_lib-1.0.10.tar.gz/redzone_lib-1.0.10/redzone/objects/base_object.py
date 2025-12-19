from datetime import datetime
from enum import Enum
from typing import TypeVar

from pydantic import BaseModel as Object

Object_ = TypeVar("Object_", bound=Object)


class BaseObject(Object):
    def json(self):
        json_data = self.model_dump().copy()

        # convert enums and datetime objects to strings
        for key, value in json_data.items():
            if isinstance(value, Enum):
                json_data[key] = value.value
            elif isinstance(value, datetime):
                json_data[key] = value.isoformat()

        return json_data
