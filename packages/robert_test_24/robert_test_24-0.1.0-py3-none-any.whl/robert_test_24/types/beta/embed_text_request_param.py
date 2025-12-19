# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["EmbedTextRequestParam"]


class EmbedTextRequestParam(TypedDict, total=False):
    """Request to get a text embedding from the model."""

    model: Required[str]
    """Required. The model name to use with the format model=models/{model}."""

    text: str
    """Optional. The free-form input text that the model will turn into an embedding."""
