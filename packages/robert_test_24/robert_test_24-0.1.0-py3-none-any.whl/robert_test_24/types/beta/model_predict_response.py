# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["ModelPredictResponse"]


class ModelPredictResponse(BaseModel):
    """Response message for [PredictionService.Predict]."""

    predictions: Optional[List[object]] = None
    """The outputs of the prediction call."""
