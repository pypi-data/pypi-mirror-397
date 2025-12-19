# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ....._models import BaseModel
from ...custom_metadata import CustomMetadata

__all__ = ["Chunk", "Data"]


class Data(BaseModel):
    """Extracted data that represents the `Chunk` content."""

    string_value: Optional[str] = FieldInfo(alias="stringValue", default=None)
    """
    The `Chunk` content as a string. The maximum number of tokens per chunk is 2043.
    """


class Chunk(BaseModel):
    """
    A `Chunk` is a subpart of a `Document` that is treated as an independent unit
    for the purposes of vector representation and storage.
    """

    data: Data
    """Extracted data that represents the `Chunk` content."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """Output only. The Timestamp of when the `Chunk` was created."""

    custom_metadata: Optional[List[CustomMetadata]] = FieldInfo(alias="customMetadata", default=None)
    """Optional.

    User provided custom metadata stored as key-value pairs. The maximum number of
    `CustomMetadata` per chunk is 20.
    """

    name: Optional[str] = None
    """Immutable.

    Identifier. The `Chunk` resource name. The ID (name excluding the
    "corpora/_/documents/_/chunks/" prefix) can contain up to 40 characters that are
    lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If
    the name is empty on create, a random 12-character unique ID will be generated.
    Example: `corpora/{corpus_id}/documents/{document_id}/chunks/123a456b789c`
    """

    state: Optional[Literal["STATE_UNSPECIFIED", "STATE_PENDING_PROCESSING", "STATE_ACTIVE", "STATE_FAILED"]] = None
    """Output only. Current state of the `Chunk`."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """Output only. The Timestamp of when the `Chunk` was last updated."""
