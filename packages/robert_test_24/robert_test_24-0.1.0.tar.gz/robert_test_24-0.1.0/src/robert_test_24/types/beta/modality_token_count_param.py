# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ModalityTokenCountParam"]


class ModalityTokenCountParam(TypedDict, total=False):
    """Represents token counting info for a single modality."""

    modality: Literal["MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "VIDEO", "AUDIO", "DOCUMENT"]
    """The modality associated with this token count."""

    token_count: Annotated[int, PropertyInfo(alias="tokenCount")]
    """Number of tokens."""
