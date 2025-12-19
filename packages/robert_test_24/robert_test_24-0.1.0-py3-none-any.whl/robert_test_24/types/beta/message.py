# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .citation_metadata import CitationMetadata

__all__ = ["Message"]


class Message(BaseModel):
    """The base unit of structured text.

    A `Message` includes an `author` and the `content` of
    the `Message`.

    The `author` is used to tag messages when they are fed to the
    model as text.
    """

    content: str
    """Required. The text content of the structured `Message`."""

    author: Optional[str] = None
    """Optional. The author of this Message.

    This serves as a key for tagging the content of this Message when it is fed to
    the model as text.

    The author can be any alphanumeric string.
    """

    citation_metadata: Optional[CitationMetadata] = FieldInfo(alias="citationMetadata", default=None)
    """A collection of source attributions for a piece of content."""
