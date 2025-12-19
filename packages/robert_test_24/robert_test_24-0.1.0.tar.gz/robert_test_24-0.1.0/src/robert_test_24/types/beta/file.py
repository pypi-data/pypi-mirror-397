# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .status import Status
from ..._models import BaseModel

__all__ = ["File", "VideoMetadata"]


class VideoMetadata(BaseModel):
    """Metadata for a video `File`."""

    video_duration: Optional[str] = FieldInfo(alias="videoDuration", default=None)
    """Duration of the video."""


class File(BaseModel):
    """
    A file uploaded to the API.
    Next ID: 15
    """

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """Output only. The timestamp of when the `File` was created."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Optional.

    The human-readable display name for the `File`. The display name must be no more
    than 512 characters in length, including spaces. Example: "Welcome Image"
    """

    download_uri: Optional[str] = FieldInfo(alias="downloadUri", default=None)
    """Output only. The download uri of the `File`."""

    error: Optional[Status] = None
    """
    The `Status` type defines a logical error model that is suitable for different
    programming environments, including REST APIs and RPC APIs. It is used by
    [gRPC](https://github.com/grpc). Each `Status` message contains three pieces of
    data: error code, error message, and error details.

    You can find out more about this error model and how to work with it in the
    [API Design Guide](https://cloud.google.com/apis/design/errors).
    """

    expiration_time: Optional[datetime] = FieldInfo(alias="expirationTime", default=None)
    """Output only.

    The timestamp of when the `File` will be deleted. Only set if the `File` is
    scheduled to expire.
    """

    mime_type: Optional[str] = FieldInfo(alias="mimeType", default=None)
    """Output only. MIME type of the file."""

    name: Optional[str] = None
    """Immutable.

    Identifier. The `File` resource name. The ID (name excluding the "files/"
    prefix) can contain up to 40 characters that are lowercase alphanumeric or
    dashes (-). The ID cannot start or end with a dash. If the name is empty on
    create, a unique name will be generated. Example: `files/123-456`
    """

    sha256_hash: Optional[str] = FieldInfo(alias="sha256Hash", default=None)
    """Output only. SHA-256 hash of the uploaded bytes."""

    size_bytes: Optional[str] = FieldInfo(alias="sizeBytes", default=None)
    """Output only. Size of the file in bytes."""

    source: Optional[Literal["SOURCE_UNSPECIFIED", "UPLOADED", "GENERATED", "REGISTERED"]] = None
    """Source of the File."""

    state: Optional[Literal["STATE_UNSPECIFIED", "PROCESSING", "ACTIVE", "FAILED"]] = None
    """Output only. Processing state of the File."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """Output only. The timestamp of when the `File` was last updated."""

    uri: Optional[str] = None
    """Output only. The uri of the `File`."""

    video_metadata: Optional[VideoMetadata] = FieldInfo(alias="videoMetadata", default=None)
    """Metadata for a video `File`."""
