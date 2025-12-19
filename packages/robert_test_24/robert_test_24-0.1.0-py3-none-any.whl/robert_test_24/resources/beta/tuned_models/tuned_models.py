# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from .operations import (
    OperationsResource,
    AsyncOperationsResource,
    OperationsResourceWithRawResponse,
    AsyncOperationsResourceWithRawResponse,
    OperationsResourceWithStreamingResponse,
    AsyncOperationsResourceWithStreamingResponse,
)
from .permissions import (
    PermissionsResource,
    AsyncPermissionsResource,
    PermissionsResourceWithRawResponse,
    AsyncPermissionsResourceWithRawResponse,
    PermissionsResourceWithStreamingResponse,
    AsyncPermissionsResourceWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....types.beta import (
    tuned_model_generate_text_params,
    tuned_model_generate_content_params,
    tuned_model_list_tuned_models_params,
    tuned_model_create_tuned_model_params,
    tuned_model_delete_tuned_model_params,
    tuned_model_transfer_ownership_params,
    tuned_model_update_tuned_model_params,
    tuned_model_retrieve_tuned_model_params,
    tuned_model_batch_generate_content_params,
    tuned_model_stream_generate_content_params,
    tuned_model_async_batch_embed_content_params,
)
from ...._base_client import make_request_options
from ....types.beta.tool_param import ToolParam
from ....types.beta.tuned_model import TunedModel
from ....types.beta.content_param import ContentParam
from ....types.beta.generate_text import GenerateText
from ....types.beta.text_prompt_param import TextPromptParam
from ....types.beta.tool_config_param import ToolConfigParam
from ....types.beta.safety_setting_param import SafetySettingParam
from ....types.beta.embed_content_batch_param import EmbedContentBatchParam
from ....types.beta.generate_content_response import GenerateContentResponse
from ....types.beta.generate_content_batch_param import GenerateContentBatchParam
from ....types.beta.batch_generate_content_operation import BatchGenerateContentOperation
from ....types.beta.async_batch_embed_content_operation import AsyncBatchEmbedContentOperation
from ....types.beta.tuned_model_list_tuned_models_response import TunedModelListTunedModelsResponse
from ....types.beta.tuned_model_create_tuned_model_response import TunedModelCreateTunedModelResponse

__all__ = ["TunedModelsResource", "AsyncTunedModelsResource"]


class TunedModelsResource(SyncAPIResource):
    @cached_property
    def operations(self) -> OperationsResource:
        return OperationsResource(self._client)

    @cached_property
    def permissions(self) -> PermissionsResource:
        return PermissionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> TunedModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return TunedModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TunedModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return TunedModelsResourceWithStreamingResponse(self)

    def async_batch_embed_content(
        self,
        tuned_model: str,
        *,
        batch: EmbedContentBatchParam,
        api_empty: tuned_model_async_batch_embed_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncBatchEmbedContentOperation:
        """Enqueues a batch of `EmbedContent` requests for batch processing.

        We have a
        `BatchEmbedContents` handler in `GenerativeService`, but it was synchronized. So
        we name this one to be `Async` to avoid confusion.

        Args:
          batch: A resource representing a batch of `EmbedContent` requests.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return self._post(
            f"/v1beta/tunedModels/{tuned_model}:asyncBatchEmbedContent",
            body=maybe_transform(
                {"batch": batch}, tuned_model_async_batch_embed_content_params.TunedModelAsyncBatchEmbedContentParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_async_batch_embed_content_params.TunedModelAsyncBatchEmbedContentParams,
                ),
            ),
            cast_to=AsyncBatchEmbedContentOperation,
        )

    def batch_generate_content(
        self,
        tuned_model: str,
        *,
        batch: GenerateContentBatchParam,
        api_empty: tuned_model_batch_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchGenerateContentOperation:
        """
        Enqueues a batch of `GenerateContent` requests for batch processing.

        Args:
          batch: A resource representing a batch of `GenerateContent` requests.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return self._post(
            f"/v1beta/tunedModels/{tuned_model}:batchGenerateContent",
            body=maybe_transform(
                {"batch": batch}, tuned_model_batch_generate_content_params.TunedModelBatchGenerateContentParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_batch_generate_content_params.TunedModelBatchGenerateContentParams,
                ),
            ),
            cast_to=BatchGenerateContentOperation,
        )

    def create_tuned_model(
        self,
        *,
        tuning_task: tuned_model_create_tuned_model_params.TuningTask,
        api_empty: tuned_model_create_tuned_model_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        tuned_model_id: str | Omit = omit,
        base_model: str | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        reader_project_numbers: SequenceNotStr[str] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        tuned_model_source: tuned_model_create_tuned_model_params.TunedModelSource | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TunedModelCreateTunedModelResponse:
        """Creates a tuned model.

        Check intermediate tuning progress (if any) through the
        [google.longrunning.Operations] service.

        Access status and results through the Operations service. Example: GET
        /v1/tunedModels/az2mb0bpw6i/operations/000-111-222

        Args:
          tuning_task: Tuning tasks that create tuned models.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          tuned_model_id: Optional. The unique id for the tuned model if specified. This value should be
              up to 40 characters, the first character must be a letter, the last could be a
              letter or a number. The id must match the regular expression:
              `[a-z]([a-z0-9-]{0,38}[a-z0-9])?`.

          base_model:
              Immutable. The name of the `Model` to tune. Example:
              `models/gemini-1.5-flash-001`

          description: Optional. A short description of this model.

          display_name: Optional. The name to display for this model in user interfaces. The display
              name must be up to 40 characters including spaces.

          reader_project_numbers: Optional. List of project numbers that have read access to the tuned model.

          temperature: Optional. Controls the randomness of the output.

              Values can range over `[0.0,1.0]`, inclusive. A value closer to `1.0` will
              produce responses that are more varied, while a value closer to `0.0` will
              typically result in less surprising responses from the model.

              This value specifies default to be the one used by the base model while creating
              the model.

          top_k: Optional. For Top-k sampling.

              Top-k sampling considers the set of `top_k` most probable tokens. This value
              specifies default to be used by the backend while making the call to the model.

              This value specifies default to be the one used by the base model while creating
              the model.

          top_p: Optional. For Nucleus sampling.

              Nucleus sampling considers the smallest set of tokens whose probability sum is
              at least `top_p`.

              This value specifies default to be the one used by the base model while creating
              the model.

          tuned_model_source: Tuned model as a source for training a new model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1beta/tunedModels",
            body=maybe_transform(
                {
                    "tuning_task": tuning_task,
                    "base_model": base_model,
                    "description": description,
                    "display_name": display_name,
                    "reader_project_numbers": reader_project_numbers,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                    "tuned_model_source": tuned_model_source,
                },
                tuned_model_create_tuned_model_params.TunedModelCreateTunedModelParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                        "tuned_model_id": tuned_model_id,
                    },
                    tuned_model_create_tuned_model_params.TunedModelCreateTunedModelParams,
                ),
            ),
            cast_to=TunedModelCreateTunedModelResponse,
        )

    def delete_tuned_model(
        self,
        tuned_model: str,
        *,
        api_empty: tuned_model_delete_tuned_model_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Deletes a tuned model.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return self._delete(
            f"/v1beta/tunedModels/{tuned_model}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_delete_tuned_model_params.TunedModelDeleteTunedModelParams,
                ),
            ),
            cast_to=object,
        )

    def generate_content(
        self,
        tuned_model: str,
        *,
        contents: Iterable[ContentParam],
        model: str,
        api_empty: tuned_model_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: tuned_model_generate_content_params.GenerationConfig | Omit = omit,
        safety_settings: Iterable[SafetySettingParam] | Omit = omit,
        system_instruction: ContentParam | Omit = omit,
        tool_config: ToolConfigParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GenerateContentResponse:
        """Generates a model response given an input `GenerateContentRequest`.

        Refer to the
        [text generation guide](https://ai.google.dev/gemini-api/docs/text-generation)
        for detailed usage information. Input capabilities differ between models,
        including tuned models. Refer to the
        [model guide](https://ai.google.dev/gemini-api/docs/models/gemini) and
        [tuning guide](https://ai.google.dev/gemini-api/docs/model-tuning) for details.

        Args:
          contents: Required. The content of the current conversation with the model.

              For single-turn queries, this is a single instance. For multi-turn queries like
              [chat](https://ai.google.dev/gemini-api/docs/text-generation#chat), this is a
              repeated field that contains the conversation history and the latest request.

          model: Required. The name of the `Model` to use for generating the completion.

              Format: `models/{model}`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          cached_content: Optional. The name of the content
              [cached](https://ai.google.dev/gemini-api/docs/caching) to use as context to
              serve the prediction. Format: `cachedContents/{cachedContent}`

          generation_config: Configuration options for model generation and outputs. Not all parameters are
              configurable for every model.

          safety_settings: Optional. A list of unique `SafetySetting` instances for blocking unsafe
              content.

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

          system_instruction: The base structured datatype containing multi-part content of a message.

              A `Content` includes a `role` field designating the producer of the `Content`
              and a `parts` field containing multi-part data that contains the content of the
              message turn.

          tool_config: The Tool configuration containing parameters for specifying `Tool` use in the
              request.

          tools: Optional. A list of `Tools` the `Model` may use to generate the next response.

              A `Tool` is a piece of code that enables the system to interact with external
              systems to perform an action, or set of actions, outside of knowledge and scope
              of the `Model`. Supported `Tool`s are `Function` and `code_execution`. Refer to
              the [Function calling](https://ai.google.dev/gemini-api/docs/function-calling)
              and the [Code execution](https://ai.google.dev/gemini-api/docs/code-execution)
              guides to learn more.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return self._post(
            f"/v1beta/tunedModels/{tuned_model}:generateContent",
            body=maybe_transform(
                {
                    "contents": contents,
                    "model": model,
                    "cached_content": cached_content,
                    "generation_config": generation_config,
                    "safety_settings": safety_settings,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                },
                tuned_model_generate_content_params.TunedModelGenerateContentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_generate_content_params.TunedModelGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )

    def generate_text(
        self,
        tuned_model: str,
        *,
        prompt: TextPromptParam,
        api_empty: tuned_model_generate_text_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        candidate_count: int | Omit = omit,
        max_output_tokens: int | Omit = omit,
        safety_settings: Iterable[SafetySettingParam] | Omit = omit,
        stop_sequences: SequenceNotStr[str] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GenerateText:
        """
        Generates a response from the model given an input message.

        Args:
          prompt: Text given to the model as a prompt.

              The Model will use this TextPrompt to Generate a text completion.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          candidate_count: Optional. Number of generated responses to return.

              This value must be between [1, 8], inclusive. If unset, this will default to 1.

          max_output_tokens: Optional. The maximum number of tokens to include in a candidate.

              If unset, this will default to output_token_limit specified in the `Model`
              specification.

          safety_settings: Optional. A list of unique `SafetySetting` instances for blocking unsafe
              content.

              that will be enforced on the `GenerateTextRequest.prompt` and
              `GenerateTextResponse.candidates`. There should not be more than one setting for
              each `SafetyCategory` type. The API will block any prompts and responses that
              fail to meet the thresholds set by these settings. This list overrides the
              default settings for each `SafetyCategory` specified in the safety_settings. If
              there is no `SafetySetting` for a given `SafetyCategory` provided in the list,
              the API will use the default safety setting for that category. Harm categories
              HARM_CATEGORY_DEROGATORY, HARM_CATEGORY_TOXICITY, HARM_CATEGORY_VIOLENCE,
              HARM_CATEGORY_SEXUAL, HARM_CATEGORY_MEDICAL, HARM_CATEGORY_DANGEROUS are
              supported in text service.

          stop_sequences: The set of character sequences (up to 5) that will stop output generation. If
              specified, the API will stop at the first appearance of a stop sequence. The
              stop sequence will not be included as part of the response.

          temperature: Optional. Controls the randomness of the output. Note: The default value varies
              by model, see the `Model.temperature` attribute of the `Model` returned the
              `getModel` function.

              Values can range from [0.0,1.0], inclusive. A value closer to 1.0 will produce
              responses that are more varied and creative, while a value closer to 0.0 will
              typically result in more straightforward responses from the model.

          top_k: Optional. The maximum number of tokens to consider when sampling.

              The model uses combined Top-k and nucleus sampling.

              Top-k sampling considers the set of `top_k` most probable tokens. Defaults
              to 40.

              Note: The default value varies by model, see the `Model.top_k` attribute of the
              `Model` returned the `getModel` function.

          top_p: Optional. The maximum cumulative probability of tokens to consider when
              sampling.

              The model uses combined Top-k and nucleus sampling.

              Tokens are sorted based on their assigned probabilities so that only the most
              likely tokens are considered. Top-k sampling directly limits the maximum number
              of tokens to consider, while Nucleus sampling limits number of tokens based on
              the cumulative probability.

              Note: The default value varies by model, see the `Model.top_p` attribute of the
              `Model` returned the `getModel` function.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return self._post(
            f"/v1beta/tunedModels/{tuned_model}:generateText",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "candidate_count": candidate_count,
                    "max_output_tokens": max_output_tokens,
                    "safety_settings": safety_settings,
                    "stop_sequences": stop_sequences,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                tuned_model_generate_text_params.TunedModelGenerateTextParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_generate_text_params.TunedModelGenerateTextParams,
                ),
            ),
            cast_to=GenerateText,
        )

    def list_tuned_models(
        self,
        *,
        api_empty: tuned_model_list_tuned_models_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        filter: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TunedModelListTunedModelsResponse:
        """
        Lists created tuned models.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          filter: Optional. A filter is a full text search over the tuned model's description and
              display name. By default, results will not include tuned models shared with
              everyone.

              Additional operators:

              - owner:me
              - writers:me
              - readers:me
              - readers:everyone

              Examples: "owner:me" returns all tuned models to which caller has owner role
              "readers:me" returns all tuned models to which caller has reader role
              "readers:everyone" returns all tuned models that are shared with everyone

          page_size: Optional. The maximum number of `TunedModels` to return (per page). The service
              may return fewer tuned models.

              If unspecified, at most 10 tuned models will be returned. This method returns at
              most 1000 models per page, even if you pass a larger page_size.

          page_token: Optional. A page token, received from a previous `ListTunedModels` call.

              Provide the `page_token` returned by one request as an argument to the next
              request to retrieve the next page.

              When paginating, all other parameters provided to `ListTunedModels` must match
              the call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1beta/tunedModels",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                        "filter": filter,
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                    tuned_model_list_tuned_models_params.TunedModelListTunedModelsParams,
                ),
            ),
            cast_to=TunedModelListTunedModelsResponse,
        )

    def retrieve_tuned_model(
        self,
        tuned_model: str,
        *,
        api_empty: tuned_model_retrieve_tuned_model_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TunedModel:
        """
        Gets information about a specific TunedModel.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return self._get(
            f"/v1beta/tunedModels/{tuned_model}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_retrieve_tuned_model_params.TunedModelRetrieveTunedModelParams,
                ),
            ),
            cast_to=TunedModel,
        )

    def stream_generate_content(
        self,
        tuned_model: str,
        *,
        contents: Iterable[ContentParam],
        model: str,
        api_empty: tuned_model_stream_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: tuned_model_stream_generate_content_params.GenerationConfig | Omit = omit,
        safety_settings: Iterable[SafetySettingParam] | Omit = omit,
        system_instruction: ContentParam | Omit = omit,
        tool_config: ToolConfigParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GenerateContentResponse:
        """
        Generates a
        [streamed response](https://ai.google.dev/gemini-api/docs/text-generation?lang=python#generate-a-text-stream)
        from the model given an input `GenerateContentRequest`.

        Args:
          contents: Required. The content of the current conversation with the model.

              For single-turn queries, this is a single instance. For multi-turn queries like
              [chat](https://ai.google.dev/gemini-api/docs/text-generation#chat), this is a
              repeated field that contains the conversation history and the latest request.

          model: Required. The name of the `Model` to use for generating the completion.

              Format: `models/{model}`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          cached_content: Optional. The name of the content
              [cached](https://ai.google.dev/gemini-api/docs/caching) to use as context to
              serve the prediction. Format: `cachedContents/{cachedContent}`

          generation_config: Configuration options for model generation and outputs. Not all parameters are
              configurable for every model.

          safety_settings: Optional. A list of unique `SafetySetting` instances for blocking unsafe
              content.

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

          system_instruction: The base structured datatype containing multi-part content of a message.

              A `Content` includes a `role` field designating the producer of the `Content`
              and a `parts` field containing multi-part data that contains the content of the
              message turn.

          tool_config: The Tool configuration containing parameters for specifying `Tool` use in the
              request.

          tools: Optional. A list of `Tools` the `Model` may use to generate the next response.

              A `Tool` is a piece of code that enables the system to interact with external
              systems to perform an action, or set of actions, outside of knowledge and scope
              of the `Model`. Supported `Tool`s are `Function` and `code_execution`. Refer to
              the [Function calling](https://ai.google.dev/gemini-api/docs/function-calling)
              and the [Code execution](https://ai.google.dev/gemini-api/docs/code-execution)
              guides to learn more.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return self._post(
            f"/v1beta/tunedModels/{tuned_model}:streamGenerateContent",
            body=maybe_transform(
                {
                    "contents": contents,
                    "model": model,
                    "cached_content": cached_content,
                    "generation_config": generation_config,
                    "safety_settings": safety_settings,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                },
                tuned_model_stream_generate_content_params.TunedModelStreamGenerateContentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_stream_generate_content_params.TunedModelStreamGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )

    def transfer_ownership(
        self,
        tuned_model: str,
        *,
        email_address: str,
        api_empty: tuned_model_transfer_ownership_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Transfers ownership of the tuned model.

        This is the only way to change ownership
        of the tuned model. The current owner will be downgraded to writer role.

        Args:
          email_address: Required. The email address of the user to whom the tuned model is being
              transferred to.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return self._post(
            f"/v1beta/tunedModels/{tuned_model}:transferOwnership",
            body=maybe_transform(
                {"email_address": email_address},
                tuned_model_transfer_ownership_params.TunedModelTransferOwnershipParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_transfer_ownership_params.TunedModelTransferOwnershipParams,
                ),
            ),
            cast_to=object,
        )

    def update_tuned_model(
        self,
        tuned_model: str,
        *,
        tuning_task: tuned_model_update_tuned_model_params.TuningTask,
        api_empty: tuned_model_update_tuned_model_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        update_mask: str | Omit = omit,
        base_model: str | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        reader_project_numbers: SequenceNotStr[str] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        tuned_model_source: tuned_model_update_tuned_model_params.TunedModelSource | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TunedModel:
        """
        Updates a tuned model.

        Args:
          tuning_task: Tuning tasks that create tuned models.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          update_mask: Optional. The list of fields to update.

          base_model:
              Immutable. The name of the `Model` to tune. Example:
              `models/gemini-1.5-flash-001`

          description: Optional. A short description of this model.

          display_name: Optional. The name to display for this model in user interfaces. The display
              name must be up to 40 characters including spaces.

          reader_project_numbers: Optional. List of project numbers that have read access to the tuned model.

          temperature: Optional. Controls the randomness of the output.

              Values can range over `[0.0,1.0]`, inclusive. A value closer to `1.0` will
              produce responses that are more varied, while a value closer to `0.0` will
              typically result in less surprising responses from the model.

              This value specifies default to be the one used by the base model while creating
              the model.

          top_k: Optional. For Top-k sampling.

              Top-k sampling considers the set of `top_k` most probable tokens. This value
              specifies default to be used by the backend while making the call to the model.

              This value specifies default to be the one used by the base model while creating
              the model.

          top_p: Optional. For Nucleus sampling.

              Nucleus sampling considers the smallest set of tokens whose probability sum is
              at least `top_p`.

              This value specifies default to be the one used by the base model while creating
              the model.

          tuned_model_source: Tuned model as a source for training a new model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return self._patch(
            f"/v1beta/tunedModels/{tuned_model}",
            body=maybe_transform(
                {
                    "tuning_task": tuning_task,
                    "base_model": base_model,
                    "description": description,
                    "display_name": display_name,
                    "reader_project_numbers": reader_project_numbers,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                    "tuned_model_source": tuned_model_source,
                },
                tuned_model_update_tuned_model_params.TunedModelUpdateTunedModelParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                        "update_mask": update_mask,
                    },
                    tuned_model_update_tuned_model_params.TunedModelUpdateTunedModelParams,
                ),
            ),
            cast_to=TunedModel,
        )


class AsyncTunedModelsResource(AsyncAPIResource):
    @cached_property
    def operations(self) -> AsyncOperationsResource:
        return AsyncOperationsResource(self._client)

    @cached_property
    def permissions(self) -> AsyncPermissionsResource:
        return AsyncPermissionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTunedModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTunedModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTunedModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncTunedModelsResourceWithStreamingResponse(self)

    async def async_batch_embed_content(
        self,
        tuned_model: str,
        *,
        batch: EmbedContentBatchParam,
        api_empty: tuned_model_async_batch_embed_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncBatchEmbedContentOperation:
        """Enqueues a batch of `EmbedContent` requests for batch processing.

        We have a
        `BatchEmbedContents` handler in `GenerativeService`, but it was synchronized. So
        we name this one to be `Async` to avoid confusion.

        Args:
          batch: A resource representing a batch of `EmbedContent` requests.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return await self._post(
            f"/v1beta/tunedModels/{tuned_model}:asyncBatchEmbedContent",
            body=await async_maybe_transform(
                {"batch": batch}, tuned_model_async_batch_embed_content_params.TunedModelAsyncBatchEmbedContentParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_async_batch_embed_content_params.TunedModelAsyncBatchEmbedContentParams,
                ),
            ),
            cast_to=AsyncBatchEmbedContentOperation,
        )

    async def batch_generate_content(
        self,
        tuned_model: str,
        *,
        batch: GenerateContentBatchParam,
        api_empty: tuned_model_batch_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchGenerateContentOperation:
        """
        Enqueues a batch of `GenerateContent` requests for batch processing.

        Args:
          batch: A resource representing a batch of `GenerateContent` requests.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return await self._post(
            f"/v1beta/tunedModels/{tuned_model}:batchGenerateContent",
            body=await async_maybe_transform(
                {"batch": batch}, tuned_model_batch_generate_content_params.TunedModelBatchGenerateContentParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_batch_generate_content_params.TunedModelBatchGenerateContentParams,
                ),
            ),
            cast_to=BatchGenerateContentOperation,
        )

    async def create_tuned_model(
        self,
        *,
        tuning_task: tuned_model_create_tuned_model_params.TuningTask,
        api_empty: tuned_model_create_tuned_model_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        tuned_model_id: str | Omit = omit,
        base_model: str | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        reader_project_numbers: SequenceNotStr[str] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        tuned_model_source: tuned_model_create_tuned_model_params.TunedModelSource | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TunedModelCreateTunedModelResponse:
        """Creates a tuned model.

        Check intermediate tuning progress (if any) through the
        [google.longrunning.Operations] service.

        Access status and results through the Operations service. Example: GET
        /v1/tunedModels/az2mb0bpw6i/operations/000-111-222

        Args:
          tuning_task: Tuning tasks that create tuned models.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          tuned_model_id: Optional. The unique id for the tuned model if specified. This value should be
              up to 40 characters, the first character must be a letter, the last could be a
              letter or a number. The id must match the regular expression:
              `[a-z]([a-z0-9-]{0,38}[a-z0-9])?`.

          base_model:
              Immutable. The name of the `Model` to tune. Example:
              `models/gemini-1.5-flash-001`

          description: Optional. A short description of this model.

          display_name: Optional. The name to display for this model in user interfaces. The display
              name must be up to 40 characters including spaces.

          reader_project_numbers: Optional. List of project numbers that have read access to the tuned model.

          temperature: Optional. Controls the randomness of the output.

              Values can range over `[0.0,1.0]`, inclusive. A value closer to `1.0` will
              produce responses that are more varied, while a value closer to `0.0` will
              typically result in less surprising responses from the model.

              This value specifies default to be the one used by the base model while creating
              the model.

          top_k: Optional. For Top-k sampling.

              Top-k sampling considers the set of `top_k` most probable tokens. This value
              specifies default to be used by the backend while making the call to the model.

              This value specifies default to be the one used by the base model while creating
              the model.

          top_p: Optional. For Nucleus sampling.

              Nucleus sampling considers the smallest set of tokens whose probability sum is
              at least `top_p`.

              This value specifies default to be the one used by the base model while creating
              the model.

          tuned_model_source: Tuned model as a source for training a new model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1beta/tunedModels",
            body=await async_maybe_transform(
                {
                    "tuning_task": tuning_task,
                    "base_model": base_model,
                    "description": description,
                    "display_name": display_name,
                    "reader_project_numbers": reader_project_numbers,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                    "tuned_model_source": tuned_model_source,
                },
                tuned_model_create_tuned_model_params.TunedModelCreateTunedModelParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                        "tuned_model_id": tuned_model_id,
                    },
                    tuned_model_create_tuned_model_params.TunedModelCreateTunedModelParams,
                ),
            ),
            cast_to=TunedModelCreateTunedModelResponse,
        )

    async def delete_tuned_model(
        self,
        tuned_model: str,
        *,
        api_empty: tuned_model_delete_tuned_model_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Deletes a tuned model.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return await self._delete(
            f"/v1beta/tunedModels/{tuned_model}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_delete_tuned_model_params.TunedModelDeleteTunedModelParams,
                ),
            ),
            cast_to=object,
        )

    async def generate_content(
        self,
        tuned_model: str,
        *,
        contents: Iterable[ContentParam],
        model: str,
        api_empty: tuned_model_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: tuned_model_generate_content_params.GenerationConfig | Omit = omit,
        safety_settings: Iterable[SafetySettingParam] | Omit = omit,
        system_instruction: ContentParam | Omit = omit,
        tool_config: ToolConfigParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GenerateContentResponse:
        """Generates a model response given an input `GenerateContentRequest`.

        Refer to the
        [text generation guide](https://ai.google.dev/gemini-api/docs/text-generation)
        for detailed usage information. Input capabilities differ between models,
        including tuned models. Refer to the
        [model guide](https://ai.google.dev/gemini-api/docs/models/gemini) and
        [tuning guide](https://ai.google.dev/gemini-api/docs/model-tuning) for details.

        Args:
          contents: Required. The content of the current conversation with the model.

              For single-turn queries, this is a single instance. For multi-turn queries like
              [chat](https://ai.google.dev/gemini-api/docs/text-generation#chat), this is a
              repeated field that contains the conversation history and the latest request.

          model: Required. The name of the `Model` to use for generating the completion.

              Format: `models/{model}`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          cached_content: Optional. The name of the content
              [cached](https://ai.google.dev/gemini-api/docs/caching) to use as context to
              serve the prediction. Format: `cachedContents/{cachedContent}`

          generation_config: Configuration options for model generation and outputs. Not all parameters are
              configurable for every model.

          safety_settings: Optional. A list of unique `SafetySetting` instances for blocking unsafe
              content.

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

          system_instruction: The base structured datatype containing multi-part content of a message.

              A `Content` includes a `role` field designating the producer of the `Content`
              and a `parts` field containing multi-part data that contains the content of the
              message turn.

          tool_config: The Tool configuration containing parameters for specifying `Tool` use in the
              request.

          tools: Optional. A list of `Tools` the `Model` may use to generate the next response.

              A `Tool` is a piece of code that enables the system to interact with external
              systems to perform an action, or set of actions, outside of knowledge and scope
              of the `Model`. Supported `Tool`s are `Function` and `code_execution`. Refer to
              the [Function calling](https://ai.google.dev/gemini-api/docs/function-calling)
              and the [Code execution](https://ai.google.dev/gemini-api/docs/code-execution)
              guides to learn more.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return await self._post(
            f"/v1beta/tunedModels/{tuned_model}:generateContent",
            body=await async_maybe_transform(
                {
                    "contents": contents,
                    "model": model,
                    "cached_content": cached_content,
                    "generation_config": generation_config,
                    "safety_settings": safety_settings,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                },
                tuned_model_generate_content_params.TunedModelGenerateContentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_generate_content_params.TunedModelGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )

    async def generate_text(
        self,
        tuned_model: str,
        *,
        prompt: TextPromptParam,
        api_empty: tuned_model_generate_text_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        candidate_count: int | Omit = omit,
        max_output_tokens: int | Omit = omit,
        safety_settings: Iterable[SafetySettingParam] | Omit = omit,
        stop_sequences: SequenceNotStr[str] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GenerateText:
        """
        Generates a response from the model given an input message.

        Args:
          prompt: Text given to the model as a prompt.

              The Model will use this TextPrompt to Generate a text completion.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          candidate_count: Optional. Number of generated responses to return.

              This value must be between [1, 8], inclusive. If unset, this will default to 1.

          max_output_tokens: Optional. The maximum number of tokens to include in a candidate.

              If unset, this will default to output_token_limit specified in the `Model`
              specification.

          safety_settings: Optional. A list of unique `SafetySetting` instances for blocking unsafe
              content.

              that will be enforced on the `GenerateTextRequest.prompt` and
              `GenerateTextResponse.candidates`. There should not be more than one setting for
              each `SafetyCategory` type. The API will block any prompts and responses that
              fail to meet the thresholds set by these settings. This list overrides the
              default settings for each `SafetyCategory` specified in the safety_settings. If
              there is no `SafetySetting` for a given `SafetyCategory` provided in the list,
              the API will use the default safety setting for that category. Harm categories
              HARM_CATEGORY_DEROGATORY, HARM_CATEGORY_TOXICITY, HARM_CATEGORY_VIOLENCE,
              HARM_CATEGORY_SEXUAL, HARM_CATEGORY_MEDICAL, HARM_CATEGORY_DANGEROUS are
              supported in text service.

          stop_sequences: The set of character sequences (up to 5) that will stop output generation. If
              specified, the API will stop at the first appearance of a stop sequence. The
              stop sequence will not be included as part of the response.

          temperature: Optional. Controls the randomness of the output. Note: The default value varies
              by model, see the `Model.temperature` attribute of the `Model` returned the
              `getModel` function.

              Values can range from [0.0,1.0], inclusive. A value closer to 1.0 will produce
              responses that are more varied and creative, while a value closer to 0.0 will
              typically result in more straightforward responses from the model.

          top_k: Optional. The maximum number of tokens to consider when sampling.

              The model uses combined Top-k and nucleus sampling.

              Top-k sampling considers the set of `top_k` most probable tokens. Defaults
              to 40.

              Note: The default value varies by model, see the `Model.top_k` attribute of the
              `Model` returned the `getModel` function.

          top_p: Optional. The maximum cumulative probability of tokens to consider when
              sampling.

              The model uses combined Top-k and nucleus sampling.

              Tokens are sorted based on their assigned probabilities so that only the most
              likely tokens are considered. Top-k sampling directly limits the maximum number
              of tokens to consider, while Nucleus sampling limits number of tokens based on
              the cumulative probability.

              Note: The default value varies by model, see the `Model.top_p` attribute of the
              `Model` returned the `getModel` function.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return await self._post(
            f"/v1beta/tunedModels/{tuned_model}:generateText",
            body=await async_maybe_transform(
                {
                    "prompt": prompt,
                    "candidate_count": candidate_count,
                    "max_output_tokens": max_output_tokens,
                    "safety_settings": safety_settings,
                    "stop_sequences": stop_sequences,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                tuned_model_generate_text_params.TunedModelGenerateTextParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_generate_text_params.TunedModelGenerateTextParams,
                ),
            ),
            cast_to=GenerateText,
        )

    async def list_tuned_models(
        self,
        *,
        api_empty: tuned_model_list_tuned_models_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        filter: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TunedModelListTunedModelsResponse:
        """
        Lists created tuned models.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          filter: Optional. A filter is a full text search over the tuned model's description and
              display name. By default, results will not include tuned models shared with
              everyone.

              Additional operators:

              - owner:me
              - writers:me
              - readers:me
              - readers:everyone

              Examples: "owner:me" returns all tuned models to which caller has owner role
              "readers:me" returns all tuned models to which caller has reader role
              "readers:everyone" returns all tuned models that are shared with everyone

          page_size: Optional. The maximum number of `TunedModels` to return (per page). The service
              may return fewer tuned models.

              If unspecified, at most 10 tuned models will be returned. This method returns at
              most 1000 models per page, even if you pass a larger page_size.

          page_token: Optional. A page token, received from a previous `ListTunedModels` call.

              Provide the `page_token` returned by one request as an argument to the next
              request to retrieve the next page.

              When paginating, all other parameters provided to `ListTunedModels` must match
              the call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1beta/tunedModels",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                        "filter": filter,
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                    tuned_model_list_tuned_models_params.TunedModelListTunedModelsParams,
                ),
            ),
            cast_to=TunedModelListTunedModelsResponse,
        )

    async def retrieve_tuned_model(
        self,
        tuned_model: str,
        *,
        api_empty: tuned_model_retrieve_tuned_model_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TunedModel:
        """
        Gets information about a specific TunedModel.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return await self._get(
            f"/v1beta/tunedModels/{tuned_model}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_retrieve_tuned_model_params.TunedModelRetrieveTunedModelParams,
                ),
            ),
            cast_to=TunedModel,
        )

    async def stream_generate_content(
        self,
        tuned_model: str,
        *,
        contents: Iterable[ContentParam],
        model: str,
        api_empty: tuned_model_stream_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: tuned_model_stream_generate_content_params.GenerationConfig | Omit = omit,
        safety_settings: Iterable[SafetySettingParam] | Omit = omit,
        system_instruction: ContentParam | Omit = omit,
        tool_config: ToolConfigParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GenerateContentResponse:
        """
        Generates a
        [streamed response](https://ai.google.dev/gemini-api/docs/text-generation?lang=python#generate-a-text-stream)
        from the model given an input `GenerateContentRequest`.

        Args:
          contents: Required. The content of the current conversation with the model.

              For single-turn queries, this is a single instance. For multi-turn queries like
              [chat](https://ai.google.dev/gemini-api/docs/text-generation#chat), this is a
              repeated field that contains the conversation history and the latest request.

          model: Required. The name of the `Model` to use for generating the completion.

              Format: `models/{model}`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          cached_content: Optional. The name of the content
              [cached](https://ai.google.dev/gemini-api/docs/caching) to use as context to
              serve the prediction. Format: `cachedContents/{cachedContent}`

          generation_config: Configuration options for model generation and outputs. Not all parameters are
              configurable for every model.

          safety_settings: Optional. A list of unique `SafetySetting` instances for blocking unsafe
              content.

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

          system_instruction: The base structured datatype containing multi-part content of a message.

              A `Content` includes a `role` field designating the producer of the `Content`
              and a `parts` field containing multi-part data that contains the content of the
              message turn.

          tool_config: The Tool configuration containing parameters for specifying `Tool` use in the
              request.

          tools: Optional. A list of `Tools` the `Model` may use to generate the next response.

              A `Tool` is a piece of code that enables the system to interact with external
              systems to perform an action, or set of actions, outside of knowledge and scope
              of the `Model`. Supported `Tool`s are `Function` and `code_execution`. Refer to
              the [Function calling](https://ai.google.dev/gemini-api/docs/function-calling)
              and the [Code execution](https://ai.google.dev/gemini-api/docs/code-execution)
              guides to learn more.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return await self._post(
            f"/v1beta/tunedModels/{tuned_model}:streamGenerateContent",
            body=await async_maybe_transform(
                {
                    "contents": contents,
                    "model": model,
                    "cached_content": cached_content,
                    "generation_config": generation_config,
                    "safety_settings": safety_settings,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                },
                tuned_model_stream_generate_content_params.TunedModelStreamGenerateContentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_stream_generate_content_params.TunedModelStreamGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )

    async def transfer_ownership(
        self,
        tuned_model: str,
        *,
        email_address: str,
        api_empty: tuned_model_transfer_ownership_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Transfers ownership of the tuned model.

        This is the only way to change ownership
        of the tuned model. The current owner will be downgraded to writer role.

        Args:
          email_address: Required. The email address of the user to whom the tuned model is being
              transferred to.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return await self._post(
            f"/v1beta/tunedModels/{tuned_model}:transferOwnership",
            body=await async_maybe_transform(
                {"email_address": email_address},
                tuned_model_transfer_ownership_params.TunedModelTransferOwnershipParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    tuned_model_transfer_ownership_params.TunedModelTransferOwnershipParams,
                ),
            ),
            cast_to=object,
        )

    async def update_tuned_model(
        self,
        tuned_model: str,
        *,
        tuning_task: tuned_model_update_tuned_model_params.TuningTask,
        api_empty: tuned_model_update_tuned_model_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        update_mask: str | Omit = omit,
        base_model: str | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        reader_project_numbers: SequenceNotStr[str] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        tuned_model_source: tuned_model_update_tuned_model_params.TunedModelSource | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TunedModel:
        """
        Updates a tuned model.

        Args:
          tuning_task: Tuning tasks that create tuned models.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          update_mask: Optional. The list of fields to update.

          base_model:
              Immutable. The name of the `Model` to tune. Example:
              `models/gemini-1.5-flash-001`

          description: Optional. A short description of this model.

          display_name: Optional. The name to display for this model in user interfaces. The display
              name must be up to 40 characters including spaces.

          reader_project_numbers: Optional. List of project numbers that have read access to the tuned model.

          temperature: Optional. Controls the randomness of the output.

              Values can range over `[0.0,1.0]`, inclusive. A value closer to `1.0` will
              produce responses that are more varied, while a value closer to `0.0` will
              typically result in less surprising responses from the model.

              This value specifies default to be the one used by the base model while creating
              the model.

          top_k: Optional. For Top-k sampling.

              Top-k sampling considers the set of `top_k` most probable tokens. This value
              specifies default to be used by the backend while making the call to the model.

              This value specifies default to be the one used by the base model while creating
              the model.

          top_p: Optional. For Nucleus sampling.

              Nucleus sampling considers the smallest set of tokens whose probability sum is
              at least `top_p`.

              This value specifies default to be the one used by the base model while creating
              the model.

          tuned_model_source: Tuned model as a source for training a new model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return await self._patch(
            f"/v1beta/tunedModels/{tuned_model}",
            body=await async_maybe_transform(
                {
                    "tuning_task": tuning_task,
                    "base_model": base_model,
                    "description": description,
                    "display_name": display_name,
                    "reader_project_numbers": reader_project_numbers,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                    "tuned_model_source": tuned_model_source,
                },
                tuned_model_update_tuned_model_params.TunedModelUpdateTunedModelParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                        "update_mask": update_mask,
                    },
                    tuned_model_update_tuned_model_params.TunedModelUpdateTunedModelParams,
                ),
            ),
            cast_to=TunedModel,
        )


class TunedModelsResourceWithRawResponse:
    def __init__(self, tuned_models: TunedModelsResource) -> None:
        self._tuned_models = tuned_models

        self.async_batch_embed_content = to_raw_response_wrapper(
            tuned_models.async_batch_embed_content,
        )
        self.batch_generate_content = to_raw_response_wrapper(
            tuned_models.batch_generate_content,
        )
        self.create_tuned_model = to_raw_response_wrapper(
            tuned_models.create_tuned_model,
        )
        self.delete_tuned_model = to_raw_response_wrapper(
            tuned_models.delete_tuned_model,
        )
        self.generate_content = to_raw_response_wrapper(
            tuned_models.generate_content,
        )
        self.generate_text = to_raw_response_wrapper(
            tuned_models.generate_text,
        )
        self.list_tuned_models = to_raw_response_wrapper(
            tuned_models.list_tuned_models,
        )
        self.retrieve_tuned_model = to_raw_response_wrapper(
            tuned_models.retrieve_tuned_model,
        )
        self.stream_generate_content = to_raw_response_wrapper(
            tuned_models.stream_generate_content,
        )
        self.transfer_ownership = to_raw_response_wrapper(
            tuned_models.transfer_ownership,
        )
        self.update_tuned_model = to_raw_response_wrapper(
            tuned_models.update_tuned_model,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithRawResponse:
        return OperationsResourceWithRawResponse(self._tuned_models.operations)

    @cached_property
    def permissions(self) -> PermissionsResourceWithRawResponse:
        return PermissionsResourceWithRawResponse(self._tuned_models.permissions)


class AsyncTunedModelsResourceWithRawResponse:
    def __init__(self, tuned_models: AsyncTunedModelsResource) -> None:
        self._tuned_models = tuned_models

        self.async_batch_embed_content = async_to_raw_response_wrapper(
            tuned_models.async_batch_embed_content,
        )
        self.batch_generate_content = async_to_raw_response_wrapper(
            tuned_models.batch_generate_content,
        )
        self.create_tuned_model = async_to_raw_response_wrapper(
            tuned_models.create_tuned_model,
        )
        self.delete_tuned_model = async_to_raw_response_wrapper(
            tuned_models.delete_tuned_model,
        )
        self.generate_content = async_to_raw_response_wrapper(
            tuned_models.generate_content,
        )
        self.generate_text = async_to_raw_response_wrapper(
            tuned_models.generate_text,
        )
        self.list_tuned_models = async_to_raw_response_wrapper(
            tuned_models.list_tuned_models,
        )
        self.retrieve_tuned_model = async_to_raw_response_wrapper(
            tuned_models.retrieve_tuned_model,
        )
        self.stream_generate_content = async_to_raw_response_wrapper(
            tuned_models.stream_generate_content,
        )
        self.transfer_ownership = async_to_raw_response_wrapper(
            tuned_models.transfer_ownership,
        )
        self.update_tuned_model = async_to_raw_response_wrapper(
            tuned_models.update_tuned_model,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithRawResponse:
        return AsyncOperationsResourceWithRawResponse(self._tuned_models.operations)

    @cached_property
    def permissions(self) -> AsyncPermissionsResourceWithRawResponse:
        return AsyncPermissionsResourceWithRawResponse(self._tuned_models.permissions)


class TunedModelsResourceWithStreamingResponse:
    def __init__(self, tuned_models: TunedModelsResource) -> None:
        self._tuned_models = tuned_models

        self.async_batch_embed_content = to_streamed_response_wrapper(
            tuned_models.async_batch_embed_content,
        )
        self.batch_generate_content = to_streamed_response_wrapper(
            tuned_models.batch_generate_content,
        )
        self.create_tuned_model = to_streamed_response_wrapper(
            tuned_models.create_tuned_model,
        )
        self.delete_tuned_model = to_streamed_response_wrapper(
            tuned_models.delete_tuned_model,
        )
        self.generate_content = to_streamed_response_wrapper(
            tuned_models.generate_content,
        )
        self.generate_text = to_streamed_response_wrapper(
            tuned_models.generate_text,
        )
        self.list_tuned_models = to_streamed_response_wrapper(
            tuned_models.list_tuned_models,
        )
        self.retrieve_tuned_model = to_streamed_response_wrapper(
            tuned_models.retrieve_tuned_model,
        )
        self.stream_generate_content = to_streamed_response_wrapper(
            tuned_models.stream_generate_content,
        )
        self.transfer_ownership = to_streamed_response_wrapper(
            tuned_models.transfer_ownership,
        )
        self.update_tuned_model = to_streamed_response_wrapper(
            tuned_models.update_tuned_model,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithStreamingResponse:
        return OperationsResourceWithStreamingResponse(self._tuned_models.operations)

    @cached_property
    def permissions(self) -> PermissionsResourceWithStreamingResponse:
        return PermissionsResourceWithStreamingResponse(self._tuned_models.permissions)


class AsyncTunedModelsResourceWithStreamingResponse:
    def __init__(self, tuned_models: AsyncTunedModelsResource) -> None:
        self._tuned_models = tuned_models

        self.async_batch_embed_content = async_to_streamed_response_wrapper(
            tuned_models.async_batch_embed_content,
        )
        self.batch_generate_content = async_to_streamed_response_wrapper(
            tuned_models.batch_generate_content,
        )
        self.create_tuned_model = async_to_streamed_response_wrapper(
            tuned_models.create_tuned_model,
        )
        self.delete_tuned_model = async_to_streamed_response_wrapper(
            tuned_models.delete_tuned_model,
        )
        self.generate_content = async_to_streamed_response_wrapper(
            tuned_models.generate_content,
        )
        self.generate_text = async_to_streamed_response_wrapper(
            tuned_models.generate_text,
        )
        self.list_tuned_models = async_to_streamed_response_wrapper(
            tuned_models.list_tuned_models,
        )
        self.retrieve_tuned_model = async_to_streamed_response_wrapper(
            tuned_models.retrieve_tuned_model,
        )
        self.stream_generate_content = async_to_streamed_response_wrapper(
            tuned_models.stream_generate_content,
        )
        self.transfer_ownership = async_to_streamed_response_wrapper(
            tuned_models.transfer_ownership,
        )
        self.update_tuned_model = async_to_streamed_response_wrapper(
            tuned_models.update_tuned_model,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithStreamingResponse:
        return AsyncOperationsResourceWithStreamingResponse(self._tuned_models.operations)

    @cached_property
    def permissions(self) -> AsyncPermissionsResourceWithStreamingResponse:
        return AsyncPermissionsResourceWithStreamingResponse(self._tuned_models.permissions)
