# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["TextPromptParam"]


class TextPromptParam(TypedDict, total=False):
    """Text given to the model as a prompt.

    The Model will use this TextPrompt to Generate a text completion.
    """

    text: Required[str]
    """Required. The prompt text."""
