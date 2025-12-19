# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .documents.chunk import Chunk

__all__ = ["DocumentChunksBatchCreateResponse"]


class DocumentChunksBatchCreateResponse(BaseModel):
    """Response from `BatchCreateChunks` containing a list of created `Chunk`s."""

    chunks: Optional[List[Chunk]] = None
    """`Chunk`s created."""
