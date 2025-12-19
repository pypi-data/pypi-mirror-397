# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo
from .candidate_param import CandidateParam
from .safety_rating_param import SafetyRatingParam

__all__ = ["GenerateContentResponseParam", "PromptFeedback"]


class PromptFeedback(TypedDict, total=False):
    """
    A set of the feedback metadata the prompt specified in
    `GenerateContentRequest.content`.
    """

    block_reason: Annotated[
        Literal["BLOCK_REASON_UNSPECIFIED", "SAFETY", "OTHER", "BLOCKLIST", "PROHIBITED_CONTENT", "IMAGE_SAFETY"],
        PropertyInfo(alias="blockReason"),
    ]
    """Optional.

    If set, the prompt was blocked and no candidates are returned. Rephrase the
    prompt.
    """

    safety_ratings: Annotated[Iterable[SafetyRatingParam], PropertyInfo(alias="safetyRatings")]
    """Ratings for safety of the prompt. There is at most one rating per category."""


class GenerateContentResponseParam(TypedDict, total=False):
    """Response from the model supporting multiple candidate responses.

    Safety ratings and content filtering are reported for both
    prompt in `GenerateContentResponse.prompt_feedback` and for each candidate
    in `finish_reason` and in `safety_ratings`. The API:
     - Returns either all requested candidates or none of them
     - Returns no candidates at all only if there was something wrong with the
       prompt (check `prompt_feedback`)
     - Reports feedback on each candidate in `finish_reason` and
       `safety_ratings`.
    """

    candidates: Iterable[CandidateParam]
    """Candidate responses from the model."""

    prompt_feedback: Annotated[PromptFeedback, PropertyInfo(alias="promptFeedback")]
    """
    A set of the feedback metadata the prompt specified in
    `GenerateContentRequest.content`.
    """
