"""Schemas for coordinates."""

import typing as t
from annotated_types import Ge, Le
from src.models.schemas.common import CustomBaseModel


LatitudeType = t.Annotated[float, Ge(-90), Le(90)]
LongitudeType = t.Annotated[float, Ge(-180), Le(180)]


class GeoCorrdinates(CustomBaseModel):
    """Schema with geo coordinates."""

    lattitude: LatitudeType
    longitude: LongitudeType
