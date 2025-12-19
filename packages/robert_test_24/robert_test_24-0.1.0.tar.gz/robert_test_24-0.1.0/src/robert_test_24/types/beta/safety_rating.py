# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .harm_category import HarmCategory

__all__ = ["SafetyRating"]


class SafetyRating(BaseModel):
    """Safety rating for a piece of content.

    The safety rating contains the category of harm and the
    harm probability level in that category for a piece of content.
    Content is classified for safety across a number of
    harm categories and the probability of the harm classification is included
    here.
    """

    category: HarmCategory
    """Required. The category for this rating."""

    probability: Literal["HARM_PROBABILITY_UNSPECIFIED", "NEGLIGIBLE", "LOW", "MEDIUM", "HIGH"]
    """Required. The probability of harm for this content."""

    blocked: Optional[bool] = None
    """Was this content blocked because of this rating?"""
