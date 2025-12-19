# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["PermissionListPermissionsParams", "api_empty"]


class PermissionListPermissionsParams(TypedDict, total=False):
    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """Optional.

    The maximum number of `Permission`s to return (per page). The service may return
    fewer permissions.

    If unspecified, at most 10 permissions will be returned. This method returns at
    most 1000 permissions per page, even if you pass larger page_size.
    """

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """Optional. A page token, received from a previous `ListPermissions` call.

    Provide the `page_token` returned by one request as an argument to the next
    request to retrieve the next page.

    When paginating, all other parameters provided to `ListPermissions` must match
    the call that provided the page token.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
