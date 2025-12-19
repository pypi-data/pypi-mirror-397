# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .candidate import Candidate
from .safety_rating import SafetyRating
from .modality_token_count import ModalityTokenCount

__all__ = ["GenerateContentResponse", "PromptFeedback", "UsageMetadata"]


class PromptFeedback(BaseModel):
    """
    A set of the feedback metadata the prompt specified in
    `GenerateContentRequest.content`.
    """

    block_reason: Optional[
        Literal["BLOCK_REASON_UNSPECIFIED", "SAFETY", "OTHER", "BLOCKLIST", "PROHIBITED_CONTENT", "IMAGE_SAFETY"]
    ] = FieldInfo(alias="blockReason", default=None)
    """Optional.

    If set, the prompt was blocked and no candidates are returned. Rephrase the
    prompt.
    """

    safety_ratings: Optional[List[SafetyRating]] = FieldInfo(alias="safetyRatings", default=None)
    """Ratings for safety of the prompt. There is at most one rating per category."""


class UsageMetadata(BaseModel):
    """Metadata on the generation request's token usage."""

    cached_content_token_count: Optional[int] = FieldInfo(alias="cachedContentTokenCount", default=None)
    """Number of tokens in the cached part of the prompt (the cached content)"""

    cache_tokens_details: Optional[List[ModalityTokenCount]] = FieldInfo(alias="cacheTokensDetails", default=None)
    """Output only. List of modalities of the cached content in the request input."""

    candidates_token_count: Optional[int] = FieldInfo(alias="candidatesTokenCount", default=None)
    """Total number of tokens across all the generated response candidates."""

    candidates_tokens_details: Optional[List[ModalityTokenCount]] = FieldInfo(
        alias="candidatesTokensDetails", default=None
    )
    """Output only. List of modalities that were returned in the response."""

    prompt_token_count: Optional[int] = FieldInfo(alias="promptTokenCount", default=None)
    """Number of tokens in the prompt.

    When `cached_content` is set, this is still the total effective prompt size
    meaning this includes the number of tokens in the cached content.
    """

    prompt_tokens_details: Optional[List[ModalityTokenCount]] = FieldInfo(alias="promptTokensDetails", default=None)
    """Output only. List of modalities that were processed in the request input."""

    thoughts_token_count: Optional[int] = FieldInfo(alias="thoughtsTokenCount", default=None)
    """Output only. Number of tokens of thoughts for thinking models."""

    tool_use_prompt_token_count: Optional[int] = FieldInfo(alias="toolUsePromptTokenCount", default=None)
    """Output only. Number of tokens present in tool-use prompt(s)."""

    tool_use_prompt_tokens_details: Optional[List[ModalityTokenCount]] = FieldInfo(
        alias="toolUsePromptTokensDetails", default=None
    )
    """Output only.

    List of modalities that were processed for tool-use request inputs.
    """

    total_token_count: Optional[int] = FieldInfo(alias="totalTokenCount", default=None)
    """Total token count for the generation request (prompt + response candidates)."""


class GenerateContentResponse(BaseModel):
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

    candidates: Optional[List[Candidate]] = None
    """Candidate responses from the model."""

    api_model_version: Optional[str] = FieldInfo(alias="modelVersion", default=None)
    """Output only. The model version used to generate the response."""

    prompt_feedback: Optional[PromptFeedback] = FieldInfo(alias="promptFeedback", default=None)
    """
    A set of the feedback metadata the prompt specified in
    `GenerateContentRequest.content`.
    """

    response_id: Optional[str] = FieldInfo(alias="responseId", default=None)
    """Output only. response_id is used to identify each response."""

    usage_metadata: Optional[UsageMetadata] = FieldInfo(alias="usageMetadata", default=None)
    """Metadata on the generation request's token usage."""
