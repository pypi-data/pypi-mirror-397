# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .batch_state import BatchState
from .embed_content_request import EmbedContentRequest
from .embed_content_batch_output import EmbedContentBatchOutput

__all__ = ["EmbedContentBatch", "InputConfig", "InputConfigRequests", "InputConfigRequestsRequest", "BatchStats"]


class InputConfigRequestsRequest(BaseModel):
    """The request to be processed in the batch."""

    request: EmbedContentRequest
    """Request containing the `Content` for the model to embed."""

    metadata: Optional[Dict[str, object]] = None
    """Optional. The metadata to be associated with the request."""


class InputConfigRequests(BaseModel):
    """
    The requests to be processed in the batch if provided as part of the
    batch creation request.
    """

    requests: List[InputConfigRequestsRequest]
    """Required. The requests to be processed in the batch."""


class InputConfig(BaseModel):
    """Configures the input to the batch request."""

    file_name: Optional[str] = FieldInfo(alias="fileName", default=None)
    """The name of the `File` containing the input requests."""

    requests: Optional[InputConfigRequests] = None
    """
    The requests to be processed in the batch if provided as part of the batch
    creation request.
    """


class BatchStats(BaseModel):
    """Stats about the batch."""

    failed_request_count: Optional[str] = FieldInfo(alias="failedRequestCount", default=None)
    """Output only. The number of requests that failed to be processed."""

    pending_request_count: Optional[str] = FieldInfo(alias="pendingRequestCount", default=None)
    """Output only. The number of requests that are still pending processing."""

    request_count: Optional[str] = FieldInfo(alias="requestCount", default=None)
    """Output only. The number of requests in the batch."""

    successful_request_count: Optional[str] = FieldInfo(alias="successfulRequestCount", default=None)
    """Output only. The number of requests that were successfully processed."""


class EmbedContentBatch(BaseModel):
    """A resource representing a batch of `EmbedContent` requests."""

    display_name: str = FieldInfo(alias="displayName")
    """Required. The user-defined name of this batch."""

    input_config: InputConfig = FieldInfo(alias="inputConfig")
    """Configures the input to the batch request."""

    model: str
    """Required. The name of the `Model` to use for generating the completion.

    Format: `models/{model}`.
    """

    batch_stats: Optional[BatchStats] = FieldInfo(alias="batchStats", default=None)
    """Stats about the batch."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """Output only. The time at which the batch was created."""

    end_time: Optional[datetime] = FieldInfo(alias="endTime", default=None)
    """Output only. The time at which the batch processing completed."""

    name: Optional[str] = None
    """Output only. Identifier. Resource name of the batch.

    Format: `batches/{batch_id}`.
    """

    output: Optional[EmbedContentBatchOutput] = None
    """The output of a batch request.

    This is returned in the `AsyncBatchEmbedContentResponse` or the
    `EmbedContentBatch.output` field.
    """

    priority: Optional[str] = None
    """Optional.

    The priority of the batch. Batches with a higher priority value will be
    processed before batches with a lower priority value. Negative values are
    allowed. Default is 0.
    """

    state: Optional[BatchState] = None
    """Output only. The state of the batch."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """Output only. The time at which the batch was last updated."""
