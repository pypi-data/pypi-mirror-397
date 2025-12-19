# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo
from ...custom_metadata_param import CustomMetadataParam

__all__ = ["ChunkParam", "Data"]


class Data(TypedDict, total=False):
    """Extracted data that represents the `Chunk` content."""

    string_value: Annotated[str, PropertyInfo(alias="stringValue")]
    """
    The `Chunk` content as a string. The maximum number of tokens per chunk is 2043.
    """


class ChunkParam(TypedDict, total=False):
    """
    A `Chunk` is a subpart of a `Document` that is treated as an independent unit
    for the purposes of vector representation and storage.
    """

    data: Required[Data]
    """Extracted data that represents the `Chunk` content."""

    custom_metadata: Annotated[Iterable[CustomMetadataParam], PropertyInfo(alias="customMetadata")]
    """Optional.

    User provided custom metadata stored as key-value pairs. The maximum number of
    `CustomMetadata` per chunk is 20.
    """

    name: str
    """Immutable.

    Identifier. The `Chunk` resource name. The ID (name excluding the
    "corpora/_/documents/_/chunks/" prefix) can contain up to 40 characters that are
    lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If
    the name is empty on create, a random 12-character unique ID will be generated.
    Example: `corpora/{corpus_id}/documents/{document_id}/chunks/123a456b789c`
    """
