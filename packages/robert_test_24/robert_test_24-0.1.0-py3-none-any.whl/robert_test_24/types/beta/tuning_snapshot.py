# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TuningSnapshot"]


class TuningSnapshot(BaseModel):
    """Record for a single tuning step."""

    compute_time: Optional[datetime] = FieldInfo(alias="computeTime", default=None)
    """Output only. The timestamp when this metric was computed."""

    epoch: Optional[int] = None
    """Output only. The epoch this step was part of."""

    mean_loss: Optional[float] = FieldInfo(alias="meanLoss", default=None)
    """Output only. The mean loss of the training examples for this step."""

    step: Optional[int] = None
    """Output only. The tuning step."""
