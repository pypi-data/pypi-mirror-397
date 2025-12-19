from pydantic import Field

from ..schemas.base_schemas import BaseResponse


class IndexResponse(BaseResponse):
    project: str = Field(examples=["core"])
    environment: str = Field(examples=["staging"])
    region: str = Field(examples=["us-east-1"])
    version: str = Field(examples=["0.1.0"])
    timestamp: str = Field(examples=["2021-10-01T00:00:00.000000"])
