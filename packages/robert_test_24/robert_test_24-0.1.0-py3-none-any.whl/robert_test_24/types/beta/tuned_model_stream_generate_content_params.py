# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo
from .content_param import ContentParam
from .tool_config_param import ToolConfigParam
from .voice_config_param import VoiceConfigParam
from .safety_setting_param import SafetySettingParam

__all__ = [
    "TunedModelStreamGenerateContentParams",
    "api_empty",
    "GenerationConfig",
    "GenerationConfigImageConfig",
    "GenerationConfigSpeechConfig",
    "GenerationConfigSpeechConfigMultiSpeakerVoiceConfig",
    "GenerationConfigSpeechConfigMultiSpeakerVoiceConfigSpeakerVoiceConfig",
    "GenerationConfigThinkingConfig",
]


class TunedModelStreamGenerateContentParams(TypedDict, total=False):
    contents: Required[Iterable[ContentParam]]
    """Required. The content of the current conversation with the model.

    For single-turn queries, this is a single instance. For multi-turn queries like
    [chat](https://ai.google.dev/gemini-api/docs/text-generation#chat), this is a
    repeated field that contains the conversation history and the latest request.
    """

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

    cached_content: Annotated[str, PropertyInfo(alias="cachedContent")]
    """Optional.

    The name of the content [cached](https://ai.google.dev/gemini-api/docs/caching)
    to use as context to serve the prediction. Format:
    `cachedContents/{cachedContent}`
    """

    generation_config: Annotated[GenerationConfig, PropertyInfo(alias="generationConfig")]
    """Configuration options for model generation and outputs.

    Not all parameters are configurable for every model.
    """

    safety_settings: Annotated[Iterable[SafetySettingParam], PropertyInfo(alias="safetySettings")]
    """Optional.

    A list of unique `SafetySetting` instances for blocking unsafe content.

    This will be enforced on the `GenerateContentRequest.contents` and
    `GenerateContentResponse.candidates`. There should not be more than one setting
    for each `SafetyCategory` type. The API will block any contents and responses
    that fail to meet the thresholds set by these settings. This list overrides the
    default settings for each `SafetyCategory` specified in the safety_settings. If
    there is no `SafetySetting` for a given `SafetyCategory` provided in the list,
    the API will use the default safety setting for that category. Harm categories
    HARM_CATEGORY_HATE_SPEECH, HARM_CATEGORY_SEXUALLY_EXPLICIT,
    HARM_CATEGORY_DANGEROUS_CONTENT, HARM_CATEGORY_HARASSMENT,
    HARM_CATEGORY_CIVIC_INTEGRITY are supported. Refer to the
    [guide](https://ai.google.dev/gemini-api/docs/safety-settings) for detailed
    information on available safety settings. Also refer to the
    [Safety guidance](https://ai.google.dev/gemini-api/docs/safety-guidance) to
    learn how to incorporate safety considerations in your AI applications.
    """

    system_instruction: Annotated[ContentParam, PropertyInfo(alias="systemInstruction")]
    """The base structured datatype containing multi-part content of a message.

    A `Content` includes a `role` field designating the producer of the `Content`
    and a `parts` field containing multi-part data that contains the content of the
    message turn.
    """

    tool_config: Annotated[ToolConfigParam, PropertyInfo(alias="toolConfig")]
    """
    The Tool configuration containing parameters for specifying `Tool` use in the
    request.
    """

    tools: Iterable["ToolParam"]
    """Optional. A list of `Tools` the `Model` may use to generate the next response.

    A `Tool` is a piece of code that enables the system to interact with external
    systems to perform an action, or set of actions, outside of knowledge and scope
    of the `Model`. Supported `Tool`s are `Function` and `code_execution`. Refer to
    the [Function calling](https://ai.google.dev/gemini-api/docs/function-calling)
    and the [Code execution](https://ai.google.dev/gemini-api/docs/code-execution)
    guides to learn more.
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""


class GenerationConfigImageConfig(TypedDict, total=False):
    """Config for image generation features."""

    aspect_ratio: Annotated[str, PropertyInfo(alias="aspectRatio")]
    """Optional.

    The aspect ratio of the image to generate. Supported aspect ratios: 1:1, 2:3,
    3:2, 3:4, 4:3, 9:16, 16:9, 21:9.

    If not specified, the model will choose a default aspect ratio based on any
    reference images provided.
    """


class GenerationConfigSpeechConfigMultiSpeakerVoiceConfigSpeakerVoiceConfig(TypedDict, total=False):
    """The configuration for a single speaker in a multi speaker setup."""

    speaker: Required[str]
    """Required. The name of the speaker to use. Should be the same as in the prompt."""

    voice_config: Required[Annotated[VoiceConfigParam, PropertyInfo(alias="voiceConfig")]]
    """The configuration for the voice to use."""


class GenerationConfigSpeechConfigMultiSpeakerVoiceConfig(TypedDict, total=False):
    """The configuration for the multi-speaker setup."""

    speaker_voice_configs: Required[
        Annotated[
            Iterable[GenerationConfigSpeechConfigMultiSpeakerVoiceConfigSpeakerVoiceConfig],
            PropertyInfo(alias="speakerVoiceConfigs"),
        ]
    ]
    """Required. All the enabled speaker voices."""


class GenerationConfigSpeechConfig(TypedDict, total=False):
    """The speech generation config."""

    language_code: Annotated[str, PropertyInfo(alias="languageCode")]
    """Optional. Language code (in BCP 47 format, e.g. "en-US") for speech synthesis.

    Valid values are: de-DE, en-AU, en-GB, en-IN, en-US, es-US, fr-FR, hi-IN, pt-BR,
    ar-XA, es-ES, fr-CA, id-ID, it-IT, ja-JP, tr-TR, vi-VN, bn-IN, gu-IN, kn-IN,
    ml-IN, mr-IN, ta-IN, te-IN, nl-NL, ko-KR, cmn-CN, pl-PL, ru-RU, and th-TH.
    """

    multi_speaker_voice_config: Annotated[
        GenerationConfigSpeechConfigMultiSpeakerVoiceConfig, PropertyInfo(alias="multiSpeakerVoiceConfig")
    ]
    """The configuration for the multi-speaker setup."""

    voice_config: Annotated[VoiceConfigParam, PropertyInfo(alias="voiceConfig")]
    """The configuration for the voice to use."""


class GenerationConfigThinkingConfig(TypedDict, total=False):
    """Config for thinking features."""

    include_thoughts: Annotated[bool, PropertyInfo(alias="includeThoughts")]
    """
    Indicates whether to include thoughts in the response. If true, thoughts are
    returned only when available.
    """

    thinking_budget: Annotated[int, PropertyInfo(alias="thinkingBudget")]
    """The number of thoughts tokens that the model should generate."""


class GenerationConfig(TypedDict, total=False):
    """Configuration options for model generation and outputs.

    Not all parameters
    are configurable for every model.
    """

    _response_json_schema: Annotated[object, PropertyInfo(alias="_responseJsonSchema")]
    """Optional.

    Output schema of the generated response. This is an alternative to
    `response_schema` that accepts [JSON Schema](https://json-schema.org/).

    If set, `response_schema` must be omitted, but `response_mime_type` is required.

    While the full JSON Schema may be sent, not all features are supported.
    Specifically, only the following properties are supported:

    - `$id`
    - `$defs`
    - `$ref`
    - `$anchor`
    - `type`
    - `format`
    - `title`
    - `description`
    - `enum` (for strings and numbers)
    - `items`
    - `prefixItems`
    - `minItems`
    - `maxItems`
    - `minimum`
    - `maximum`
    - `anyOf`
    - `oneOf` (interpreted the same as `anyOf`)
    - `properties`
    - `additionalProperties`
    - `required`

    The non-standard `propertyOrdering` property may also be set.

    Cyclic references are unrolled to a limited degree and, as such, may only be
    used within non-required properties. (Nullable properties are not sufficient.)
    If `$ref` is set on a sub-schema, no other properties, except for than those
    starting as a `$`, may be set.
    """

    candidate_count: Annotated[int, PropertyInfo(alias="candidateCount")]
    """Optional.

    Number of generated responses to return. If unset, this will default to 1.
    Please note that this doesn't work for previous generation models (Gemini 1.0
    family)
    """

    enable_enhanced_civic_answers: Annotated[bool, PropertyInfo(alias="enableEnhancedCivicAnswers")]
    """Optional.

    Enables enhanced civic answers. It may not be available for all models.
    """

    frequency_penalty: Annotated[float, PropertyInfo(alias="frequencyPenalty")]
    """Optional.

    Frequency penalty applied to the next token's logprobs, multiplied by the number
    of times each token has been seen in the respponse so far.

    A positive penalty will discourage the use of tokens that have already been
    used, proportional to the number of times the token has been used: The more a
    token is used, the more difficult it is for the model to use that token again
    increasing the vocabulary of responses.

    Caution: A _negative_ penalty will encourage the model to reuse tokens
    proportional to the number of times the token has been used. Small negative
    values will reduce the vocabulary of a response. Larger negative values will
    cause the model to start repeating a common token until it hits the
    max_output_tokens limit.
    """

    image_config: Annotated[GenerationConfigImageConfig, PropertyInfo(alias="imageConfig")]
    """Config for image generation features."""

    logprobs: int
    """Optional.

    Only valid if response_logprobs=True. This sets the number of top logprobs to
    return at each decoding step in the Candidate.logprobs_result. The number must
    be in the range of [0, 20].
    """

    max_output_tokens: Annotated[int, PropertyInfo(alias="maxOutputTokens")]
    """Optional. The maximum number of tokens to include in a response candidate.

    Note: The default value varies by model, see the `Model.output_token_limit`
    attribute of the `Model` returned from the `getModel` function.
    """

    media_resolution: Annotated[
        Literal[
            "MEDIA_RESOLUTION_UNSPECIFIED", "MEDIA_RESOLUTION_LOW", "MEDIA_RESOLUTION_MEDIUM", "MEDIA_RESOLUTION_HIGH"
        ],
        PropertyInfo(alias="mediaResolution"),
    ]
    """Optional. If specified, the media resolution specified will be used."""

    presence_penalty: Annotated[float, PropertyInfo(alias="presencePenalty")]
    """Optional.

    Presence penalty applied to the next token's logprobs if the token has already
    been seen in the response.

    This penalty is binary on/off and not dependant on the number of times the token
    is used (after the first). Use frequency_penalty for a penalty that increases
    with each use.

    A positive penalty will discourage the use of tokens that have already been used
    in the response, increasing the vocabulary.

    A negative penalty will encourage the use of tokens that have already been used
    in the response, decreasing the vocabulary.
    """

    response_json_schema: Annotated[object, PropertyInfo(alias="responseJsonSchema")]
    """Optional. An internal detail. Use `responseJsonSchema` rather than this field."""

    response_logprobs: Annotated[bool, PropertyInfo(alias="responseLogprobs")]
    """Optional. If true, export the logprobs results in response."""

    response_mime_type: Annotated[str, PropertyInfo(alias="responseMimeType")]
    """Optional.

    MIME type of the generated candidate text. Supported MIME types are:
    `text/plain`: (default) Text output. `application/json`: JSON response in the
    response candidates. `text/x.enum`: ENUM as a string response in the response
    candidates. Refer to the
    [docs](https://ai.google.dev/gemini-api/docs/prompting_with_media#plain_text_formats)
    for a list of all supported text MIME types.
    """

    response_modalities: Annotated[
        List[Literal["MODALITY_UNSPECIFIED", "TEXT", "IMAGE", "AUDIO"]], PropertyInfo(alias="responseModalities")
    ]
    """Optional.

    The requested modalities of the response. Represents the set of modalities that
    the model can return, and should be expected in the response. This is an exact
    match to the modalities of the response.

    A model may have multiple combinations of supported modalities. If the requested
    modalities do not match any of the supported combinations, an error will be
    returned.

    An empty list is equivalent to requesting only text.
    """

    response_schema: Annotated["SchemaParam", PropertyInfo(alias="responseSchema")]
    """
    The `Schema` object allows the definition of input and output data types. These
    types can be objects, but also primitives and arrays. Represents a select subset
    of an [OpenAPI 3.0 schema object](https://spec.openapis.org/oas/v3.0.3#schema).
    """

    seed: int
    """Optional.

    Seed used in decoding. If not set, the request uses a randomly generated seed.
    """

    speech_config: Annotated[GenerationConfigSpeechConfig, PropertyInfo(alias="speechConfig")]
    """The speech generation config."""

    stop_sequences: Annotated[SequenceNotStr[str], PropertyInfo(alias="stopSequences")]
    """Optional.

    The set of character sequences (up to 5) that will stop output generation. If
    specified, the API will stop at the first appearance of a `stop_sequence`. The
    stop sequence will not be included as part of the response.
    """

    temperature: float
    """Optional. Controls the randomness of the output.

    Note: The default value varies by model, see the `Model.temperature` attribute
    of the `Model` returned from the `getModel` function.

    Values can range from [0.0, 2.0].
    """

    thinking_config: Annotated[GenerationConfigThinkingConfig, PropertyInfo(alias="thinkingConfig")]
    """Config for thinking features."""

    top_k: Annotated[int, PropertyInfo(alias="topK")]
    """Optional. The maximum number of tokens to consider when sampling.

    Gemini models use Top-p (nucleus) sampling or a combination of Top-k and nucleus
    sampling. Top-k sampling considers the set of `top_k` most probable tokens.
    Models running with nucleus sampling don't allow top_k setting.

    Note: The default value varies by `Model` and is specified by the`Model.top_p`
    attribute returned from the `getModel` function. An empty `top_k` attribute
    indicates that the model doesn't apply top-k sampling and doesn't allow setting
    `top_k` on requests.
    """

    top_p: Annotated[float, PropertyInfo(alias="topP")]
    """Optional.

    The maximum cumulative probability of tokens to consider when sampling.

    The model uses combined Top-k and Top-p (nucleus) sampling.

    Tokens are sorted based on their assigned probabilities so that only the most
    likely tokens are considered. Top-k sampling directly limits the maximum number
    of tokens to consider, while Nucleus sampling limits the number of tokens based
    on the cumulative probability.

    Note: The default value varies by `Model` and is specified by the`Model.top_p`
    attribute returned from the `getModel` function. An empty `top_k` attribute
    indicates that the model doesn't apply top-k sampling and doesn't allow setting
    `top_k` on requests.
    """


from .tool_param import ToolParam
from .schema_param import SchemaParam
