# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .candidate import Candidate
from .safety_rating import SafetyRating

__all__ = ["ModelGenerateAnswerResponse", "InputFeedback"]


class InputFeedback(BaseModel):
    """
    Feedback related to the input data used to answer the question, as opposed
    to the model-generated response to the question.
    """

    block_reason: Optional[Literal["BLOCK_REASON_UNSPECIFIED", "SAFETY", "OTHER"]] = FieldInfo(
        alias="blockReason", default=None
    )
    """Optional.

    If set, the input was blocked and no candidates are returned. Rephrase the
    input.
    """

    safety_ratings: Optional[List[SafetyRating]] = FieldInfo(alias="safetyRatings", default=None)
    """Ratings for safety of the input. There is at most one rating per category."""


class ModelGenerateAnswerResponse(BaseModel):
    """Response from the model for a grounded answer."""

    answer: Optional[Candidate] = None
    """A response candidate generated from the model."""

    answerable_probability: Optional[float] = FieldInfo(alias="answerableProbability", default=None)
    """Output only.

    The model's estimate of the probability that its answer is correct and grounded
    in the input passages.

    A low `answerable_probability` indicates that the answer might not be grounded
    in the sources.

    When `answerable_probability` is low, you may want to:

    - Display a message to the effect of "We couldn’t answer that question" to the
      user.
    - Fall back to a general-purpose LLM that answers the question from world
      knowledge. The threshold and nature of such fallbacks will depend on
      individual use cases. `0.5` is a good starting threshold.
    """

    input_feedback: Optional[InputFeedback] = FieldInfo(alias="inputFeedback", default=None)
    """
    Feedback related to the input data used to answer the question, as opposed to
    the model-generated response to the question.
    """
