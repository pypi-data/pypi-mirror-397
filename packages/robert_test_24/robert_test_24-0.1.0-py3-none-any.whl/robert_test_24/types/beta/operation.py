# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .base_operation import BaseOperation

__all__ = ["Operation"]


class Operation(BaseOperation):
    """
    This resource represents a long-running operation that is the result of a
    network API call.
    """

    metadata: Optional[Dict[str, object]] = None
    """Service-specific metadata associated with the operation.

    It typically contains progress information and common metadata such as create
    time. Some services might not provide such metadata. Any method that returns a
    long-running operation should document the metadata type, if any.
    """

    response: Optional[Dict[str, object]] = None
    """The normal, successful response of the operation.

    If the original method returns no data on success, such as `Delete`, the
    response is `google.protobuf.Empty`. If the original method is standard
    `Get`/`Create`/`Update`, the response should be the resource. For other methods,
    the response should have the type `XxxResponse`, where `Xxx` is the original
    method name. For example, if the original method name is `TakeSnapshot()`, the
    inferred response type is `TakeSnapshotResponse`.
    """
