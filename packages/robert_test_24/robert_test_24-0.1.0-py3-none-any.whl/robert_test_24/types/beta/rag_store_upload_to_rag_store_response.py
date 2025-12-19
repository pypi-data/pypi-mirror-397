# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .base_operation import BaseOperation

__all__ = ["RagStoreUploadToRagStoreResponse", "RagStoreUploadToRagStoreResponseResponse"]


class RagStoreUploadToRagStoreResponseResponse(BaseModel):
    """Response from UploadToRagStore."""

    document_name: Optional[str] = FieldInfo(alias="documentName", default=None)
    """Immutable.

    Identifier. The identifier for the `Document` imported. Example:
    `ragStores/{rag_store}/documents/my-awesome-doc-123a456b789c`
    """

    mime_type: Optional[str] = FieldInfo(alias="mimeType", default=None)
    """MIME type of the file."""

    parent: Optional[str] = None
    """
    The name of the `RagStore` containing `Document`s. Example:
    `ragStores/my-rag-store-123`
    """

    size_bytes: Optional[str] = FieldInfo(alias="sizeBytes", default=None)
    """Size of the file in bytes."""


class RagStoreUploadToRagStoreResponse(BaseOperation):
    """
    This resource represents a long-running operation where metadata and response fields are strongly typed.
    """

    metadata: Optional[object] = None
    """Metadata for LongRunning UploadDataToRagStore Operations."""

    response: Optional[RagStoreUploadToRagStoreResponseResponse] = None
    """Response from UploadToRagStore."""
