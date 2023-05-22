from typing import Optional, Any
from pydantic import (
    BaseModel,
    conlist,
    Field,
)


class State(BaseModel):
    entity_id: str


class LightState(State):
    rgb_color: conlist(int, min_items=3, max_items=3) | None = None
    kelvin: Optional[int] | None = Field(default=None, description="color temperature in kelvin")
    brightness: Optional[int] | None = Field(default=None, title="brightness", ge=0, le=255)


class ClimateState(State):
    temperature: float = Field(default=None, title="temperature in celsius")


class ServiceField(BaseModel):
    name: str | None = None
    description: str | None = None
    required: bool = False
    example: Any | None = None


class Service(BaseModel):
    name: str
    description: str | None = None
    fields: dict[str, ServiceField]


class Domain(BaseModel):
    domain: str
    services: dict[str, Service]
