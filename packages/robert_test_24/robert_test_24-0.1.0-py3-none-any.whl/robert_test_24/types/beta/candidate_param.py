# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo
from .safety_rating_param import SafetyRatingParam

__all__ = ["CandidateParam"]


class CandidateParam(TypedDict, total=False):
    """A response candidate generated from the model."""

    safety_ratings: Annotated[Iterable[SafetyRatingParam], PropertyInfo(alias="safetyRatings")]
    """List of ratings for the safety of a response candidate.

    There is at most one rating per category.
    """
