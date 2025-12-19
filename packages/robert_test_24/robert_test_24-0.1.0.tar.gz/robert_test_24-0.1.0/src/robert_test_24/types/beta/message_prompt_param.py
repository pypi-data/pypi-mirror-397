# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .message_param import MessageParam

__all__ = ["MessagePromptParam", "Example"]


class Example(TypedDict, total=False):
    """An input/output example used to instruct the Model.

    It demonstrates how the model should respond or format its response.
    """

    input: Required[MessageParam]
    """The base unit of structured text.

    A `Message` includes an `author` and the `content` of the `Message`.

    The `author` is used to tag messages when they are fed to the model as text.
    """

    output: Required[MessageParam]
    """The base unit of structured text.

    A `Message` includes an `author` and the `content` of the `Message`.

    The `author` is used to tag messages when they are fed to the model as text.
    """


class MessagePromptParam(TypedDict, total=False):
    """All of the structured input text passed to the model as a prompt.

    A `MessagePrompt` contains a structured set of fields that provide context
    for the conversation, examples of user input/model output message pairs that
    prime the model to respond in different ways, and the conversation history
    or list of messages representing the alternating turns of the conversation
    between the user and the model.
    """

    messages: Required[Iterable[MessageParam]]
    """Required. A snapshot of the recent conversation history sorted chronologically.

    Turns alternate between two authors.

    If the total input size exceeds the model's `input_token_limit` the input will
    be truncated: The oldest items will be dropped from `messages`.
    """

    context: str
    """Optional.

    Text that should be provided to the model first to ground the response.

    If not empty, this `context` will be given to the model first before the
    `examples` and `messages`. When using a `context` be sure to provide it with
    every request to maintain continuity.

    This field can be a description of your prompt to the model to help provide
    context and guide the responses. Examples: "Translate the phrase from English to
    French." or "Given a statement, classify the sentiment as happy, sad or
    neutral."

    Anything included in this field will take precedence over message history if the
    total input size exceeds the model's `input_token_limit` and the input request
    is truncated.
    """

    examples: Iterable[Example]
    """Optional. Examples of what the model should generate.

    This includes both user input and the response that the model should emulate.

    These `examples` are treated identically to conversation messages except that
    they take precedence over the history in `messages`: If the total input size
    exceeds the model's `input_token_limit` the input will be truncated. Items will
    be dropped from `messages` before `examples`.
    """
