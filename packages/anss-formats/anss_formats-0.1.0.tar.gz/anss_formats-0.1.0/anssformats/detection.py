from typing import List, Literal, Optional

from pydantic import Field


from anssformats.formatbasemodel import CustomDT, FormatBaseModel
from anssformats.eventType import EventType
from anssformats.hypocenter import Hypocenter, HypocenterProperties
from anssformats.source import Source
from anssformats.pick import Pick
from anssformats.magnitude import Magnitude


class Detection(FormatBaseModel):
    """A conversion class used to create, parse, and validate detection data.

    type: string identifying this message as a detection

    id: string containing a unique identifier for this detection

    source: Source object containing the source of the detection

    hypocenter: Hypocenter object containing the hypocenter of the detection

    detectionType: optional string containing the origin type of this detection; valid
        values are "New", "Update", "Final", and "Retract"

    detectionTime: optional datetime containing the time this detection was made

    eventType: optional EventType object containing the event type of the detection

    minimumDistance: optional float containing the distance to the closest station

    rms: optional float containing the detection RMS

    maximumGap: optional float containing the detection gap

    detector: optional string containing the detection grid, algorithm, or other
        information

    pickData: optional list of either Pick objects used to generate
        this detection


    """

    type: Literal["Detection"]
    id: str
    source: Source

    hypocenter: Hypocenter

    detectionType: Optional[Literal["New", "Update", "Final", "Retract"]] = None
    detectionTime: Optional[CustomDT] = None

    eventType: Optional[EventType] = None

    minimumDistance: Optional[float] = Field(None, ge=0.0)
    rms: Optional[float] = None
    maximumGap: Optional[float] = Field(None, ge=0.0, le=360.0)

    detector: Optional[str] = None

    pickData: Optional[List[Pick]] = None

    magnitudeData: Optional[List[Magnitude]] = None
