# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from ..custom_metadata import CustomMetadata

__all__ = ["Document"]


class Document(BaseModel):
    """A `Document` is a collection of `Chunk`s."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """Output only. The Timestamp of when the `Document` was created."""

    custom_metadata: Optional[List[CustomMetadata]] = FieldInfo(alias="customMetadata", default=None)
    """Optional.

    User provided custom metadata stored as key-value pairs used for querying. A
    `Document` can have a maximum of 20 `CustomMetadata`.
    """

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Optional.

    The human-readable display name for the `Document`. The display name must be no
    more than 512 characters in length, including spaces. Example: "Semantic
    Retriever Documentation"
    """

    mime_type: Optional[str] = FieldInfo(alias="mimeType", default=None)
    """Output only. The mime type of the Document."""

    name: Optional[str] = None
    """Immutable.

    Identifier. The `Document` resource name. The ID (name excluding the
    "ragStores/\\**/documents/" prefix) can contain up to 40 characters that are
    lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If
    the name is empty on create, a unique name will be derived from `display_name`
    along with a 12 character random suffix. Example:
    `ragStores/{corpus_id}/documents/my-awesome-doc-123a456b789c`
    """

    size_bytes: Optional[str] = FieldInfo(alias="sizeBytes", default=None)
    """Output only. The size of raw bytes ingested into the Document."""

    state: Optional[Literal["STATE_UNSPECIFIED", "STATE_PENDING", "STATE_ACTIVE", "STATE_FAILED"]] = None
    """Output only. Current state of the `Document`."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """Output only. The Timestamp of when the `Document` was last updated."""
