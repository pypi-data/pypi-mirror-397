# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LogprobsResultCandidateParam"]


class LogprobsResultCandidateParam(TypedDict, total=False):
    """Candidate for the logprobs token and score."""

    token: str
    """The candidate’s token string value."""

    log_probability: Annotated[float, PropertyInfo(alias="logProbability")]
    """The candidate's log probability."""

    token_id: Annotated[int, PropertyInfo(alias="tokenId")]
    """The candidate’s token id value."""
