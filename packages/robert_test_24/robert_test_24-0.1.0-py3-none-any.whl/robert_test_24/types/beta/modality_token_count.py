# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ModalityTokenCount"]


class ModalityTokenCount(BaseModel):
    """Represents token counting info for a single modality."""

    modality: Optional[Literal["MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "VIDEO", "AUDIO", "DOCUMENT"]] = None
    """The modality associated with this token count."""

    token_count: Optional[int] = FieldInfo(alias="tokenCount", default=None)
    """Number of tokens."""
