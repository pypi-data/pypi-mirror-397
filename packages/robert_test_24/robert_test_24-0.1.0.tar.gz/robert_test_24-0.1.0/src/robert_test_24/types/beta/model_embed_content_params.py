# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .content_param import ContentParam

__all__ = ["ModelEmbedContentParams", "api_empty"]


class ModelEmbedContentParams(TypedDict, total=False):
    content: Required[ContentParam]
    """The base structured datatype containing multi-part content of a message.

    A `Content` includes a `role` field designating the producer of the `Content`
    and a `parts` field containing multi-part data that contains the content of the
    message turn.
    """

    body_model: Required[Annotated[str, PropertyInfo(alias="model")]]
    """Required. The model's resource name. This serves as an ID for the Model to use.

    This name should match a model name returned by the `ListModels` method.

    Format: `models/{model}`
    """

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    output_dimensionality: Annotated[int, PropertyInfo(alias="outputDimensionality")]
    """Optional.

    Optional reduced dimension for the output embedding. If set, excessive values in
    the output embedding are truncated from the end. Supported by newer models since
    2024 only. You cannot set this value if using the earlier model
    (`models/embedding-001`).
    """

    task_type: Annotated[
        Literal[
            "TASK_TYPE_UNSPECIFIED",
            "RETRIEVAL_QUERY",
            "RETRIEVAL_DOCUMENT",
            "SEMANTIC_SIMILARITY",
            "CLASSIFICATION",
            "CLUSTERING",
            "QUESTION_ANSWERING",
            "FACT_VERIFICATION",
            "CODE_RETRIEVAL_QUERY",
        ],
        PropertyInfo(alias="taskType"),
    ]
    """Optional.

    Optional task type for which the embeddings will be used. Not supported on
    earlier models (`models/embedding-001`).
    """

    title: str
    """Optional.

    An optional title for the text. Only applicable when TaskType is
    `RETRIEVAL_DOCUMENT`.

    Note: Specifying a `title` for `RETRIEVAL_DOCUMENT` provides better quality
    embeddings for retrieval.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
