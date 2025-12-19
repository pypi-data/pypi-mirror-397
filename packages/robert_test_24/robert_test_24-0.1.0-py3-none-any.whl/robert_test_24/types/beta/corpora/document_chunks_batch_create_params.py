# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .documents.chunk_param import ChunkParam

__all__ = ["DocumentChunksBatchCreateParams", "Request", "api_empty"]


class DocumentChunksBatchCreateParams(TypedDict, total=False):
    corpus: Required[str]

    requests: Required[Iterable[Request]]
    """Required.

    The request messages specifying the `Chunk`s to create. A maximum of 100
    `Chunk`s can be created in a batch.
    """

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""


class Request(TypedDict, total=False):
    """Request to create a `Chunk`."""

    chunk: Required[ChunkParam]
    """
    A `Chunk` is a subpart of a `Document` that is treated as an independent unit
    for the purposes of vector representation and storage.
    """

    parent: Required[str]
    """Required.

    The name of the `Document` where this `Chunk` will be created. Example:
    `corpora/my-corpus-123/documents/the-doc-abc`
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
