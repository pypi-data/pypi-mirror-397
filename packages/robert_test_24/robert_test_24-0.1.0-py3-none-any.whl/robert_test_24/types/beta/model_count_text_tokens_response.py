# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ModelCountTextTokensResponse"]


class ModelCountTextTokensResponse(BaseModel):
    """A response from `CountTextTokens`.

    It returns the model's `token_count` for the `prompt`.
    """

    token_count: Optional[int] = FieldInfo(alias="tokenCount", default=None)
    """The number of tokens that the `model` tokenizes the `prompt` into.

    Always non-negative.
    """
