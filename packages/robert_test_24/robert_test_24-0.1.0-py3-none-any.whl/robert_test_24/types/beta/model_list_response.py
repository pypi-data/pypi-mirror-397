# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .model import Model
from ..._models import BaseModel

__all__ = ["ModelListResponse"]


class ModelListResponse(BaseModel):
    """Response from `ListModel` containing a paginated list of Models."""

    models: Optional[List[Model]] = None
    """The returned Models."""

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """A token, which can be sent as `page_token` to retrieve the next page.

    If this field is omitted, there are no more pages.
    """
