# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["RagStore"]


class RagStore(BaseModel):
    """A `RagStore` is a collection of `Document`s."""

    active_documents_count: Optional[str] = FieldInfo(alias="activeDocumentsCount", default=None)
    """Output only.

    The number of documents in the Ragstore that are active and ready for retrieval.
    """

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """Output only. The Timestamp of when the `RagStore` was created."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Optional.

    The human-readable display name for the `RagStore`. The display name must be no
    more than 512 characters in length, including spaces. Example: "Docs on Semantic
    Retriever"
    """

    failed_documents_count: Optional[str] = FieldInfo(alias="failedDocumentsCount", default=None)
    """Output only.

    The number of documents in the Ragstore that have failed processing.
    """

    name: Optional[str] = None
    """Output only.

    Immutable. Identifier. The `RagStore` resource name. It is an ID (name excluding
    the "ragStores/" prefix) that can contain up to 40 characters that are lowercase
    alphanumeric or dashes (-). It is output only. The unique name will be derived
    from `display_name` along with a 12 character random suffix. Example:
    `ragStores/my-awesome-rag-store-123a456b789c` If `display_name` is not provided,
    the name will be randomly generated.
    """

    pending_documents_count: Optional[str] = FieldInfo(alias="pendingDocumentsCount", default=None)
    """Output only. The number of documents in the Ragstore that are being processed."""

    size_bytes: Optional[str] = FieldInfo(alias="sizeBytes", default=None)
    """Output only.

    The size of raw bytes ingested into the Ragstore. This is the total size of all
    the documents in the Ragstore.
    """

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """Output only. The Timestamp of when the `RagStore` was last updated."""
