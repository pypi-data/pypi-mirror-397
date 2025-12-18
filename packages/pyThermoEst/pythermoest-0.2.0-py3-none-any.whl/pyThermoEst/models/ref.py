# import libs
from typing import Callable, TypedDict
from pydantic import BaseModel, Field

# NOTE: Quantity


class GroupUnit(BaseModel):
    """A class to represent a physical quantity with a value and unit."""
    value: float = Field(
        0,
        description="The numerical value of the quantity."
    )


class Eq(BaseModel):
    value: Callable[[float], float]
    unit: str
    symbol: str


class EstimatedProp(TypedDict):
    value: Callable[[float], float] | float | None
    unit: str
    symbol: str
