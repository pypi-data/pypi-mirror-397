# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .file import File
from ..._models import BaseModel

__all__ = ["FileListResponse"]


class FileListResponse(BaseModel):
    """Response for `ListFiles`."""

    files: Optional[List[File]] = None
    """The list of `File`s."""

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """A token that can be sent as a `page_token` into a subsequent `ListFiles` call."""
