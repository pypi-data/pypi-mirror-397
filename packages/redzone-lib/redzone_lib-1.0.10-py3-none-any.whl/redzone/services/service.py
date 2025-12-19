from microgue.asynchronous.services.service import Service as _Service

from ..utils.trace import Trace


class Service(_Service):
    mask_request_headers_fields: list = [
        "Authorization",
    ]

    class Request(_Service.Request):
        pass

    class Response(_Service.Response):
        pass

    async def invoke(self, request: _Service.Request) -> _Service.Response:
        request.headers["X-Trace-ID"] = Trace.get_trace_id()
        return await super().invoke(request)
