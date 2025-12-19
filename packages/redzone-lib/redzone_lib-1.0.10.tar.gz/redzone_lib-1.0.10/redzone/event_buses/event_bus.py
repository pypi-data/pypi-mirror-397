from microgue.asynchronous.events.abstract_event_bus import AbstractEventBus

from ..settings import EVENT_BUS_NAME, PROJECT_NAME, REGION
from ..utils.trace import Trace


class EventBus(AbstractEventBus):
    event_bus_name = EVENT_BUS_NAME
    event_bus_region = REGION
    event_source = PROJECT_NAME

    async def publish(self, event_type: str, event_data: dict | None = None) -> bool:
        event_data = event_data or {}
        event_data["trace_id"] = Trace.get_trace_id()
        return await super().publish(event_type, event_data)
