from typing import Optional, List, Literal

from pydantic import Field, field_validator, ValidationInfo
from anssformats.formatbasemodel import CustomDT, FormatBaseModel
from anssformats.geojson import PointGeometry


class HypocenterProperties(FormatBaseModel):
    """A class holding the hypocenter specific custom properties for a geojson point feature

    originTime: required datetime containing the origin time of the hypocenter

    latitudeError: optional float containing the error of the latitude of this
        hypocenter in kilometers

    longitudeError: optional float containing the error of the longitude of this
        hypocenter in kilometers

    depthError: optional float containing the error of the depth of this hypocenter in
        kilometers

    timeError: optional float containing the error of the origin time of this hypocenter
        in seconds
    """

    originTime: CustomDT
    latitudeError: Optional[float] = None
    longitudeError: Optional[float] = None
    depthError: Optional[float] = None
    timeError: Optional[float] = None


class Hypocenter(FormatBaseModel):
    """A conversion class used to create, parse, and validate geojson Hypocenter data as part of
    detection data.

    type: string containing the type of this geojson

    geometry: PointGeometry object containing the geojson geometry for this feature

    properties: HypocenterProperties object containing the hypocenter properties
    """

    type: str = "Feature"

    geometry: PointGeometry
    properties: HypocenterProperties
