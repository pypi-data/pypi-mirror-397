# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .message_prompt_param import MessagePromptParam

__all__ = ["ModelCountMessageTokensParams", "api_empty"]


class ModelCountMessageTokensParams(TypedDict, total=False):
    prompt: Required[MessagePromptParam]
    """All of the structured input text passed to the model as a prompt.

    A `MessagePrompt` contains a structured set of fields that provide context for
    the conversation, examples of user input/model output message pairs that prime
    the model to respond in different ways, and the conversation history or list of
    messages representing the alternating turns of the conversation between the user
    and the model.
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
