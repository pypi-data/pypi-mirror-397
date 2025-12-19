# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["TunedModelListTunedModelsParams", "api_empty"]


class TunedModelListTunedModelsParams(TypedDict, total=False):
    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    filter: str
    """Optional.

    A filter is a full text search over the tuned model's description and display
    name. By default, results will not include tuned models shared with everyone.

    Additional operators:

    - owner:me
    - writers:me
    - readers:me
    - readers:everyone

    Examples: "owner:me" returns all tuned models to which caller has owner role
    "readers:me" returns all tuned models to which caller has reader role
    "readers:everyone" returns all tuned models that are shared with everyone
    """

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """Optional.

    The maximum number of `TunedModels` to return (per page). The service may return
    fewer tuned models.

    If unspecified, at most 10 tuned models will be returned. This method returns at
    most 1000 models per page, even if you pass a larger page_size.
    """

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """Optional. A page token, received from a previous `ListTunedModels` call.

    Provide the `page_token` returned by one request as an argument to the next
    request to retrieve the next page.

    When paginating, all other parameters provided to `ListTunedModels` must match
    the call that provided the page token.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
