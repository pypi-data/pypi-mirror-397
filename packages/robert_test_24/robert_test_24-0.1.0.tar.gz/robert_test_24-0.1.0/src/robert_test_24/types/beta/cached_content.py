# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["CachedContent", "UsageMetadata"]


class UsageMetadata(BaseModel):
    """Metadata on the usage of the cached content."""

    total_token_count: Optional[int] = FieldInfo(alias="totalTokenCount", default=None)
    """Total number of tokens that the cached content consumes."""


class CachedContent(BaseModel):
    """
    Content that has been preprocessed and can be used in subsequent request
    to GenerativeService.

    Cached content can be only used with model it was created for.
    """

    model: str
    """Required.

    Immutable. The name of the `Model` to use for cached content Format:
    `models/{model}`
    """

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """Output only. Creation time of the cache entry."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Optional.

    Immutable. The user-generated meaningful display name of the cached content.
    Maximum 128 Unicode characters.
    """

    expire_time: Optional[datetime] = FieldInfo(alias="expireTime", default=None)
    """
    Timestamp in UTC of when this resource is considered expired. This is _always_
    provided on output, regardless of what was sent on input.
    """

    name: Optional[str] = None
    """Output only.

    Identifier. The resource name referring to the cached content. Format:
    `cachedContents/{id}`
    """

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """Output only. When the cache entry was last updated in UTC time."""

    usage_metadata: Optional[UsageMetadata] = FieldInfo(alias="usageMetadata", default=None)
    """Metadata on the usage of the cached content."""
