# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["DocumentDeleteParams", "api_empty"]


class DocumentDeleteParams(TypedDict, total=False):
    rag_store: Required[Annotated[str, PropertyInfo(alias="ragStore")]]

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    force: bool
    """Optional.

    If set to true, any `Chunk`s and objects related to this `Document` will also be
    deleted.

    If false (the default), a `FAILED_PRECONDITION` error will be returned if
    `Document` contains any `Chunk`s.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
