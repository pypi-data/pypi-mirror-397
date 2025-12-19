# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo
from .content_param import ContentParam

__all__ = ["ModelCountTokensParams", "api_empty"]


class ModelCountTokensParams(TypedDict, total=False):
    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    contents: Iterable[ContentParam]
    """Optional.

    The input given to the model as a prompt. This field is ignored when
    `generate_content_request` is set.
    """

    generate_content_request: Annotated["GenerateContentRequestParam", PropertyInfo(alias="generateContentRequest")]
    """Request to generate a completion from the model."""


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""


from .generate_content_request_param import GenerateContentRequestParam
