# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Corpus"]


class Corpus(BaseModel):
    """
    A `Corpus` is a collection of `Document`s.
    A project can create up to 10 corpora.
    """

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """Output only. The Timestamp of when the `Corpus` was created."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Optional.

    The human-readable display name for the `Corpus`. The display name must be no
    more than 512 characters in length, including spaces. Example: "Docs on Semantic
    Retriever"
    """

    name: Optional[str] = None
    """Output only.

    Immutable. Identifier. The `Corpus` resource name. The ID (name excluding the
    "corpora/" prefix) can contain up to 40 characters that are lowercase
    alphanumeric or dashes (-). The ID cannot start or end with a dash. If the name
    is empty on create, a unique name will be derived from `display_name` along with
    a 12 character random suffix. Example: `corpora/my-awesome-corpora-123a456b789c`
    """

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """Output only. The Timestamp of when the `Corpus` was last updated."""
