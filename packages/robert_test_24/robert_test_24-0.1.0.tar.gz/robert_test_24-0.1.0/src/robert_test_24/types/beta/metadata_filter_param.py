# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["MetadataFilterParam", "Condition"]


class Condition(TypedDict, total=False):
    """Filter condition applicable to a single key."""

    operation: Required[
        Literal[
            "OPERATOR_UNSPECIFIED",
            "LESS",
            "LESS_EQUAL",
            "EQUAL",
            "GREATER_EQUAL",
            "GREATER",
            "NOT_EQUAL",
            "INCLUDES",
            "EXCLUDES",
        ]
    ]
    """Required.

    Operator applied to the given key-value pair to trigger the condition.
    """

    numeric_value: Annotated[float, PropertyInfo(alias="numericValue")]
    """The numeric value to filter the metadata on."""

    string_value: Annotated[str, PropertyInfo(alias="stringValue")]
    """The string value to filter the metadata on."""


class MetadataFilterParam(TypedDict, total=False):
    """
    User provided filter to limit retrieval based on `Chunk` or `Document` level
    metadata values.
    Example (genre = drama OR genre = action):
      key = "document.custom_metadata.genre"
      conditions = [{string_value = "drama", operation = EQUAL},
                    {string_value = "action", operation = EQUAL}]
    """

    conditions: Required[Iterable[Condition]]
    """Required.

    The `Condition`s for the given key that will trigger this filter. Multiple
    `Condition`s are joined by logical ORs.
    """

    key: Required[str]
    """Required. The key of the metadata to filter on."""
