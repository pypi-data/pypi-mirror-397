# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["DocumentChunksBatchDeleteParams", "Request", "api_empty"]


class DocumentChunksBatchDeleteParams(TypedDict, total=False):
    corpus: Required[str]

    requests: Required[Iterable[Request]]
    """Required. The request messages specifying the `Chunk`s to delete."""

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""


class Request(TypedDict, total=False):
    """Request to delete a `Chunk`."""

    name: Required[str]
    """Required.

    The resource name of the `Chunk` to delete. Example:
    `corpora/my-corpus-123/documents/the-doc-abc/chunks/some-chunk`
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
