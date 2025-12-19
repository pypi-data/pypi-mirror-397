# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .content import Content
from ..._models import BaseModel

__all__ = ["EmbedContentRequest"]


class EmbedContentRequest(BaseModel):
    """Request containing the `Content` for the model to embed."""

    content: Content
    """The base structured datatype containing multi-part content of a message.

    A `Content` includes a `role` field designating the producer of the `Content`
    and a `parts` field containing multi-part data that contains the content of the
    message turn.
    """

    model: str
    """Required. The model's resource name. This serves as an ID for the Model to use.

    This name should match a model name returned by the `ListModels` method.

    Format: `models/{model}`
    """

    output_dimensionality: Optional[int] = FieldInfo(alias="outputDimensionality", default=None)
    """Optional.

    Optional reduced dimension for the output embedding. If set, excessive values in
    the output embedding are truncated from the end. Supported by newer models since
    2024 only. You cannot set this value if using the earlier model
    (`models/embedding-001`).
    """

    task_type: Optional[
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
        ]
    ] = FieldInfo(alias="taskType", default=None)
    """Optional.

    Optional task type for which the embeddings will be used. Not supported on
    earlier models (`models/embedding-001`).
    """

    title: Optional[str] = None
    """Optional.

    An optional title for the text. Only applicable when TaskType is
    `RETRIEVAL_DOCUMENT`.

    Note: Specifying a `title` for `RETRIEVAL_DOCUMENT` provides better quality
    embeddings for retrieval.
    """
