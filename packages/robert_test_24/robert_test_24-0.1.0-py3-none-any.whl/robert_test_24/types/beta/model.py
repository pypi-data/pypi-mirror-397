# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Model"]


class Model(BaseModel):
    """Information about a Generative Language Model."""

    base_model_id: str = FieldInfo(alias="baseModelId")
    """Required. The name of the base model, pass this to the generation request.

    Examples:

    - `gemini-1.5-flash`
    """

    name: str
    """Required.

    The resource name of the `Model`. Refer to
    [Model variants](https://ai.google.dev/gemini-api/docs/models/gemini#model-variations)
    for all allowed values.

    Format: `models/{model}` with a `{model}` naming convention of:

    - "{base_model_id}-{version}"

    Examples:

    - `models/gemini-1.5-flash-001`
    """

    version: str
    """Required. The version number of the model.

    This represents the major version (`1.0` or `1.5`)
    """

    description: Optional[str] = None
    """A short description of the model."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """The human-readable name of the model. E.g. "Gemini 1.5 Flash".

    The name can be up to 128 characters long and can consist of any UTF-8
    characters.
    """

    input_token_limit: Optional[int] = FieldInfo(alias="inputTokenLimit", default=None)
    """Maximum number of input tokens allowed for this model."""

    max_temperature: Optional[float] = FieldInfo(alias="maxTemperature", default=None)
    """The maximum temperature this model can use."""

    output_token_limit: Optional[int] = FieldInfo(alias="outputTokenLimit", default=None)
    """Maximum number of output tokens available for this model."""

    supported_generation_methods: Optional[List[str]] = FieldInfo(alias="supportedGenerationMethods", default=None)
    """The model's supported generation methods.

    The corresponding API method names are defined as Pascal case strings, such as
    `generateMessage` and `generateContent`.
    """

    temperature: Optional[float] = None
    """Controls the randomness of the output.

    Values can range over `[0.0,max_temperature]`, inclusive. A higher value will
    produce responses that are more varied, while a value closer to `0.0` will
    typically result in less surprising responses from the model. This value
    specifies default to be used by the backend while making the call to the model.
    """

    thinking: Optional[bool] = None
    """Whether the model supports thinking."""

    top_k: Optional[int] = FieldInfo(alias="topK", default=None)
    """For Top-k sampling.

    Top-k sampling considers the set of `top_k` most probable tokens. This value
    specifies default to be used by the backend while making the call to the model.
    If empty, indicates the model doesn't use top-k sampling, and `top_k` isn't
    allowed as a generation parameter.
    """

    top_p: Optional[float] = FieldInfo(alias="topP", default=None)
    """
    For
    [Nucleus sampling](https://ai.google.dev/gemini-api/docs/prompting-strategies#top-p).

    Nucleus sampling considers the smallest set of tokens whose probability sum is
    at least `top_p`. This value specifies default to be used by the backend while
    making the call to the model.
    """
