# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ....._utils import PropertyInfo
from ...custom_metadata_param import CustomMetadataParam

__all__ = ["ChunkUpdateParams", "Data", "api_empty"]


class ChunkUpdateParams(TypedDict, total=False):
    corpus: Required[str]

    document: Required[str]

    update_mask: Required[Annotated[str, PropertyInfo(alias="updateMask")]]
    """Required.

    The list of fields to update. Currently, this only supports updating
    `custom_metadata` and `data`.
    """

    data: Required[Data]
    """Extracted data that represents the `Chunk` content."""

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    custom_metadata: Annotated[Iterable[CustomMetadataParam], PropertyInfo(alias="customMetadata")]
    """Optional.

    User provided custom metadata stored as key-value pairs. The maximum number of
    `CustomMetadata` per chunk is 20.
    """

    name: str
    """Immutable.

    Identifier. The `Chunk` resource name. The ID (name excluding the
    "corpora/_/documents/_/chunks/" prefix) can contain up to 40 characters that are
    lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If
    the name is empty on create, a random 12-character unique ID will be generated.
    Example: `corpora/{corpus_id}/documents/{document_id}/chunks/123a456b789c`
    """


class Data(TypedDict, total=False):
    """Extracted data that represents the `Chunk` content."""

    string_value: Annotated[str, PropertyInfo(alias="stringValue")]
    """
    The `Chunk` content as a string. The maximum number of tokens per chunk is 2043.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
