# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .content_embedding import ContentEmbedding

__all__ = ["EmbedContentResponse"]


class EmbedContentResponse(BaseModel):
    """The response to an `EmbedContentRequest`."""

    embedding: Optional[ContentEmbedding] = None
    """A list of floats representing an embedding."""
