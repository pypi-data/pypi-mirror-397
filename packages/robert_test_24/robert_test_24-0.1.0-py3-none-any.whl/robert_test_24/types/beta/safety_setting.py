# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .harm_category import HarmCategory

__all__ = ["SafetySetting"]


class SafetySetting(BaseModel):
    """Safety setting, affecting the safety-blocking behavior.

    Passing a safety setting for a category changes the allowed probability that
    content is blocked.
    """

    category: HarmCategory
    """Required. The category for this setting."""

    threshold: Literal[
        "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
        "BLOCK_LOW_AND_ABOVE",
        "BLOCK_MEDIUM_AND_ABOVE",
        "BLOCK_ONLY_HIGH",
        "BLOCK_NONE",
        "OFF",
    ]
    """Required. Controls the probability threshold at which harm is blocked."""
