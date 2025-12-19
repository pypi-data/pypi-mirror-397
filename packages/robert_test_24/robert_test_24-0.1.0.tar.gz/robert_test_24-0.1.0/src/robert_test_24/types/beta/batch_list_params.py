# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["BatchListParams", "api_empty"]


class BatchListParams(TypedDict, total=False):
    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    filter: str
    """The standard list filter."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """The standard list page size."""

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """The standard list page token."""

    return_partial_success: Annotated[bool, PropertyInfo(alias="returnPartialSuccess")]
    """
    When set to `true`, operations that are reachable are returned as normal, and
    those that are unreachable are returned in the
    [ListOperationsResponse.unreachable] field.

    This can only be `true` when reading across collections e.g. when `parent` is
    set to `"projects/example/locations/-"`.

    This field is not by default supported and will result in an `UNIMPLEMENTED`
    error if set unless explicitly documented otherwise in service or product
    specific documentation.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
