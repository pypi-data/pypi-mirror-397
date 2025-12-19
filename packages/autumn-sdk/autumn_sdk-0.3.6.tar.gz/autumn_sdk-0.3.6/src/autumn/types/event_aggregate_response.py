# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Union
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "EventAggregateResponse",
    "UnionMember0",
    "UnionMember0List",
    "UnionMember0Total",
    "UnionMember1",
    "UnionMember1List",
    "UnionMember1Total",
]


class UnionMember0List(BaseModel):
    period: float

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, float] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> float: ...
    else:
        __pydantic_extra__: Dict[str, float]


class UnionMember0Total(BaseModel):
    count: float

    sum: float


class UnionMember0(BaseModel):
    list: List[UnionMember0List]

    total: Dict[str, UnionMember0Total]


class UnionMember1List(BaseModel):
    period: float

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, Dict[str, float]] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> Dict[str, float]: ...
    else:
        __pydantic_extra__: Dict[str, Dict[str, float]]


class UnionMember1Total(BaseModel):
    count: float

    sum: float


class UnionMember1(BaseModel):
    list: List[UnionMember1List]

    total: Dict[str, UnionMember1Total]


EventAggregateResponse: TypeAlias = Union[UnionMember0, UnionMember1]
