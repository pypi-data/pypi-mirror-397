from typing import Optional, List, Literal

from pydantic import Field, field_validator, ValidationInfo
from anssformats.formatbasemodel import FormatBaseModel
from anssformats.geojson import PointGeometry


class ChannelProperties(FormatBaseModel):
    """A class holding the channel specific custom properties for a geojson point feature

    Station: string containing the station code

    Channel: optional string containing the channel code

    Network: string containing the network code

    Location: optional string containing the location code
    """

    station: str
    channel: Optional[str] = None
    network: str
    location: Optional[str] = None


class Channel(FormatBaseModel):
    """A conversion class used to create, parse, and validate geojson Channel data as part of
    detection data.

    type: string containing the type of this geojson

    geometry: PointGeometry object containing the geojson geometry for this feature

    properties: ChannelProperties object containing the channel properties
    """

    type: str = "Feature"

    geometry: PointGeometry
    properties: ChannelProperties
