# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .content_param import ContentParam
from .tool_config_param import ToolConfigParam

__all__ = ["CachedContentUpdateParams", "api_empty"]


class CachedContentUpdateParams(TypedDict, total=False):
    model: Required[str]
    """Required.

    Immutable. The name of the `Model` to use for cached content Format:
    `models/{model}`
    """

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    update_mask: Annotated[str, PropertyInfo(alias="updateMask")]
    """The list of fields to update."""

    contents: Iterable[ContentParam]
    """Optional. Input only. Immutable. The content to cache."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Optional.

    Immutable. The user-generated meaningful display name of the cached content.
    Maximum 128 Unicode characters.
    """

    expire_time: Annotated[Union[str, datetime], PropertyInfo(alias="expireTime", format="iso8601")]
    """
    Timestamp in UTC of when this resource is considered expired. This is _always_
    provided on output, regardless of what was sent on input.
    """

    system_instruction: Annotated[ContentParam, PropertyInfo(alias="systemInstruction")]
    """The base structured datatype containing multi-part content of a message.

    A `Content` includes a `role` field designating the producer of the `Content`
    and a `parts` field containing multi-part data that contains the content of the
    message turn.
    """

    tool_config: Annotated[ToolConfigParam, PropertyInfo(alias="toolConfig")]
    """
    The Tool configuration containing parameters for specifying `Tool` use in the
    request.
    """

    tools: Iterable["ToolParam"]
    """Optional.

    Input only. Immutable. A list of `Tools` the model may use to generate the next
    response
    """

    ttl: str
    """Input only. New TTL for this resource, input only."""


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""


from .tool_param import ToolParam
