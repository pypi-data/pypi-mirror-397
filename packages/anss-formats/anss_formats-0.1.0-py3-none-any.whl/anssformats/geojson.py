from typing import Optional, List, Literal

from pydantic import Field, field_validator, ValidationInfo
from anssformats.formatbasemodel import FormatBaseModel


class PointGeometry(FormatBaseModel):
    """A class holding a geojson point geometry

    type: string containing the type of this geometry

    coordinates: List of floats containing the longitude in degrees, latitude in degrees, and elevation in meters or depth in kilometers, in that order
    """

    type: str = "Point"
    coordinates: List[float]

    # check that coordinates are valid
    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(
        cls, value: List[float], info: ValidationInfo
    ) -> List[float]:
        if value is None:
            raise ValueError("Missing coordinates")

        if len(value) != 3:
            raise ValueError("Incomplete coordinates")

        # longitude
        if value[0] < -180.0 or value[0] > 180.0:
            raise ValueError("Longitude coordinate out of valid range")

        # latitude
        if value[1] < -90.0 or value[1] > 90.0:
            raise ValueError("Latitude coordinate out of valid range")

        # don't validate elevation/depth
        # value[2]

        return value
