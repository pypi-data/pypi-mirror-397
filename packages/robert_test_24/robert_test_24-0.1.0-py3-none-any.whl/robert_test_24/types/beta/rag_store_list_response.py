# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .rag_store import RagStore

__all__ = ["RagStoreListResponse"]


class RagStoreListResponse(BaseModel):
    """Response from `ListRagStores` containing a paginated list of
    `RagStores`.

    The results are sorted by ascending `rag_store.create_time`.
    """

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no more pages.
    """

    rag_stores: Optional[List[RagStore]] = FieldInfo(alias="ragStores", default=None)
    """The returned rag_stores."""
