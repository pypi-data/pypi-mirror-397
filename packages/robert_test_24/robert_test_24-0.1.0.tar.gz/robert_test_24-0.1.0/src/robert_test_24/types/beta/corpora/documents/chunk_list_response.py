# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .chunk import Chunk
from ....._models import BaseModel

__all__ = ["ChunkListResponse"]


class ChunkListResponse(BaseModel):
    """
    Response from `ListChunks` containing a paginated list of `Chunk`s.
    The `Chunk`s are sorted by ascending `chunk.create_time`.
    """

    chunks: Optional[List[Chunk]] = None
    """The returned `Chunk`s."""

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no more pages.
    """
