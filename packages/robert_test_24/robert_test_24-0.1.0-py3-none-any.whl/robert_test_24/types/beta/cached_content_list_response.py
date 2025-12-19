# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["CachedContentListResponse"]


class CachedContentListResponse(BaseModel):
    """Response with CachedContents list."""

    cached_contents: Optional[List["CachedContent"]] = FieldInfo(alias="cachedContents", default=None)
    """List of cached contents."""

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """


from .cached_content import CachedContent
