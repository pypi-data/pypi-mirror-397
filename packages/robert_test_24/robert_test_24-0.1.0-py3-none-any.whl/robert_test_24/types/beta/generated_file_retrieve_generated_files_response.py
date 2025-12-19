# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .generated_file import GeneratedFile

__all__ = ["GeneratedFileRetrieveGeneratedFilesResponse"]


class GeneratedFileRetrieveGeneratedFilesResponse(BaseModel):
    """Response for `ListGeneratedFiles`."""

    generated_files: Optional[List[GeneratedFile]] = FieldInfo(alias="generatedFiles", default=None)
    """The list of `GeneratedFile`s."""

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token that can be sent as a `page_token` into a subsequent
    `ListGeneratedFiles` call.
    """
