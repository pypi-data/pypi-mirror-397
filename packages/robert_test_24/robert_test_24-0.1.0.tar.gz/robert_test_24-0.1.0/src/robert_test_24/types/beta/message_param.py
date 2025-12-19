# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["MessageParam"]


class MessageParam(TypedDict, total=False):
    """The base unit of structured text.

    A `Message` includes an `author` and the `content` of
    the `Message`.

    The `author` is used to tag messages when they are fed to the
    model as text.
    """

    content: Required[str]
    """Required. The text content of the structured `Message`."""

    author: str
    """Optional. The author of this Message.

    This serves as a key for tagging the content of this Message when it is fed to
    the model as text.

    The author can be any alphanumeric string.
    """
