# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["CitationMetadata", "CitationSource"]


class CitationSource(BaseModel):
    """A citation to a source for a portion of a specific response."""

    end_index: Optional[int] = FieldInfo(alias="endIndex", default=None)
    """Optional. End of the attributed segment, exclusive."""

    license: Optional[str] = None
    """Optional.

    License for the GitHub project that is attributed as a source for segment.

    License info is required for code citations.
    """

    start_index: Optional[int] = FieldInfo(alias="startIndex", default=None)
    """Optional. Start of segment of the response that is attributed to this source.

    Index indicates the start of the segment, measured in bytes.
    """

    uri: Optional[str] = None
    """Optional. URI that is attributed as a source for a portion of the text."""


class CitationMetadata(BaseModel):
    """A collection of source attributions for a piece of content."""

    citation_sources: Optional[List[CitationSource]] = FieldInfo(alias="citationSources", default=None)
    """Citations to sources for a specific response."""
