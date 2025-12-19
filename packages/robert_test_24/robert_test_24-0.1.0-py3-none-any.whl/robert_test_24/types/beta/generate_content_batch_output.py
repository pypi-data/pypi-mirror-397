# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .status import Status
from ..._models import BaseModel
from .generate_content_response import GenerateContentResponse

__all__ = ["GenerateContentBatchOutput", "InlinedResponses", "InlinedResponsesInlinedResponse"]


class InlinedResponsesInlinedResponse(BaseModel):
    """The response to a single request in the batch."""

    error: Optional[Status] = None
    """
    The `Status` type defines a logical error model that is suitable for different
    programming environments, including REST APIs and RPC APIs. It is used by
    [gRPC](https://github.com/grpc). Each `Status` message contains three pieces of
    data: error code, error message, and error details.

    You can find out more about this error model and how to work with it in the
    [API Design Guide](https://cloud.google.com/apis/design/errors).
    """

    metadata: Optional[Dict[str, object]] = None
    """Output only. The metadata associated with the request."""

    response: Optional[GenerateContentResponse] = None
    """Response from the model supporting multiple candidate responses.

    Safety ratings and content filtering are reported for both prompt in
    `GenerateContentResponse.prompt_feedback` and for each candidate in
    `finish_reason` and in `safety_ratings`. The API:

    - Returns either all requested candidates or none of them
    - Returns no candidates at all only if there was something wrong with the prompt
      (check `prompt_feedback`)
    - Reports feedback on each candidate in `finish_reason` and `safety_ratings`.
    """


class InlinedResponses(BaseModel):
    """The responses to the requests in the batch."""

    inlined_responses: Optional[List[InlinedResponsesInlinedResponse]] = FieldInfo(
        alias="inlinedResponses", default=None
    )
    """Output only. The responses to the requests in the batch."""


class GenerateContentBatchOutput(BaseModel):
    """The output of a batch request.

    This is returned in the
    `BatchGenerateContentResponse` or the `GenerateContentBatch.output` field.
    """

    inlined_responses: Optional[InlinedResponses] = FieldInfo(alias="inlinedResponses", default=None)
    """The responses to the requests in the batch."""

    responses_file: Optional[str] = FieldInfo(alias="responsesFile", default=None)
    """Output only.

    The file ID of the file containing the responses. The file will be a JSONL file
    with a single response per line. The responses will be `GenerateContentResponse`
    messages formatted as JSON. The responses will be written in the same order as
    the input requests.
    """
