# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .document import Document
from ...._models import BaseModel

__all__ = ["DocumentListResponse"]


class DocumentListResponse(BaseModel):
    """
    Response from `ListDocuments` containing a paginated list of `Document`s.
    The `Document`s are sorted by ascending `document.create_time`.
    """

    documents: Optional[List[Document]] = None
    """The returned `Document`s."""

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no more pages.
    """
