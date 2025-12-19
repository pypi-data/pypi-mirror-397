# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .content_embedding import ContentEmbedding

__all__ = ["ModelBatchEmbedContentsResponse"]


class ModelBatchEmbedContentsResponse(BaseModel):
    """The response to a `BatchEmbedContentsRequest`."""

    embeddings: Optional[List[ContentEmbedding]] = None
    """Output only.

    The embeddings for each request, in the same order as provided in the batch
    request.
    """
