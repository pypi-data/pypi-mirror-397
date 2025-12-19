# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .base_operation import BaseOperation

__all__ = [
    "ModelPredictLongRunningResponse",
    "ModelPredictLongRunningResponseResponse",
    "ModelPredictLongRunningResponseResponseGenerateVideoResponse",
    "ModelPredictLongRunningResponseResponseGenerateVideoResponseGeneratedSample",
    "ModelPredictLongRunningResponseResponseGenerateVideoResponseGeneratedSampleVideo",
]


class ModelPredictLongRunningResponseResponseGenerateVideoResponseGeneratedSampleVideo(BaseModel):
    """Representation of a video."""

    uri: Optional[str] = None
    """Path to another storage."""

    video: Optional[str] = None
    """Raw bytes."""


class ModelPredictLongRunningResponseResponseGenerateVideoResponseGeneratedSample(BaseModel):
    """A proto encapsulate various type of media."""

    video: Optional[ModelPredictLongRunningResponseResponseGenerateVideoResponseGeneratedSampleVideo] = None
    """Representation of a video."""


class ModelPredictLongRunningResponseResponseGenerateVideoResponse(BaseModel):
    """Veo response."""

    generated_samples: Optional[List[ModelPredictLongRunningResponseResponseGenerateVideoResponseGeneratedSample]] = (
        FieldInfo(alias="generatedSamples", default=None)
    )
    """The generated samples."""

    rai_media_filtered_count: Optional[int] = FieldInfo(alias="raiMediaFilteredCount", default=None)
    """Returns if any videos were filtered due to RAI policies."""

    rai_media_filtered_reasons: Optional[List[str]] = FieldInfo(alias="raiMediaFilteredReasons", default=None)
    """Returns rai failure reasons if any."""


class ModelPredictLongRunningResponseResponse(BaseModel):
    """Response message for [PredictionService.PredictLongRunning]"""

    generate_video_response: Optional[ModelPredictLongRunningResponseResponseGenerateVideoResponse] = FieldInfo(
        alias="generateVideoResponse", default=None
    )
    """Veo response."""


class ModelPredictLongRunningResponse(BaseOperation):
    """
    This resource represents a long-running operation where metadata and response fields are strongly typed.
    """

    metadata: Optional[object] = None
    """Metadata for PredictLongRunning long running operations."""

    response: Optional[ModelPredictLongRunningResponseResponse] = None
    """Response message for [PredictionService.PredictLongRunning]"""
