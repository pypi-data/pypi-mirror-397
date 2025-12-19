# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CitationMetadataParam", "CitationSource"]


class CitationSource(TypedDict, total=False):
    """A citation to a source for a portion of a specific response."""

    end_index: Annotated[int, PropertyInfo(alias="endIndex")]
    """Optional. End of the attributed segment, exclusive."""

    license: str
    """Optional.

    License for the GitHub project that is attributed as a source for segment.

    License info is required for code citations.
    """

    start_index: Annotated[int, PropertyInfo(alias="startIndex")]
    """Optional. Start of segment of the response that is attributed to this source.

    Index indicates the start of the segment, measured in bytes.
    """

    uri: str
    """Optional. URI that is attributed as a source for a portion of the text."""


class CitationMetadataParam(TypedDict, total=False):
    """A collection of source attributions for a piece of content."""

    citation_sources: Annotated[Iterable[CitationSource], PropertyInfo(alias="citationSources")]
    """Citations to sources for a specific response."""
