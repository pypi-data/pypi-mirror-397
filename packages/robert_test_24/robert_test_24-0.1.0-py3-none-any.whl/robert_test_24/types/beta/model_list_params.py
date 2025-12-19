# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ModelListParams", "api_empty"]


class ModelListParams(TypedDict, total=False):
    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """The maximum number of `Models` to return (per page).

    If unspecified, 50 models will be returned per page. This method returns at most
    1000 models per page, even if you pass a larger page_size.
    """

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """A page token, received from a previous `ListModels` call.

    Provide the `page_token` returned by one request as an argument to the next
    request to retrieve the next page.

    When paginating, all other parameters provided to `ListModels` must match the
    call that provided the page token.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
