# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = [
    "BatchUpdateGenerateContentBatchUpdateGenerateContentBatchParams",
    "InputConfig",
    "InputConfigRequests",
    "InputConfigRequestsRequest",
    "api_empty",
]


class BatchUpdateGenerateContentBatchUpdateGenerateContentBatchParams(TypedDict, total=False):
    display_name: Required[Annotated[str, PropertyInfo(alias="displayName")]]
    """Required. The user-defined name of this batch."""

    input_config: Required[Annotated[InputConfig, PropertyInfo(alias="inputConfig")]]
    """Configures the input to the batch request."""

    model: Required[str]
    """Required. The name of the `Model` to use for generating the completion.

    Format: `models/{model}`.
    """

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    update_mask: Annotated[str, PropertyInfo(alias="updateMask")]
    """Optional. The list of fields to update."""

    priority: str
    """Optional.

    The priority of the batch. Batches with a higher priority value will be
    processed before batches with a lower priority value. Negative values are
    allowed. Default is 0.
    """


class InputConfigRequestsRequest(TypedDict, total=False):
    """The request to be processed in the batch."""

    request: Required["GenerateContentRequestParam"]
    """Request to generate a completion from the model."""

    metadata: Dict[str, object]
    """Optional. The metadata to be associated with the request."""


class InputConfigRequests(TypedDict, total=False):
    """
    The requests to be processed in the batch if provided as part of the
    batch creation request.
    """

    requests: Required[Iterable[InputConfigRequestsRequest]]
    """Required. The requests to be processed in the batch."""


class InputConfig(TypedDict, total=False):
    """Configures the input to the batch request."""

    file_name: Annotated[str, PropertyInfo(alias="fileName")]
    """The name of the `File` containing the input requests."""

    requests: InputConfigRequests
    """
    The requests to be processed in the batch if provided as part of the batch
    creation request.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""


from .generate_content_request_param import GenerateContentRequestParam
