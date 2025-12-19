# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["ContentEmbedding"]


class ContentEmbedding(BaseModel):
    """A list of floats representing an embedding."""

    values: Optional[List[float]] = None
    """The embedding values."""
