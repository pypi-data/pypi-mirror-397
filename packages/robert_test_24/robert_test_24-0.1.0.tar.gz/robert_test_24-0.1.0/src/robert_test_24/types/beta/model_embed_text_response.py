# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .embedding import Embedding

__all__ = ["ModelEmbedTextResponse"]


class ModelEmbedTextResponse(BaseModel):
    """The response to a EmbedTextRequest."""

    embedding: Optional[Embedding] = None
    """A list of floats representing the embedding."""
