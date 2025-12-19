# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .status import Status
from ..._models import BaseModel

__all__ = ["BaseOperation"]


class BaseOperation(BaseModel):
    """
    This resource represents a long-running operation that is the result of a
    network API call.
    """

    done: Optional[bool] = None
    """
    If the value is `false`, it means the operation is still in progress. If `true`,
    the operation is completed, and either `error` or `response` is available.
    """

    error: Optional[Status] = None
    """
    The `Status` type defines a logical error model that is suitable for different
    programming environments, including REST APIs and RPC APIs. It is used by
    [gRPC](https://github.com/grpc). Each `Status` message contains three pieces of
    data: error code, error message, and error details.

    You can find out more about this error model and how to work with it in the
    [API Design Guide](https://cloud.google.com/apis/design/errors).
    """

    name: Optional[str] = None
    """
    The server-assigned name, which is only unique within the same service that
    originally returns it. If you use the default HTTP mapping, the `name` should be
    a resource name ending with `operations/{unique_id}`.
    """
