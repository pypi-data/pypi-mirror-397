# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .modality_token_count import ModalityTokenCount

__all__ = ["ModelCountTokensResponse"]


class ModelCountTokensResponse(BaseModel):
    """A response from `CountTokens`.

    It returns the model's `token_count` for the `prompt`.
    """

    cached_content_token_count: Optional[int] = FieldInfo(alias="cachedContentTokenCount", default=None)
    """Number of tokens in the cached part of the prompt (the cached content)."""

    cache_tokens_details: Optional[List[ModalityTokenCount]] = FieldInfo(alias="cacheTokensDetails", default=None)
    """Output only. List of modalities that were processed in the cached content."""

    prompt_tokens_details: Optional[List[ModalityTokenCount]] = FieldInfo(alias="promptTokensDetails", default=None)
    """Output only. List of modalities that were processed in the request input."""

    total_tokens: Optional[int] = FieldInfo(alias="totalTokens", default=None)
    """The number of tokens that the `Model` tokenizes the `prompt` into.

    Always non-negative.
    """
