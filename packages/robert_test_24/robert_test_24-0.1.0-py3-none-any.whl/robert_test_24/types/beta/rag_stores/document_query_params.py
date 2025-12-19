# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from ..metadata_filter_param import MetadataFilterParam

__all__ = ["DocumentQueryParams", "api_empty"]


class DocumentQueryParams(TypedDict, total=False):
    rag_store: Required[Annotated[str, PropertyInfo(alias="ragStore")]]

    query: Required[str]
    """Required. Query string to perform semantic search."""

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    metadata_filters: Annotated[Iterable[MetadataFilterParam], PropertyInfo(alias="metadataFilters")]
    """Optional.

    Filter for `Chunk` metadata. Each `MetadataFilter` object should correspond to a
    unique key. Multiple `MetadataFilter` objects are joined by logical "AND"s.

    Note: `Document`-level filtering is not supported for this request because a
    `Document` name is already specified.

    Example query: (year >= 2020 OR year < 2010) AND (genre = drama OR genre =
    action)

    `MetadataFilter` object list: metadata_filters = [ {key =
    "chunk.custom_metadata.year" conditions = [{int_value = 2020, operation =
    GREATER_EQUAL}, {int_value = 2010, operation = LESS}}, {key =
    "chunk.custom_metadata.genre" conditions = [{string_value = "drama", operation =
    EQUAL}, {string_value = "action", operation = EQUAL}}]

    Example query for a numeric range of values: (year > 2015 AND year <= 2020)

    `MetadataFilter` object list: metadata_filters = [ {key =
    "chunk.custom_metadata.year" conditions = [{int_value = 2015, operation =
    GREATER}]}, {key = "chunk.custom_metadata.year" conditions = [{int_value = 2020,
    operation = LESS_EQUAL}]}]

    Note: "AND"s for the same key are only supported for numeric values. String
    values only support "OR"s for the same key.
    """

    results_count: Annotated[int, PropertyInfo(alias="resultsCount")]
    """Optional.

    The maximum number of `Chunk`s to return. The service may return fewer `Chunk`s.

    If unspecified, at most 10 `Chunk`s will be returned. The maximum specified
    result count is 100.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
