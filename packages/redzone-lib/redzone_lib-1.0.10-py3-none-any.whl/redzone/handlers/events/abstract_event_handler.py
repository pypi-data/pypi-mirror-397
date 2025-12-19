from ...handlers.events.event import Event


class AbstractEventHandler:
    _event: Event

    def __init__(self, event: Event):
        self._event = event

    async def process(self) -> None:
        raise NotImplementedError
