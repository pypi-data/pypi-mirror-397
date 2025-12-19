# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo
from .custom_metadata_param import CustomMetadataParam

__all__ = ["RagStoreUploadToRagStoreParams", "api_empty", "ChunkingConfig", "ChunkingConfigWhiteSpaceConfig"]


class RagStoreUploadToRagStoreParams(TypedDict, total=False):
    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    chunking_config: Annotated[ChunkingConfig, PropertyInfo(alias="chunkingConfig")]
    """
    Parameters for telling the service how to chunk the file. inspired by
    google3/cloud/ai/platform/extension/lib/retrieval/config/chunker_config.proto
    """

    custom_metadata: Annotated[Iterable[CustomMetadataParam], PropertyInfo(alias="customMetadata")]
    """Custom metadata to be associated with the data."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Optional. Display name of the created document."""

    mime_type: Annotated[str, PropertyInfo(alias="mimeType")]
    """Optional.

    MIME type of the data. If not provided, it will be inferred from the uploaded
    content.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""


class ChunkingConfigWhiteSpaceConfig(TypedDict, total=False):
    """Configuration for a white space chunking algorithm [white space delimited]."""

    max_overlap_tokens: Annotated[int, PropertyInfo(alias="maxOverlapTokens")]
    """Maximum number of overlapping tokens between two adjacent chunks."""

    max_tokens_per_chunk: Annotated[int, PropertyInfo(alias="maxTokensPerChunk")]
    """
    Maximum number of tokens per chunk. Tokens are defined as words for this
    chunking algorithm. Note: we are defining tokens as words split by whitespace as
    opposed to the output of a tokenizer. The context window of the latest gemini
    embedding model as of 2025-04-17 is currently 8192 tokens. We assume that the
    average word is 5 characters. Therefore, we set the upper limit to 2\\**\\**9, which
    is 512 words, or 2560 tokens, assuming worst case a character per token. This is
    a conservative estimate meant to prevent context window overflow.
    """


class ChunkingConfig(TypedDict, total=False):
    """
    Parameters for telling the service how to chunk the file.
    inspired by
    google3/cloud/ai/platform/extension/lib/retrieval/config/chunker_config.proto
    """

    white_space_config: Annotated[ChunkingConfigWhiteSpaceConfig, PropertyInfo(alias="whiteSpaceConfig")]
    """Configuration for a white space chunking algorithm [white space delimited]."""
