# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["CustomMetadataParam", "StringListValue"]


class StringListValue(TypedDict, total=False):
    """User provided string values assigned to a single metadata key."""

    values: SequenceNotStr[str]
    """The string values of the metadata to store."""


class CustomMetadataParam(TypedDict, total=False):
    """User provided metadata stored as key-value pairs."""

    key: Required[str]
    """Required. The key of the metadata to store."""

    numeric_value: Annotated[float, PropertyInfo(alias="numericValue")]
    """The numeric value of the metadata to store."""

    string_list_value: Annotated[StringListValue, PropertyInfo(alias="stringListValue")]
    """User provided string values assigned to a single metadata key."""

    string_value: Annotated[str, PropertyInfo(alias="stringValue")]
    """The string value of the metadata to store."""
