# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from ..relevant_chunk import RelevantChunk

__all__ = ["DocumentQueryResponse"]


class DocumentQueryResponse(BaseModel):
    """Response from `QueryDocument` containing a list of relevant chunks."""

    relevant_chunks: Optional[List[RelevantChunk]] = FieldInfo(alias="relevantChunks", default=None)
    """The returned relevant chunks."""
