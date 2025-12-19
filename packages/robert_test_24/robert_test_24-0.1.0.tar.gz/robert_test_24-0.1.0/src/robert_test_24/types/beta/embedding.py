# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["Embedding"]


class Embedding(BaseModel):
    """A list of floats representing the embedding."""

    value: Optional[List[float]] = None
    """The embedding values."""
