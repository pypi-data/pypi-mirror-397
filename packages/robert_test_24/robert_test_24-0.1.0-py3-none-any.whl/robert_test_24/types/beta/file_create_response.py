# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .file import File
from ..._models import BaseModel

__all__ = ["FileCreateResponse"]


class FileCreateResponse(BaseModel):
    """Response for `CreateFile`."""

    file: Optional[File] = None
    """A file uploaded to the API. Next ID: 15"""
