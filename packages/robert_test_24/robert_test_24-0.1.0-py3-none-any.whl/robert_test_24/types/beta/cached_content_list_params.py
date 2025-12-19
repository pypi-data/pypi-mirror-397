# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CachedContentListParams", "api_empty"]


class CachedContentListParams(TypedDict, total=False):
    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """Optional.

    The maximum number of cached contents to return. The service may return fewer
    than this value. If unspecified, some default (under maximum) number of items
    will be returned. The maximum value is 1000; values above 1000 will be coerced
    to 1000.
    """

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """Optional.

    A page token, received from a previous `ListCachedContents` call. Provide this
    to retrieve the subsequent page.

    When paginating, all other parameters provided to `ListCachedContents` must
    match the call that provided the page token.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
