# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

from ..._models import BaseModel
from .base_operation import BaseOperation
from .generate_content_batch_output import GenerateContentBatchOutput

__all__ = ["BatchGenerateContentOperation", "BatchGenerateContentOperationResponse"]


class BatchGenerateContentOperationResponse(BaseModel):
    """Response for a `BatchGenerateContent` operation."""

    output: Optional[GenerateContentBatchOutput] = None
    """The output of a batch request.

    This is returned in the `BatchGenerateContentResponse` or the
    `GenerateContentBatch.output` field.
    """


class BatchGenerateContentOperation(BaseOperation):
    """
    This resource represents a long-running operation where metadata and response fields are strongly typed.
    """

    metadata: Optional["GenerateContentBatch"] = None
    """A resource representing a batch of `GenerateContent` requests."""

    response: Optional[BatchGenerateContentOperationResponse] = None
    """Response for a `BatchGenerateContent` operation."""


from .generate_content_batch import GenerateContentBatch
