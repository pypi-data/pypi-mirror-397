# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ContentFilter"]


class ContentFilter(BaseModel):
    """Content filtering metadata associated with processing a single request.

    ContentFilter contains a reason and an optional supporting string. The reason
    may be unspecified.
    """

    message: Optional[str] = None
    """A string that describes the filtering behavior in more detail."""

    reason: Optional[Literal["BLOCKED_REASON_UNSPECIFIED", "SAFETY", "OTHER"]] = None
    """The reason content was blocked during request processing."""
