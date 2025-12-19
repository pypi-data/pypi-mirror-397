# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .corpus import Corpus
from ..._models import BaseModel

__all__ = ["CorporaListResponse"]


class CorporaListResponse(BaseModel):
    """
    Response from `ListCorpora` containing a paginated list of `Corpora`.
    The results are sorted by ascending `corpus.create_time`.
    """

    corpora: Optional[List[Corpus]] = None
    """The returned corpora."""

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no more pages.
    """
