# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .rag_stores.document import Document
from .corpora.documents.chunk import Chunk

__all__ = ["RelevantChunk"]


class RelevantChunk(BaseModel):
    """The information for a chunk relevant to a query."""

    chunk: Optional[Chunk] = None
    """
    A `Chunk` is a subpart of a `Document` that is treated as an independent unit
    for the purposes of vector representation and storage.
    """

    chunk_relevance_score: Optional[float] = FieldInfo(alias="chunkRelevanceScore", default=None)
    """`Chunk` relevance to the query."""

    document: Optional[Document] = None
    """A `Document` is a collection of `Chunk`s."""
