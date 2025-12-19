# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .documents.chunk_param import ChunkParam

__all__ = ["DocumentChunksBatchUpdateParams", "Request", "api_empty"]


class DocumentChunksBatchUpdateParams(TypedDict, total=False):
    corpus: Required[str]

    requests: Required[Iterable[Request]]
    """Required.

    The request messages specifying the `Chunk`s to update. A maximum of 100
    `Chunk`s can be updated in a batch.
    """

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""


class Request(TypedDict, total=False):
    """Request to update a `Chunk`."""

    chunk: Required[ChunkParam]
    """
    A `Chunk` is a subpart of a `Document` that is treated as an independent unit
    for the purposes of vector representation and storage.
    """

    update_mask: Required[Annotated[str, PropertyInfo(alias="updateMask")]]
    """Required.

    The list of fields to update. Currently, this only supports updating
    `custom_metadata` and `data`.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
