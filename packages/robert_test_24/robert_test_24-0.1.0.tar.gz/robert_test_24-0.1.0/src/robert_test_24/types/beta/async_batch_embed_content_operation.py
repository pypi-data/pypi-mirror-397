# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .base_operation import BaseOperation
from .embed_content_batch import EmbedContentBatch
from .embed_content_batch_output import EmbedContentBatchOutput

__all__ = ["AsyncBatchEmbedContentOperation", "AsyncBatchEmbedContentOperationResponse"]


class AsyncBatchEmbedContentOperationResponse(BaseModel):
    """Response for a `BatchGenerateContent` operation."""

    output: Optional[EmbedContentBatchOutput] = None
    """The output of a batch request.

    This is returned in the `AsyncBatchEmbedContentResponse` or the
    `EmbedContentBatch.output` field.
    """


class AsyncBatchEmbedContentOperation(BaseOperation):
    """
    This resource represents a long-running operation where metadata and response fields are strongly typed.
    """

    metadata: Optional[EmbedContentBatch] = None
    """A resource representing a batch of `EmbedContent` requests."""

    response: Optional[AsyncBatchEmbedContentOperationResponse] = None
    """Response for a `BatchGenerateContent` operation."""
