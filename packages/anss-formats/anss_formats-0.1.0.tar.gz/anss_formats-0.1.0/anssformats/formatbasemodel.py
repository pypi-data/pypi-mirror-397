from datetime import datetime
from typing import Any

from pydantic import BaseModel, GetCoreSchemaHandler, field_validator
from pydantic_core import CoreSchema, core_schema


def convert_datetime_to_iso8601_with_z_suffix(dt: datetime) -> str:
    """Convert provided datetime to an ISO 8601 UTC time string

    Parameters
    ----------
    dt: Datetime containing the date time to convert

    Returns
    -------
    A str containing the ISO 8601 UTC formatted time string
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class FormatBaseModel(BaseModel):
    """A Pydantic BaseModel used for any required formatting of keys and values"""

    def model_dump(self):
        """Override the default model_dump method to always exclude None values"""
        return super().model_dump(exclude_none=True)

    def model_dump_json(self):
        """Override the default model_dump_json method to always exclude None values"""
        return super().model_dump_json(exclude_none=True)


class CustomDT(datetime):
    """A convenience class used to strip all datetime objects of timezone information,
    required to bypass Pydantic's automatic inclusion of timezone when parsing JSON
    strings.
    """

    @field_validator("*", mode="before")
    @classmethod
    def validate_no_tz(cls, v: Any, info: core_schema.ValidationInfo) -> Any:
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=None)
        return v.replace(tzinfo=None)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.with_info_before_validator_function(
            cls.validate_no_tz,
            handler(datetime),
            serialization=core_schema.plain_serializer_function_ser_schema(
                convert_datetime_to_iso8601_with_z_suffix,
                when_used="json-unless-none",
            ),
        )
