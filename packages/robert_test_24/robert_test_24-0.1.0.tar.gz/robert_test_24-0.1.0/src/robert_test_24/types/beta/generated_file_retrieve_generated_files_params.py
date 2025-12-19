# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["GeneratedFileRetrieveGeneratedFilesParams", "api_empty"]


class GeneratedFileRetrieveGeneratedFilesParams(TypedDict, total=False):
    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """Optional.

    Maximum number of `GeneratedFile`s to return per page. If unspecified, defaults
    to 10. Maximum `page_size` is 50.
    """

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """Optional. A page token from a previous `ListGeneratedFiles` call."""


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
