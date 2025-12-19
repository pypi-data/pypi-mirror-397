# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["RagStoreListParams", "api_empty"]


class RagStoreListParams(TypedDict, total=False):
    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """Optional.

    The maximum number of `RagStores` to return (per page). The service may return
    fewer `RagStores`.

    If unspecified, at most 10 `RagStores` will be returned. The maximum size limit
    is 20 `RagStores` per page.
    """

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """Optional. A page token, received from a previous `ListRagStores` call.

    Provide the `next_page_token` returned in the response as an argument to the
    next request to retrieve the next page.

    When paginating, all other parameters provided to `ListRagStores` must match the
    call that provided the page token.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
