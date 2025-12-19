# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from ..operation import Operation

__all__ = ["ListOperations"]


class ListOperations(BaseModel):
    """The response message for Operations.ListOperations."""

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """The standard List next-page token."""

    operations: Optional[List[Operation]] = None
    """A list of operations that matches the specified filter in the request."""

    unreachable: Optional[List[str]] = None
    """Unordered list.

    Unreachable resources. Populated when the request sets
    `ListOperationsRequest.return_partial_success` and reads across collections e.g.
    when attempting to list all resources across all supported locations.
    """
