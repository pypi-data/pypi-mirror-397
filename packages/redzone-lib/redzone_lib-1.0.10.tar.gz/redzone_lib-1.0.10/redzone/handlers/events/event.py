import json

from ...objects.base_object import BaseObject


class Event(BaseObject):
    source: str
    name: str
    data: dict

    @classmethod
    def serialize(cls, record: dict):  # type: ignore
        # get message from the sqs data
        message = json.loads(record["body"])

        return cls(
            **{
                "source": message.get("source"),
                "name": message.get("detail-type"),
                "data": message.get("detail"),
            },
        )
