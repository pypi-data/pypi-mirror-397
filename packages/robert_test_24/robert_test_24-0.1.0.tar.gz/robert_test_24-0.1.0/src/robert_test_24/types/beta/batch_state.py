# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["BatchState"]

BatchState: TypeAlias = Literal[
    "BATCH_STATE_UNSPECIFIED",
    "BATCH_STATE_PENDING",
    "BATCH_STATE_RUNNING",
    "BATCH_STATE_SUCCEEDED",
    "BATCH_STATE_FAILED",
    "BATCH_STATE_CANCELLED",
    "BATCH_STATE_EXPIRED",
]
