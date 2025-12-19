# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo
from .embed_text_request_param import EmbedTextRequestParam

__all__ = ["ModelBatchEmbedTextParams", "api_empty"]


class ModelBatchEmbedTextParams(TypedDict, total=False):
    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    requests: Iterable[EmbedTextRequestParam]
    """Optional.

    Embed requests for the batch. Only one of `texts` or `requests` can be set.
    """

    texts: SequenceNotStr[str]
    """Optional.

    The free-form input texts that the model will turn into an embedding. The
    current limit is 100 texts, over which an error will be thrown.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
