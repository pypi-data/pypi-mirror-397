# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .embedding import Embedding

__all__ = ["ModelBatchEmbedTextResponse"]


class ModelBatchEmbedTextResponse(BaseModel):
    """The response to a EmbedTextRequest."""

    embeddings: Optional[List[Embedding]] = None
    """Output only. The embeddings generated from the input text."""
