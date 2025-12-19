# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .content_param import ContentParam
from .safety_setting_param import SafetySettingParam
from .metadata_filter_param import MetadataFilterParam

__all__ = ["ModelGenerateAnswerParams", "api_empty", "InlinePassages", "InlinePassagesPassage", "SemanticRetriever"]


class ModelGenerateAnswerParams(TypedDict, total=False):
    answer_style: Required[
        Annotated[
            Literal["ANSWER_STYLE_UNSPECIFIED", "ABSTRACTIVE", "EXTRACTIVE", "VERBOSE"],
            PropertyInfo(alias="answerStyle"),
        ]
    ]
    """Required. Style in which answers should be returned."""

    contents: Required[Iterable[ContentParam]]
    """Required.

    The content of the current conversation with the `Model`. For single-turn
    queries, this is a single question to answer. For multi-turn queries, this is a
    repeated field that contains conversation history and the last `Content` in the
    list containing the question.

    Note: `GenerateAnswer` only supports queries in English.
    """

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    inline_passages: Annotated[InlinePassages, PropertyInfo(alias="inlinePassages")]
    """A repeated list of passages."""

    safety_settings: Annotated[Iterable[SafetySettingParam], PropertyInfo(alias="safetySettings")]
    """Optional.

    A list of unique `SafetySetting` instances for blocking unsafe content.

    This will be enforced on the `GenerateAnswerRequest.contents` and
    `GenerateAnswerResponse.candidate`. There should not be more than one setting
    for each `SafetyCategory` type. The API will block any contents and responses
    that fail to meet the thresholds set by these settings. This list overrides the
    default settings for each `SafetyCategory` specified in the safety_settings. If
    there is no `SafetySetting` for a given `SafetyCategory` provided in the list,
    the API will use the default safety setting for that category. Harm categories
    HARM_CATEGORY_HATE_SPEECH, HARM_CATEGORY_SEXUALLY_EXPLICIT,
    HARM_CATEGORY_DANGEROUS_CONTENT, HARM_CATEGORY_HARASSMENT are supported. Refer
    to the [guide](https://ai.google.dev/gemini-api/docs/safety-settings) for
    detailed information on available safety settings. Also refer to the
    [Safety guidance](https://ai.google.dev/gemini-api/docs/safety-guidance) to
    learn how to incorporate safety considerations in your AI applications.
    """

    semantic_retriever: Annotated[SemanticRetriever, PropertyInfo(alias="semanticRetriever")]
    """
    Configuration for retrieving grounding content from a `Corpus` or `Document`
    created using the Semantic Retriever API.
    """

    temperature: float
    """Optional. Controls the randomness of the output.

    Values can range from [0.0,1.0], inclusive. A value closer to 1.0 will produce
    responses that are more varied and creative, while a value closer to 0.0 will
    typically result in more straightforward responses from the model. A low
    temperature (~0.2) is usually recommended for Attributed-Question-Answering use
    cases.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""


class InlinePassagesPassage(TypedDict, total=False):
    """Passage included inline with a grounding configuration."""

    id: str
    """Identifier for the passage for attributing this passage in grounded answers."""

    content: ContentParam
    """The base structured datatype containing multi-part content of a message.

    A `Content` includes a `role` field designating the producer of the `Content`
    and a `parts` field containing multi-part data that contains the content of the
    message turn.
    """


class InlinePassages(TypedDict, total=False):
    """A repeated list of passages."""

    passages: Iterable[InlinePassagesPassage]
    """List of passages."""


class SemanticRetriever(TypedDict, total=False):
    """
    Configuration for retrieving grounding content from a `Corpus` or
    `Document` created using the Semantic Retriever API.
    """

    query: Required[ContentParam]
    """The base structured datatype containing multi-part content of a message.

    A `Content` includes a `role` field designating the producer of the `Content`
    and a `parts` field containing multi-part data that contains the content of the
    message turn.
    """

    source: Required[str]
    """Required.

    Name of the resource for retrieval. Example: `corpora/123` or
    `corpora/123/documents/abc`.
    """

    max_chunks_count: Annotated[int, PropertyInfo(alias="maxChunksCount")]
    """Optional. Maximum number of relevant `Chunk`s to retrieve."""

    metadata_filters: Annotated[Iterable[MetadataFilterParam], PropertyInfo(alias="metadataFilters")]
    """Optional. Filters for selecting `Document`s and/or `Chunk`s from the resource."""

    minimum_relevance_score: Annotated[float, PropertyInfo(alias="minimumRelevanceScore")]
    """Optional. Minimum relevance score for retrieved relevant `Chunk`s."""
