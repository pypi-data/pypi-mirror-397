# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .status import Status
from ..._models import BaseModel

__all__ = ["GeneratedFile"]


class GeneratedFile(BaseModel):
    """A file generated on behalf of a user."""

    error: Optional[Status] = None
    """
    The `Status` type defines a logical error model that is suitable for different
    programming environments, including REST APIs and RPC APIs. It is used by
    [gRPC](https://github.com/grpc). Each `Status` message contains three pieces of
    data: error code, error message, and error details.

    You can find out more about this error model and how to work with it in the
    [API Design Guide](https://cloud.google.com/apis/design/errors).
    """

    mime_type: Optional[str] = FieldInfo(alias="mimeType", default=None)
    """MIME type of the generatedFile."""

    name: Optional[str] = None
    """Identifier. The name of the generated file. Example: `generatedFiles/abc-123`"""

    state: Optional[Literal["STATE_UNSPECIFIED", "GENERATING", "GENERATED", "FAILED"]] = None
    """Output only. The state of the GeneratedFile."""
