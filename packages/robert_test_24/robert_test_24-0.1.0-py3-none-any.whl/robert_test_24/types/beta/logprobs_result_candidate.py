# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["LogprobsResultCandidate"]


class LogprobsResultCandidate(BaseModel):
    """Candidate for the logprobs token and score."""

    token: Optional[str] = None
    """The candidate’s token string value."""

    log_probability: Optional[float] = FieldInfo(alias="logProbability", default=None)
    """The candidate's log probability."""

    token_id: Optional[int] = FieldInfo(alias="tokenId", default=None)
    """The candidate’s token id value."""
