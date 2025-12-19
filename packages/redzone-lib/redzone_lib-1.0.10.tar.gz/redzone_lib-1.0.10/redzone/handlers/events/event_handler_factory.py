from ...handlers.events.abstract_event_handler import AbstractEventHandler
from ...handlers.events.event import Event
from ...utils.logger import logger


class EventNotRegisteredError(Exception):
    pass


class EventHandlerFactory:
    """
    This is used to build EventHandler objects based on the event name
    """

    __event_handlers: dict = {}

    def __init__(self, event_handlers: dict) -> None:
        # register the event source and event name to the event handlers
        self.__event_handlers = event_handlers

    def get_event_handler(self, event: Event) -> AbstractEventHandler:
        logger.debug(f"{self.__class__.__name__}.get_event_handler", priority=2)
        try:
            registered_event = f"{event.source}.{event.name}"
            logger.debug(f"event_handler: {self.__event_handlers[registered_event].__name__}")
            logger.debug(f"event_source: {event.source}")
            logger.debug(f"event_name: {event.name}")
            event_handler = self.__event_handlers[registered_event]
            return event_handler(event)
        except KeyError:
            raise EventNotRegisteredError(f"event not registered with: {self.__class__.__name__}")
