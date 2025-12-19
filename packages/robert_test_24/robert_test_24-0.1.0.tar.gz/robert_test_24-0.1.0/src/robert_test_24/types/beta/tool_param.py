# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = [
    "ToolParam",
    "ComputerUse",
    "FileSearch",
    "FileSearchRetrievalResource",
    "FileSearchRetrievalConfig",
    "FunctionDeclaration",
    "GoogleMaps",
    "GoogleSearch",
    "GoogleSearchTimeRangeFilter",
    "GoogleSearchRetrieval",
    "GoogleSearchRetrievalDynamicRetrievalConfig",
]


class ComputerUse(TypedDict, total=False):
    """Computer Use tool type."""

    environment: Required[Literal["ENVIRONMENT_UNSPECIFIED", "ENVIRONMENT_BROWSER"]]
    """Required. The environment being operated."""

    excluded_predefined_functions: Annotated[SequenceNotStr[str], PropertyInfo(alias="excludedPredefinedFunctions")]
    """Optional.

    By default, predefined functions are included in the final model call. Some of
    them can be explicitly excluded from being automatically included. This can
    serve two purposes:

    1. Using a more restricted / different action space.
    2. Improving the definitions / instructions of predefined functions.
    """


class FileSearchRetrievalResource(TypedDict, total=False):
    """The semantic retrieval resource to retrieve from."""

    rag_store_name: Required[Annotated[str, PropertyInfo(alias="ragStoreName")]]
    """Required.

    The name of the semantic retrieval resource to retrieve from. Example:
    `ragStores/my-rag-store-123`
    """


class FileSearchRetrievalConfig(TypedDict, total=False):
    """Semantic retrieval configuration."""

    metadata_filter: Annotated[str, PropertyInfo(alias="metadataFilter")]
    """Optional.

    Metadata filter to apply to the semantic retrieval documents and chunks.
    """

    top_k: Annotated[int, PropertyInfo(alias="topK")]
    """Optional. The number of semantic retrieval chunks to retrieve."""


class FileSearch(TypedDict, total=False):
    """
    The FileSearch tool that retrieves knowledge from Semantic Retrieval corpora.
    Files are imported to Semantic Retrieval corpora using the ImportFile API.
    """

    retrieval_resources: Required[
        Annotated[Iterable[FileSearchRetrievalResource], PropertyInfo(alias="retrievalResources")]
    ]
    """Required.

    Semantic retrieval resources to retrieve from. Currently only supports one
    corpus. In the future we may open up multiple corpora support.
    """

    retrieval_config: Annotated[FileSearchRetrievalConfig, PropertyInfo(alias="retrievalConfig")]
    """Semantic retrieval configuration."""


class FunctionDeclaration(TypedDict, total=False):
    """
    Structured representation of a function declaration as defined by the
    [OpenAPI 3.03 specification](https://spec.openapis.org/oas/v3.0.3). Included
    in this declaration are the function name and parameters. This
    FunctionDeclaration is a representation of a block of code that can be used
    as a `Tool` by the model and executed by the client.
    """

    description: Required[str]
    """Required. A brief description of the function."""

    name: Required[str]
    """Required.

    The name of the function. Must be a-z, A-Z, 0-9, or contain underscores, colons,
    dots, and dashes, with a maximum length of 64.
    """

    behavior: Literal["UNSPECIFIED", "BLOCKING", "NON_BLOCKING"]
    """Optional.

    Specifies the function Behavior. Currently only supported by the
    BidiGenerateContent method.
    """

    parameters: "SchemaParam"
    """
    The `Schema` object allows the definition of input and output data types. These
    types can be objects, but also primitives and arrays. Represents a select subset
    of an [OpenAPI 3.0 schema object](https://spec.openapis.org/oas/v3.0.3#schema).
    """

    parameters_json_schema: Annotated[object, PropertyInfo(alias="parametersJsonSchema")]
    """Optional.

    Describes the parameters to the function in JSON Schema format. The schema must
    describe an object where the properties are the parameters to the function. For
    example:

    ```
    {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "age": { "type": "integer" }
      },
      "additionalProperties": false,
      "required": ["name", "age"],
      "propertyOrdering": ["name", "age"]
    }
    ```

    This field is mutually exclusive with `parameters`.
    """

    response: "SchemaParam"
    """
    The `Schema` object allows the definition of input and output data types. These
    types can be objects, but also primitives and arrays. Represents a select subset
    of an [OpenAPI 3.0 schema object](https://spec.openapis.org/oas/v3.0.3#schema).
    """

    response_json_schema: Annotated[object, PropertyInfo(alias="responseJsonSchema")]
    """Optional.

    Describes the output from this function in JSON Schema format. The value
    specified by the schema is the response value of the function.

    This field is mutually exclusive with `response`.
    """


class GoogleMaps(TypedDict, total=False):
    """The GoogleMaps Tool that provides geospatial context for the user's query."""

    enable_widget: Annotated[bool, PropertyInfo(alias="enableWidget")]
    """Optional.

    Whether to return a widget context token in the GroundingMetadata of the
    response. Developers can use the widget context token to render a Google Maps
    widget with geospatial context related to the places that the model references
    in the response.
    """


class GoogleSearchTimeRangeFilter(TypedDict, total=False):
    """
    Represents a time interval, encoded as a Timestamp start (inclusive) and a
    Timestamp end (exclusive).

    The start must be less than or equal to the end.
    When the start equals the end, the interval is empty (matches no time).
    When both start and end are unspecified, the interval matches any time.
    """

    end_time: Annotated[Union[str, datetime], PropertyInfo(alias="endTime", format="iso8601")]
    """Optional. Exclusive end of the interval.

    If specified, a Timestamp matching this interval will have to be before the end.
    """

    start_time: Annotated[Union[str, datetime], PropertyInfo(alias="startTime", format="iso8601")]
    """Optional. Inclusive start of the interval.

    If specified, a Timestamp matching this interval will have to be the same or
    after the start.
    """


class GoogleSearch(TypedDict, total=False):
    """GoogleSearch tool type.
    Tool to support Google Search in Model.

    Powered by Google.
    """

    time_range_filter: Annotated[GoogleSearchTimeRangeFilter, PropertyInfo(alias="timeRangeFilter")]
    """
    Represents a time interval, encoded as a Timestamp start (inclusive) and a
    Timestamp end (exclusive).

    The start must be less than or equal to the end. When the start equals the end,
    the interval is empty (matches no time). When both start and end are
    unspecified, the interval matches any time.
    """


class GoogleSearchRetrievalDynamicRetrievalConfig(TypedDict, total=False):
    """Describes the options to customize dynamic retrieval."""

    dynamic_threshold: Annotated[float, PropertyInfo(alias="dynamicThreshold")]
    """
    The threshold to be used in dynamic retrieval. If not set, a system default
    value is used.
    """

    mode: Literal["MODE_UNSPECIFIED", "MODE_DYNAMIC"]
    """The mode of the predictor to be used in dynamic retrieval."""


class GoogleSearchRetrieval(TypedDict, total=False):
    """Tool to retrieve public web data for grounding, powered by Google."""

    dynamic_retrieval_config: Annotated[
        GoogleSearchRetrievalDynamicRetrievalConfig, PropertyInfo(alias="dynamicRetrievalConfig")
    ]
    """Describes the options to customize dynamic retrieval."""


class ToolParam(TypedDict, total=False):
    """Tool details that the model may use to generate response.

    A `Tool` is a piece of code that enables the system to interact with
    external systems to perform an action, or set of actions, outside of
    knowledge and scope of the model.

    Next ID: 12
    """

    code_execution: Annotated[object, PropertyInfo(alias="codeExecution")]
    """
    Tool that executes code generated by the model, and automatically returns the
    result to the model.

    See also `ExecutableCode` and `CodeExecutionResult` which are only generated
    when using this tool.
    """

    computer_use: Annotated[ComputerUse, PropertyInfo(alias="computerUse")]
    """Computer Use tool type."""

    file_search: Annotated[FileSearch, PropertyInfo(alias="fileSearch")]
    """
    The FileSearch tool that retrieves knowledge from Semantic Retrieval corpora.
    Files are imported to Semantic Retrieval corpora using the ImportFile API.
    """

    function_declarations: Annotated[Iterable[FunctionDeclaration], PropertyInfo(alias="functionDeclarations")]
    """Optional.

    A list of `FunctionDeclarations` available to the model that can be used for
    function calling.

    The model or system does not execute the function. Instead the defined function
    may be returned as a FunctionCall with arguments to the client side for
    execution. The model may decide to call a subset of these functions by
    populating FunctionCall in the response. The next conversation turn may contain
    a FunctionResponse with the Content.role "function" generation context for the
    next model turn.
    """

    google_maps: Annotated[GoogleMaps, PropertyInfo(alias="googleMaps")]
    """The GoogleMaps Tool that provides geospatial context for the user's query."""

    google_search: Annotated[GoogleSearch, PropertyInfo(alias="googleSearch")]
    """GoogleSearch tool type. Tool to support Google Search in Model.

    Powered by Google.
    """

    google_search_retrieval: Annotated[GoogleSearchRetrieval, PropertyInfo(alias="googleSearchRetrieval")]
    """Tool to retrieve public web data for grounding, powered by Google."""

    url_context: Annotated[object, PropertyInfo(alias="urlContext")]
    """Tool to support URL context retrieval."""


from .schema_param import SchemaParam
