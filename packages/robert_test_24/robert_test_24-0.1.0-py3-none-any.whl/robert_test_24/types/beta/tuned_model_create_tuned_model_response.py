# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .tuned_model import TunedModel
from .base_operation import BaseOperation
from .tuning_snapshot import TuningSnapshot

__all__ = ["TunedModelCreateTunedModelResponse", "TunedModelCreateTunedModelResponseMetadata"]


class TunedModelCreateTunedModelResponseMetadata(BaseModel):
    """
    Metadata about the state and progress of creating a tuned model returned from
    the long-running operation
    """

    completed_percent: Optional[float] = FieldInfo(alias="completedPercent", default=None)
    """The completed percentage for the tuning operation."""

    completed_steps: Optional[int] = FieldInfo(alias="completedSteps", default=None)
    """The number of steps completed."""

    snapshots: Optional[List[TuningSnapshot]] = None
    """Metrics collected during tuning."""

    total_steps: Optional[int] = FieldInfo(alias="totalSteps", default=None)
    """The total number of tuning steps."""

    tuned_model: Optional[str] = FieldInfo(alias="tunedModel", default=None)
    """Name of the tuned model associated with the tuning operation."""


class TunedModelCreateTunedModelResponse(BaseOperation):
    """
    This resource represents a long-running operation where metadata and response fields are strongly typed.
    """

    metadata: Optional[TunedModelCreateTunedModelResponseMetadata] = None
    """
    Metadata about the state and progress of creating a tuned model returned from
    the long-running operation
    """

    response: Optional[TunedModel] = None
    """A fine-tuned model created using ModelService.CreateTunedModel."""
