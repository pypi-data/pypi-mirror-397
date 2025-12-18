from typing import Optional

from pydantic import Field

from anssformats.formatbasemodel import FormatBaseModel
from anssformats.source import Source


class Magnitude(FormatBaseModel):
    """A conversion class used to create, parse, and validate Magnitude data as part
    of detection data.

    Attributes
    ----------

    value: float containing the magnitude value

    type: string containing the magnitude type

    error: optional float containing the associated magnitude error (if any)

    probability: optional float containing the associated magnitude probability (if any)

    id: optional string containing a unique identifier for this magnitude

    source: optional Source object containing the source of the magnitude
    """

    value: float = Field(None, ge=-2.0, le=10.0)
    type: str

    error: Optional[float] = Field(None, ge=0.0)
    probability: Optional[float] = Field(None, ge=0.0, le=100.0)
    id: Optional[str] = None
    source: Optional[Source] = None
