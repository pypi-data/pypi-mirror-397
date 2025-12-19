# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CorporaUpdateParams", "api_empty"]


class CorporaUpdateParams(TypedDict, total=False):
    update_mask: Required[Annotated[str, PropertyInfo(alias="updateMask")]]
    """Required.

    The list of fields to update. Currently, this only supports updating
    `display_name`.
    """

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Optional.

    The human-readable display name for the `Corpus`. The display name must be no
    more than 512 characters in length, including spaces. Example: "Docs on Semantic
    Retriever"
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
