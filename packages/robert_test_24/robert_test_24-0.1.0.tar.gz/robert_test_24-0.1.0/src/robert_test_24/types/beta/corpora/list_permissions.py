# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .permission import Permission

__all__ = ["ListPermissions"]


class ListPermissions(BaseModel):
    """
    Response from `ListPermissions` containing a paginated list of
    permissions.
    """

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """A token, which can be sent as `page_token` to retrieve the next page.

    If this field is omitted, there are no more pages.
    """

    permissions: Optional[List[Permission]] = None
    """Returned permissions."""
