# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["CustomMetadata", "StringListValue"]


class StringListValue(BaseModel):
    """User provided string values assigned to a single metadata key."""

    values: Optional[List[str]] = None
    """The string values of the metadata to store."""


class CustomMetadata(BaseModel):
    """User provided metadata stored as key-value pairs."""

    key: str
    """Required. The key of the metadata to store."""

    numeric_value: Optional[float] = FieldInfo(alias="numericValue", default=None)
    """The numeric value of the metadata to store."""

    string_list_value: Optional[StringListValue] = FieldInfo(alias="stringListValue", default=None)
    """User provided string values assigned to a single metadata key."""

    string_value: Optional[str] = FieldInfo(alias="stringValue", default=None)
    """The string value of the metadata to store."""
