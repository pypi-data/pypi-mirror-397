# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.beta import (
    dynamic_dynamic_id_generate_content_params,
    dynamic_dynamic_id_stream_generate_content_params,
)
from ..._base_client import make_request_options
from ...types.beta.tool_param import ToolParam
from ...types.beta.content_param import ContentParam
from ...types.beta.tool_config_param import ToolConfigParam
from ...types.beta.safety_setting_param import SafetySettingParam
from ...types.beta.generate_content_response import GenerateContentResponse

__all__ = ["DynamicResource", "AsyncDynamicResource"]


class DynamicResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DynamicResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return DynamicResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DynamicResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return DynamicResourceWithStreamingResponse(self)

    def dynamic_id_generate_content(
        self,
        dynamic_id: str,
        *,
        contents: Iterable[ContentParam],
        model: str,
        api_empty: dynamic_dynamic_id_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: dynamic_dynamic_id_generate_content_params.GenerationConfig | Omit = omit,
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
        if not dynamic_id:
            raise ValueError(f"Expected a non-empty value for `dynamic_id` but received {dynamic_id!r}")
        return self._post(
            f"/v1beta/dynamic/{dynamic_id}:generateContent",
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
                dynamic_dynamic_id_generate_content_params.DynamicDynamicIDGenerateContentParams,
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
                    dynamic_dynamic_id_generate_content_params.DynamicDynamicIDGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )

    def dynamic_id_stream_generate_content(
        self,
        dynamic_id: str,
        *,
        contents: Iterable[ContentParam],
        model: str,
        api_empty: dynamic_dynamic_id_stream_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: dynamic_dynamic_id_stream_generate_content_params.GenerationConfig | Omit = omit,
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
        if not dynamic_id:
            raise ValueError(f"Expected a non-empty value for `dynamic_id` but received {dynamic_id!r}")
        return self._post(
            f"/v1beta/dynamic/{dynamic_id}:streamGenerateContent",
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
                dynamic_dynamic_id_stream_generate_content_params.DynamicDynamicIDStreamGenerateContentParams,
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
                    dynamic_dynamic_id_stream_generate_content_params.DynamicDynamicIDStreamGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )


class AsyncDynamicResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDynamicResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDynamicResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDynamicResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncDynamicResourceWithStreamingResponse(self)

    async def dynamic_id_generate_content(
        self,
        dynamic_id: str,
        *,
        contents: Iterable[ContentParam],
        model: str,
        api_empty: dynamic_dynamic_id_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: dynamic_dynamic_id_generate_content_params.GenerationConfig | Omit = omit,
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
        if not dynamic_id:
            raise ValueError(f"Expected a non-empty value for `dynamic_id` but received {dynamic_id!r}")
        return await self._post(
            f"/v1beta/dynamic/{dynamic_id}:generateContent",
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
                dynamic_dynamic_id_generate_content_params.DynamicDynamicIDGenerateContentParams,
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
                    dynamic_dynamic_id_generate_content_params.DynamicDynamicIDGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )

    async def dynamic_id_stream_generate_content(
        self,
        dynamic_id: str,
        *,
        contents: Iterable[ContentParam],
        model: str,
        api_empty: dynamic_dynamic_id_stream_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: dynamic_dynamic_id_stream_generate_content_params.GenerationConfig | Omit = omit,
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
        if not dynamic_id:
            raise ValueError(f"Expected a non-empty value for `dynamic_id` but received {dynamic_id!r}")
        return await self._post(
            f"/v1beta/dynamic/{dynamic_id}:streamGenerateContent",
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
                dynamic_dynamic_id_stream_generate_content_params.DynamicDynamicIDStreamGenerateContentParams,
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
                    dynamic_dynamic_id_stream_generate_content_params.DynamicDynamicIDStreamGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )


class DynamicResourceWithRawResponse:
    def __init__(self, dynamic: DynamicResource) -> None:
        self._dynamic = dynamic

        self.dynamic_id_generate_content = to_raw_response_wrapper(
            dynamic.dynamic_id_generate_content,
        )
        self.dynamic_id_stream_generate_content = to_raw_response_wrapper(
            dynamic.dynamic_id_stream_generate_content,
        )


class AsyncDynamicResourceWithRawResponse:
    def __init__(self, dynamic: AsyncDynamicResource) -> None:
        self._dynamic = dynamic

        self.dynamic_id_generate_content = async_to_raw_response_wrapper(
            dynamic.dynamic_id_generate_content,
        )
        self.dynamic_id_stream_generate_content = async_to_raw_response_wrapper(
            dynamic.dynamic_id_stream_generate_content,
        )


class DynamicResourceWithStreamingResponse:
    def __init__(self, dynamic: DynamicResource) -> None:
        self._dynamic = dynamic

        self.dynamic_id_generate_content = to_streamed_response_wrapper(
            dynamic.dynamic_id_generate_content,
        )
        self.dynamic_id_stream_generate_content = to_streamed_response_wrapper(
            dynamic.dynamic_id_stream_generate_content,
        )


class AsyncDynamicResourceWithStreamingResponse:
    def __init__(self, dynamic: AsyncDynamicResource) -> None:
        self._dynamic = dynamic

        self.dynamic_id_generate_content = async_to_streamed_response_wrapper(
            dynamic.dynamic_id_generate_content,
        )
        self.dynamic_id_stream_generate_content = async_to_streamed_response_wrapper(
            dynamic.dynamic_id_stream_generate_content,
        )
