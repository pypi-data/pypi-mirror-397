# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .harm_category import HarmCategory

__all__ = ["SafetyRatingParam"]


class SafetyRatingParam(TypedDict, total=False):
    """Safety rating for a piece of content.

    The safety rating contains the category of harm and the
    harm probability level in that category for a piece of content.
    Content is classified for safety across a number of
    harm categories and the probability of the harm classification is included
    here.
    """

    category: Required[HarmCategory]
    """Required. The category for this rating."""

    probability: Required[Literal["HARM_PROBABILITY_UNSPECIFIED", "NEGLIGIBLE", "LOW", "MEDIUM", "HIGH"]]
    """Required. The probability of harm for this content."""

    blocked: bool
    """Was this content blocked because of this rating?"""
