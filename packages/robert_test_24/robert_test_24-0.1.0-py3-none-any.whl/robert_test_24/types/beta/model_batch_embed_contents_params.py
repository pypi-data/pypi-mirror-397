# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .embed_content_request_param import EmbedContentRequestParam

__all__ = ["ModelBatchEmbedContentsParams", "api_empty"]


class ModelBatchEmbedContentsParams(TypedDict, total=False):
    requests: Required[Iterable[EmbedContentRequestParam]]
    """Required.

    Embed requests for the batch. The model in each of these requests must match the
    model specified `BatchEmbedContentsRequest.model`.
    """

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
