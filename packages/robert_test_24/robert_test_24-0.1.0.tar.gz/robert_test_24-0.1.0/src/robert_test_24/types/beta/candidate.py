# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .content import Content
from ..._models import BaseModel
from .safety_rating import SafetyRating
from .citation_metadata import CitationMetadata
from .logprobs_result_candidate import LogprobsResultCandidate

__all__ = [
    "Candidate",
    "GroundingAttribution",
    "GroundingAttributionSourceID",
    "GroundingAttributionSourceIDGroundingPassage",
    "GroundingAttributionSourceIDSemanticRetrieverChunk",
    "GroundingMetadata",
    "GroundingMetadataGroundingChunk",
    "GroundingMetadataGroundingChunkMaps",
    "GroundingMetadataGroundingChunkMapsPlaceAnswerSources",
    "GroundingMetadataGroundingChunkMapsPlaceAnswerSourcesReviewSnippet",
    "GroundingMetadataGroundingChunkRetrievedContext",
    "GroundingMetadataGroundingChunkWeb",
    "GroundingMetadataGroundingSupport",
    "GroundingMetadataGroundingSupportSegment",
    "GroundingMetadataRetrievalMetadata",
    "GroundingMetadataSearchEntryPoint",
    "LogprobsResult",
    "LogprobsResultTopCandidate",
    "URLContextMetadata",
    "URLContextMetadataURLMetadata",
]


class GroundingAttributionSourceIDGroundingPassage(BaseModel):
    """Identifier for a part within a `GroundingPassage`."""

    part_index: Optional[int] = FieldInfo(alias="partIndex", default=None)
    """Output only.

    Index of the part within the `GenerateAnswerRequest`'s
    `GroundingPassage.content`.
    """

    passage_id: Optional[str] = FieldInfo(alias="passageId", default=None)
    """Output only.

    ID of the passage matching the `GenerateAnswerRequest`'s `GroundingPassage.id`.
    """


class GroundingAttributionSourceIDSemanticRetrieverChunk(BaseModel):
    """
    Identifier for a `Chunk` retrieved via Semantic Retriever specified in the
    `GenerateAnswerRequest` using `SemanticRetrieverConfig`.
    """

    chunk: Optional[str] = None
    """Output only.

    Name of the `Chunk` containing the attributed text. Example:
    `corpora/123/documents/abc/chunks/xyz`
    """

    source: Optional[str] = None
    """Output only.

    Name of the source matching the request's `SemanticRetrieverConfig.source`.
    Example: `corpora/123` or `corpora/123/documents/abc`
    """


class GroundingAttributionSourceID(BaseModel):
    """Identifier for the source contributing to this attribution."""

    grounding_passage: Optional[GroundingAttributionSourceIDGroundingPassage] = FieldInfo(
        alias="groundingPassage", default=None
    )
    """Identifier for a part within a `GroundingPassage`."""

    semantic_retriever_chunk: Optional[GroundingAttributionSourceIDSemanticRetrieverChunk] = FieldInfo(
        alias="semanticRetrieverChunk", default=None
    )
    """
    Identifier for a `Chunk` retrieved via Semantic Retriever specified in the
    `GenerateAnswerRequest` using `SemanticRetrieverConfig`.
    """


class GroundingAttribution(BaseModel):
    """Attribution for a source that contributed to an answer."""

    content: Optional[Content] = None
    """The base structured datatype containing multi-part content of a message.

    A `Content` includes a `role` field designating the producer of the `Content`
    and a `parts` field containing multi-part data that contains the content of the
    message turn.
    """

    source_id: Optional[GroundingAttributionSourceID] = FieldInfo(alias="sourceId", default=None)
    """Identifier for the source contributing to this attribution."""


class GroundingMetadataGroundingChunkMapsPlaceAnswerSourcesReviewSnippet(BaseModel):
    """
    Encapsulates a snippet of a user review that answers a question about
    the features of a specific place in Google Maps.
    """

    google_maps_uri: Optional[str] = FieldInfo(alias="googleMapsUri", default=None)
    """A link that corresponds to the user review on Google Maps."""

    review_id: Optional[str] = FieldInfo(alias="reviewId", default=None)
    """The ID of the review snippet."""

    title: Optional[str] = None
    """Title of the review."""


class GroundingMetadataGroundingChunkMapsPlaceAnswerSources(BaseModel):
    """
    Collection of sources that provide answers about the features of a given
    place in Google Maps. Each PlaceAnswerSources message corresponds to a
    specific place in Google Maps. The Google Maps tool used these sources in
    order to answer questions about features of the place (e.g: "does Bar Foo
    have Wifi" or "is Foo Bar wheelchair accessible?"). Currently we only
    support review snippets as sources.
    """

    review_snippets: Optional[List[GroundingMetadataGroundingChunkMapsPlaceAnswerSourcesReviewSnippet]] = FieldInfo(
        alias="reviewSnippets", default=None
    )
    """
    Snippets of reviews that are used to generate answers about the features of a
    given place in Google Maps.
    """


class GroundingMetadataGroundingChunkMaps(BaseModel):
    """A grounding chunk from Google Maps.

    A Maps chunk corresponds to a single
    place.
    """

    place_answer_sources: Optional[GroundingMetadataGroundingChunkMapsPlaceAnswerSources] = FieldInfo(
        alias="placeAnswerSources", default=None
    )
    """
    Collection of sources that provide answers about the features of a given place
    in Google Maps. Each PlaceAnswerSources message corresponds to a specific place
    in Google Maps. The Google Maps tool used these sources in order to answer
    questions about features of the place (e.g: "does Bar Foo have Wifi" or "is Foo
    Bar wheelchair accessible?"). Currently we only support review snippets as
    sources.
    """

    place_id: Optional[str] = FieldInfo(alias="placeId", default=None)
    """This ID of the place, in `places/{place_id}` format.

    A user can use this ID to look up that place.
    """

    text: Optional[str] = None
    """Text description of the place answer."""

    title: Optional[str] = None
    """Title of the place."""

    uri: Optional[str] = None
    """URI reference of the place."""


class GroundingMetadataGroundingChunkRetrievedContext(BaseModel):
    """Chunk from context retrieved by the file search tool."""

    rag_store: Optional[str] = FieldInfo(alias="ragStore", default=None)
    """Optional.

    Name of the `RagStore` containing the document. Example: `ragStores/123`
    """

    text: Optional[str] = None
    """Optional. Text of the chunk."""

    title: Optional[str] = None
    """Optional. Title of the document."""

    uri: Optional[str] = None
    """Optional. URI reference of the semantic retrieval document."""


class GroundingMetadataGroundingChunkWeb(BaseModel):
    """Chunk from the web."""

    title: Optional[str] = None
    """Title of the chunk."""

    uri: Optional[str] = None
    """URI reference of the chunk."""


class GroundingMetadataGroundingChunk(BaseModel):
    """Grounding chunk."""

    maps: Optional[GroundingMetadataGroundingChunkMaps] = None
    """A grounding chunk from Google Maps. A Maps chunk corresponds to a single place."""

    retrieved_context: Optional[GroundingMetadataGroundingChunkRetrievedContext] = FieldInfo(
        alias="retrievedContext", default=None
    )
    """Chunk from context retrieved by the file search tool."""

    web: Optional[GroundingMetadataGroundingChunkWeb] = None
    """Chunk from the web."""


class GroundingMetadataGroundingSupportSegment(BaseModel):
    """Segment of the content."""

    end_index: Optional[int] = FieldInfo(alias="endIndex", default=None)
    """Output only.

    End index in the given Part, measured in bytes. Offset from the start of the
    Part, exclusive, starting at zero.
    """

    part_index: Optional[int] = FieldInfo(alias="partIndex", default=None)
    """Output only. The index of a Part object within its parent Content object."""

    start_index: Optional[int] = FieldInfo(alias="startIndex", default=None)
    """Output only.

    Start index in the given Part, measured in bytes. Offset from the start of the
    Part, inclusive, starting at zero.
    """

    text: Optional[str] = None
    """Output only. The text corresponding to the segment from the response."""


class GroundingMetadataGroundingSupport(BaseModel):
    """Grounding support."""

    confidence_scores: Optional[List[float]] = FieldInfo(alias="confidenceScores", default=None)
    """Confidence score of the support references.

    Ranges from 0 to 1. 1 is the most confident. This list must have the same size
    as the grounding_chunk_indices.
    """

    grounding_chunk_indices: Optional[List[int]] = FieldInfo(alias="groundingChunkIndices", default=None)
    """
    A list of indices (into 'grounding_chunk') specifying the citations associated
    with the claim. For instance [1,3,4] means that grounding_chunk[1],
    grounding_chunk[3], grounding_chunk[4] are the retrieved content attributed to
    the claim.
    """

    segment: Optional[GroundingMetadataGroundingSupportSegment] = None
    """Segment of the content."""


class GroundingMetadataRetrievalMetadata(BaseModel):
    """Metadata related to retrieval in the grounding flow."""

    google_search_dynamic_retrieval_score: Optional[float] = FieldInfo(
        alias="googleSearchDynamicRetrievalScore", default=None
    )
    """Optional.

    Score indicating how likely information from google search could help answer the
    prompt. The score is in the range [0, 1], where 0 is the least likely and 1 is
    the most likely. This score is only populated when google search grounding and
    dynamic retrieval is enabled. It will be compared to the threshold to determine
    whether to trigger google search.
    """


class GroundingMetadataSearchEntryPoint(BaseModel):
    """Google search entry point."""

    rendered_content: Optional[str] = FieldInfo(alias="renderedContent", default=None)
    """Optional.

    Web content snippet that can be embedded in a web page or an app webview.
    """

    sdk_blob: Optional[str] = FieldInfo(alias="sdkBlob", default=None)
    """Optional. Base64 encoded JSON representing array of tuple."""


class GroundingMetadata(BaseModel):
    """Metadata returned to client when grounding is enabled."""

    google_maps_widget_context_token: Optional[str] = FieldInfo(alias="googleMapsWidgetContextToken", default=None)
    """Optional.

    Resource name of the Google Maps widget context token that can be used with the
    PlacesContextElement widget in order to render contextual data. Only populated
    in the case that grounding with Google Maps is enabled.
    """

    grounding_chunks: Optional[List[GroundingMetadataGroundingChunk]] = FieldInfo(alias="groundingChunks", default=None)
    """List of supporting references retrieved from specified grounding source."""

    grounding_supports: Optional[List[GroundingMetadataGroundingSupport]] = FieldInfo(
        alias="groundingSupports", default=None
    )
    """List of grounding support."""

    retrieval_metadata: Optional[GroundingMetadataRetrievalMetadata] = FieldInfo(
        alias="retrievalMetadata", default=None
    )
    """Metadata related to retrieval in the grounding flow."""

    search_entry_point: Optional[GroundingMetadataSearchEntryPoint] = FieldInfo(alias="searchEntryPoint", default=None)
    """Google search entry point."""

    web_search_queries: Optional[List[str]] = FieldInfo(alias="webSearchQueries", default=None)
    """Web search queries for the following-up web search."""


class LogprobsResultTopCandidate(BaseModel):
    """Candidates with top log probabilities at each decoding step."""

    candidates: Optional[List[LogprobsResultCandidate]] = None
    """Sorted by log probability in descending order."""


class LogprobsResult(BaseModel):
    """Logprobs Result"""

    chosen_candidates: Optional[List[LogprobsResultCandidate]] = FieldInfo(alias="chosenCandidates", default=None)
    """
    Length = total number of decoding steps. The chosen candidates may or may not be
    in top_candidates.
    """

    log_probability_sum: Optional[float] = FieldInfo(alias="logProbabilitySum", default=None)
    """Sum of log probabilities for all tokens."""

    top_candidates: Optional[List[LogprobsResultTopCandidate]] = FieldInfo(alias="topCandidates", default=None)
    """Length = total number of decoding steps."""


class URLContextMetadataURLMetadata(BaseModel):
    """Context of the a single url retrieval."""

    retrieved_url: Optional[str] = FieldInfo(alias="retrievedUrl", default=None)
    """Retrieved url by the tool."""

    url_retrieval_status: Optional[
        Literal[
            "URL_RETRIEVAL_STATUS_UNSPECIFIED",
            "URL_RETRIEVAL_STATUS_SUCCESS",
            "URL_RETRIEVAL_STATUS_ERROR",
            "URL_RETRIEVAL_STATUS_PAYWALL",
            "URL_RETRIEVAL_STATUS_UNSAFE",
        ]
    ] = FieldInfo(alias="urlRetrievalStatus", default=None)
    """Status of the url retrieval."""


class URLContextMetadata(BaseModel):
    """Metadata related to url context retrieval tool."""

    url_metadata: Optional[List[URLContextMetadataURLMetadata]] = FieldInfo(alias="urlMetadata", default=None)
    """List of url context."""


class Candidate(BaseModel):
    """A response candidate generated from the model."""

    avg_logprobs: Optional[float] = FieldInfo(alias="avgLogprobs", default=None)
    """Output only. Average log probability score of the candidate."""

    citation_metadata: Optional[CitationMetadata] = FieldInfo(alias="citationMetadata", default=None)
    """A collection of source attributions for a piece of content."""

    content: Optional[Content] = None
    """The base structured datatype containing multi-part content of a message.

    A `Content` includes a `role` field designating the producer of the `Content`
    and a `parts` field containing multi-part data that contains the content of the
    message turn.
    """

    finish_message: Optional[str] = FieldInfo(alias="finishMessage", default=None)
    """Optional.

    Output only. Details the reason why the model stopped generating tokens. This is
    populated only when `finish_reason` is set.
    """

    finish_reason: Optional[
        Literal[
            "FINISH_REASON_UNSPECIFIED",
            "STOP",
            "MAX_TOKENS",
            "SAFETY",
            "RECITATION",
            "LANGUAGE",
            "OTHER",
            "BLOCKLIST",
            "PROHIBITED_CONTENT",
            "SPII",
            "MALFORMED_FUNCTION_CALL",
            "IMAGE_SAFETY",
            "IMAGE_PROHIBITED_CONTENT",
            "IMAGE_OTHER",
            "NO_IMAGE",
            "IMAGE_RECITATION",
            "UNEXPECTED_TOOL_CALL",
            "TOO_MANY_TOOL_CALLS",
        ]
    ] = FieldInfo(alias="finishReason", default=None)
    """Optional. Output only. The reason why the model stopped generating tokens.

    If empty, the model has not stopped generating tokens.
    """

    grounding_attributions: Optional[List[GroundingAttribution]] = FieldInfo(
        alias="groundingAttributions", default=None
    )
    """Output only.

    Attribution information for sources that contributed to a grounded answer.

    This field is populated for `GenerateAnswer` calls.
    """

    grounding_metadata: Optional[GroundingMetadata] = FieldInfo(alias="groundingMetadata", default=None)
    """Metadata returned to client when grounding is enabled."""

    index: Optional[int] = None
    """Output only. Index of the candidate in the list of response candidates."""

    logprobs_result: Optional[LogprobsResult] = FieldInfo(alias="logprobsResult", default=None)
    """Logprobs Result"""

    safety_ratings: Optional[List[SafetyRating]] = FieldInfo(alias="safetyRatings", default=None)
    """List of ratings for the safety of a response candidate.

    There is at most one rating per category.
    """

    token_count: Optional[int] = FieldInfo(alias="tokenCount", default=None)
    """Output only. Token count for this candidate."""

    url_context_metadata: Optional[URLContextMetadata] = FieldInfo(alias="urlContextMetadata", default=None)
    """Metadata related to url context retrieval tool."""
