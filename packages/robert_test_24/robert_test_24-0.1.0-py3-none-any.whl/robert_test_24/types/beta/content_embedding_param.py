# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import TypedDict

__all__ = ["ContentEmbeddingParam"]


class ContentEmbeddingParam(TypedDict, total=False):
    """A list of floats representing an embedding."""

    values: Iterable[float]
    """The embedding values."""
