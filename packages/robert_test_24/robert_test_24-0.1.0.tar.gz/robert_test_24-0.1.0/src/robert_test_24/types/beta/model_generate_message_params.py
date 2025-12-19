# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .message_prompt_param import MessagePromptParam

__all__ = ["ModelGenerateMessageParams", "api_empty"]


class ModelGenerateMessageParams(TypedDict, total=False):
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

    candidate_count: Annotated[int, PropertyInfo(alias="candidateCount")]
    """Optional. The number of generated response messages to return.

    This value must be between `[1, 8]`, inclusive. If unset, this will default to
    `1`.
    """

    temperature: float
    """Optional. Controls the randomness of the output.

    Values can range over `[0.0,1.0]`, inclusive. A value closer to `1.0` will
    produce responses that are more varied, while a value closer to `0.0` will
    typically result in less surprising responses from the model.
    """

    top_k: Annotated[int, PropertyInfo(alias="topK")]
    """Optional. The maximum number of tokens to consider when sampling.

    The model uses combined Top-k and nucleus sampling.

    Top-k sampling considers the set of `top_k` most probable tokens.
    """

    top_p: Annotated[float, PropertyInfo(alias="topP")]
    """Optional.

    The maximum cumulative probability of tokens to consider when sampling.

    The model uses combined Top-k and nucleus sampling.

    Nucleus sampling considers the smallest set of tokens whose probability sum is
    at least `top_p`.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
