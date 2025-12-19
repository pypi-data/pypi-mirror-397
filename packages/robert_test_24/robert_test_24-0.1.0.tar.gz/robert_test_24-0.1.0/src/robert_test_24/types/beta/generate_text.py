# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .safety_rating import SafetyRating
from .content_filter import ContentFilter
from .safety_setting import SafetySetting
from .citation_metadata import CitationMetadata

__all__ = ["GenerateText", "Candidate", "SafetyFeedback"]


class Candidate(BaseModel):
    """Output text returned from a model."""

    citation_metadata: Optional[CitationMetadata] = FieldInfo(alias="citationMetadata", default=None)
    """A collection of source attributions for a piece of content."""

    output: Optional[str] = None
    """Output only. The generated text returned from the model."""

    safety_ratings: Optional[List[SafetyRating]] = FieldInfo(alias="safetyRatings", default=None)
    """Ratings for the safety of a response.

    There is at most one rating per category.
    """


class SafetyFeedback(BaseModel):
    """Safety feedback for an entire request.

    This field is populated if content in the input and/or response is blocked
    due to safety settings. SafetyFeedback may not exist for every HarmCategory.
    Each SafetyFeedback will return the safety settings used by the request as
    well as the lowest HarmProbability that should be allowed in order to return
    a result.
    """

    rating: Optional[SafetyRating] = None
    """Safety rating for a piece of content.

    The safety rating contains the category of harm and the harm probability level
    in that category for a piece of content. Content is classified for safety across
    a number of harm categories and the probability of the harm classification is
    included here.
    """

    setting: Optional[SafetySetting] = None
    """Safety setting, affecting the safety-blocking behavior.

    Passing a safety setting for a category changes the allowed probability that
    content is blocked.
    """


class GenerateText(BaseModel):
    """The response from the model, including candidate completions."""

    candidates: Optional[List[Candidate]] = None
    """Candidate responses from the model."""

    filters: Optional[List[ContentFilter]] = None
    """A set of content filtering metadata for the prompt and response text.

    This indicates which `SafetyCategory`(s) blocked a candidate from this response,
    the lowest `HarmProbability` that triggered a block, and the HarmThreshold
    setting for that category. This indicates the smallest change to the
    `SafetySettings` that would be necessary to unblock at least 1 response.

    The blocking is configured by the `SafetySettings` in the request (or the
    default `SafetySettings` of the API).
    """

    safety_feedback: Optional[List[SafetyFeedback]] = FieldInfo(alias="safetyFeedback", default=None)
    """Returns any safety feedback related to content filtering."""
