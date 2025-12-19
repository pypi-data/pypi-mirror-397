# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import TypedDict

__all__ = ["StatusParam"]


class StatusParam(TypedDict, total=False):
    """
    The `Status` type defines a logical error model that is suitable for
    different programming environments, including REST APIs and RPC APIs. It is
    used by [gRPC](https://github.com/grpc). Each `Status` message contains
    three pieces of data: error code, error message, and error details.

    You can find out more about this error model and how to work with it in the
    [API Design Guide](https://cloud.google.com/apis/design/errors).
    """

    code: int
    """The status code, which should be an enum value of google.rpc.Code."""

    details: Iterable[Dict[str, object]]
    """A list of messages that carry the error details.

    There is a common set of message types for APIs to use.
    """

    message: str
    """A developer-facing error message, which should be in English.

    Any user-facing error message should be localized and sent in the
    google.rpc.Status.details field, or localized by the client.
    """
