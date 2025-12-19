# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .relevant_chunk import RelevantChunk

__all__ = ["CorporaCorpusQueryResponse"]


class CorporaCorpusQueryResponse(BaseModel):
    """Response from `QueryCorpus` containing a list of relevant chunks."""

    relevant_chunks: Optional[List[RelevantChunk]] = FieldInfo(alias="relevantChunks", default=None)
    """The relevant chunks."""
