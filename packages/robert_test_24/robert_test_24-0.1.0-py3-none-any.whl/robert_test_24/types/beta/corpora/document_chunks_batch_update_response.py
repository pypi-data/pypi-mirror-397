# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .documents.chunk import Chunk

__all__ = ["DocumentChunksBatchUpdateResponse"]


class DocumentChunksBatchUpdateResponse(BaseModel):
    """Response from `BatchUpdateChunks` containing a list of updated `Chunk`s."""

    chunks: Optional[List[Chunk]] = None
    """`Chunk`s updated."""
