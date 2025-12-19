import json
import traceback
from typing import Callable

import sentry_sdk

from .. import bootstrap  # noqa
from ..handlers.events.event import Event
from ..handlers.events.event_handler_factory import EventHandlerFactory, EventNotRegisteredError
from ..utils.logger import logger
from ..utils.trace import Trace


class EventsListenerCreator:
    @staticmethod
    def create(
        event_handlers: dict,
        use_database_connection: bool = False,
    ) -> Callable:
        async def async_handler(event, context):
            if use_database_connection:
                from ..utils.database import Database, ReplicaDatabase

                async with ReplicaDatabase().connection():
                    async with Database().connection():
                        async with Database.session.transaction():  # type: ignore
                            await EventsListenerCreator._create(event_handlers, event)
            else:
                await EventsListenerCreator._create(event_handlers, event)

        return async_handler

    @staticmethod
    async def _create(event_handlers: dict, event) -> None:
        for record in event["Records"]:
            try:
                Trace.start_trace(json.loads(record["body"]).get("detail", {}).get("trace_id", None))
                logger.debug("event_listener.handler - start", priority=1)

                # create event object from data
                event = Event.serialize(record)

                # process the event using the event handler factory
                await EventHandlerFactory(event_handlers).get_event_handler(event).process()

                logger.debug("event_listener.handler - end", priority=1)
            except EventNotRegisteredError as e:
                # log unrecognized events and allow the message to be removed from the queue
                logger.debug(str(e))
            except Exception as e:
                # log the error and let the message return to the queue
                sentry_sdk.capture_exception(e)
                sentry_sdk.flush(2)
                logger.debug("failed to process message", priority=1)
                logger.debug("{}: {}".format(e.__class__.__name__, e))
                logger.debug(traceback.format_exc())
                raise
