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
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....types.beta import (
    model_list_params,
    model_predict_params,
    model_retrieve_params,
    model_embed_text_params,
    model_count_tokens_params,
    model_embed_content_params,
    model_generate_text_params,
    model_generate_answer_params,
    model_batch_embed_text_params,
    model_generate_content_params,
    model_generate_message_params,
    model_count_text_tokens_params,
    model_batch_embed_contents_params,
    model_count_message_tokens_params,
    model_predict_long_running_params,
    model_batch_generate_content_params,
    model_stream_generate_content_params,
    model_async_batch_embed_content_params,
)
from ...._base_client import make_request_options
from ....types.beta.model import Model
from ....types.beta.tool_param import ToolParam
from ....types.beta.content_param import ContentParam
from ....types.beta.generate_text import GenerateText
from ....types.beta.text_prompt_param import TextPromptParam
from ....types.beta.tool_config_param import ToolConfigParam
from ....types.beta.model_list_response import ModelListResponse
from ....types.beta.message_prompt_param import MessagePromptParam
from ....types.beta.safety_setting_param import SafetySettingParam
from ....types.beta.embed_content_response import EmbedContentResponse
from ....types.beta.model_predict_response import ModelPredictResponse
from ....types.beta.embed_text_request_param import EmbedTextRequestParam
from ....types.beta.embed_content_batch_param import EmbedContentBatchParam
from ....types.beta.generate_content_response import GenerateContentResponse
from ....types.beta.model_embed_text_response import ModelEmbedTextResponse
from ....types.beta.embed_content_request_param import EmbedContentRequestParam
from ....types.beta.model_count_tokens_response import ModelCountTokensResponse
from ....types.beta.generate_content_batch_param import GenerateContentBatchParam
from ....types.beta.generate_content_request_param import GenerateContentRequestParam
from ....types.beta.model_generate_answer_response import ModelGenerateAnswerResponse
from ....types.beta.model_batch_embed_text_response import ModelBatchEmbedTextResponse
from ....types.beta.model_generate_message_response import ModelGenerateMessageResponse
from ....types.beta.batch_generate_content_operation import BatchGenerateContentOperation
from ....types.beta.model_count_text_tokens_response import ModelCountTextTokensResponse
from ....types.beta.async_batch_embed_content_operation import AsyncBatchEmbedContentOperation
from ....types.beta.model_batch_embed_contents_response import ModelBatchEmbedContentsResponse
from ....types.beta.model_count_message_tokens_response import ModelCountMessageTokensResponse
from ....types.beta.model_predict_long_running_response import ModelPredictLongRunningResponse

__all__ = ["ModelsResource", "AsyncModelsResource"]


class ModelsResource(SyncAPIResource):
    @cached_property
    def operations(self) -> OperationsResource:
        return OperationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return ModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return ModelsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        model: str,
        *,
        api_empty: model_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """
        Gets information about a specific `Model` such as its version number, token
        limits,
        [parameters](https://ai.google.dev/gemini-api/docs/models/generative-models#model-parameters)
        and other metadata. Refer to the
        [Gemini models guide](https://ai.google.dev/gemini-api/docs/models/gemini) for
        detailed model information.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._get(
            f"/v1beta/models/{model}",
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
                    model_retrieve_params.ModelRetrieveParams,
                ),
            ),
            cast_to=Model,
        )

    def list(
        self,
        *,
        api_empty: model_list_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListResponse:
        """
        Lists the [`Model`s](https://ai.google.dev/gemini-api/docs/models/gemini)
        available through the Gemini API.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: The maximum number of `Models` to return (per page).

              If unspecified, 50 models will be returned per page. This method returns at most
              1000 models per page, even if you pass a larger page_size.

          page_token: A page token, received from a previous `ListModels` call.

              Provide the `page_token` returned by one request as an argument to the next
              request to retrieve the next page.

              When paginating, all other parameters provided to `ListModels` must match the
              call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1beta/models",
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
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                    model_list_params.ModelListParams,
                ),
            ),
            cast_to=ModelListResponse,
        )

    def async_batch_embed_content(
        self,
        model: str,
        *,
        batch: EmbedContentBatchParam,
        api_empty: model_async_batch_embed_content_params.api_empty | Omit = omit,
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
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:asyncBatchEmbedContent",
            body=maybe_transform(
                {"batch": batch}, model_async_batch_embed_content_params.ModelAsyncBatchEmbedContentParams
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
                    model_async_batch_embed_content_params.ModelAsyncBatchEmbedContentParams,
                ),
            ),
            cast_to=AsyncBatchEmbedContentOperation,
        )

    def batch_embed_contents(
        self,
        model: str,
        *,
        requests: Iterable[EmbedContentRequestParam],
        api_empty: model_batch_embed_contents_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelBatchEmbedContentsResponse:
        """
        Generates multiple embedding vectors from the input `Content` which consists of
        a batch of strings represented as `EmbedContentRequest` objects.

        Args:
          requests: Required. Embed requests for the batch. The model in each of these requests must
              match the model specified `BatchEmbedContentsRequest.model`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:batchEmbedContents",
            body=maybe_transform(
                {"requests": requests}, model_batch_embed_contents_params.ModelBatchEmbedContentsParams
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
                    model_batch_embed_contents_params.ModelBatchEmbedContentsParams,
                ),
            ),
            cast_to=ModelBatchEmbedContentsResponse,
        )

    def batch_embed_text(
        self,
        model: str,
        *,
        api_empty: model_batch_embed_text_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        requests: Iterable[EmbedTextRequestParam] | Omit = omit,
        texts: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelBatchEmbedTextResponse:
        """
        Generates multiple embeddings from the model given input text in a synchronous
        call.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          requests: Optional. Embed requests for the batch. Only one of `texts` or `requests` can be
              set.

          texts: Optional. The free-form input texts that the model will turn into an embedding.
              The current limit is 100 texts, over which an error will be thrown.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:batchEmbedText",
            body=maybe_transform(
                {
                    "requests": requests,
                    "texts": texts,
                },
                model_batch_embed_text_params.ModelBatchEmbedTextParams,
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
                    model_batch_embed_text_params.ModelBatchEmbedTextParams,
                ),
            ),
            cast_to=ModelBatchEmbedTextResponse,
        )

    def batch_generate_content(
        self,
        model: str,
        *,
        batch: GenerateContentBatchParam,
        api_empty: model_batch_generate_content_params.api_empty | Omit = omit,
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
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:batchGenerateContent",
            body=maybe_transform({"batch": batch}, model_batch_generate_content_params.ModelBatchGenerateContentParams),
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
                    model_batch_generate_content_params.ModelBatchGenerateContentParams,
                ),
            ),
            cast_to=BatchGenerateContentOperation,
        )

    def count_message_tokens(
        self,
        model: str,
        *,
        prompt: MessagePromptParam,
        api_empty: model_count_message_tokens_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelCountMessageTokensResponse:
        """
        Runs a model's tokenizer on a string and returns the token count.

        Args:
          prompt: All of the structured input text passed to the model as a prompt.

              A `MessagePrompt` contains a structured set of fields that provide context for
              the conversation, examples of user input/model output message pairs that prime
              the model to respond in different ways, and the conversation history or list of
              messages representing the alternating turns of the conversation between the user
              and the model.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:countMessageTokens",
            body=maybe_transform({"prompt": prompt}, model_count_message_tokens_params.ModelCountMessageTokensParams),
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
                    model_count_message_tokens_params.ModelCountMessageTokensParams,
                ),
            ),
            cast_to=ModelCountMessageTokensResponse,
        )

    def count_text_tokens(
        self,
        model: str,
        *,
        prompt: TextPromptParam,
        api_empty: model_count_text_tokens_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelCountTextTokensResponse:
        """
        Runs a model's tokenizer on a text and returns the token count.

        Args:
          prompt: Text given to the model as a prompt.

              The Model will use this TextPrompt to Generate a text completion.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:countTextTokens",
            body=maybe_transform({"prompt": prompt}, model_count_text_tokens_params.ModelCountTextTokensParams),
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
                    model_count_text_tokens_params.ModelCountTextTokensParams,
                ),
            ),
            cast_to=ModelCountTextTokensResponse,
        )

    def count_tokens(
        self,
        model: str,
        *,
        api_empty: model_count_tokens_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        contents: Iterable[ContentParam] | Omit = omit,
        generate_content_request: GenerateContentRequestParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelCountTokensResponse:
        """Runs a model's tokenizer on input `Content` and returns the token count.

        Refer
        to the [tokens guide](https://ai.google.dev/gemini-api/docs/tokens) to learn
        more about tokens.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          contents: Optional. The input given to the model as a prompt. This field is ignored when
              `generate_content_request` is set.

          generate_content_request: Request to generate a completion from the model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:countTokens",
            body=maybe_transform(
                {
                    "contents": contents,
                    "generate_content_request": generate_content_request,
                },
                model_count_tokens_params.ModelCountTokensParams,
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
                    model_count_tokens_params.ModelCountTokensParams,
                ),
            ),
            cast_to=ModelCountTokensResponse,
        )

    def embed_content(
        self,
        path_model: str,
        *,
        content: ContentParam,
        body_model: str,
        api_empty: model_embed_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        output_dimensionality: int | Omit = omit,
        task_type: Literal[
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
        | Omit = omit,
        title: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EmbedContentResponse:
        """
        Generates a text embedding vector from the input `Content` using the specified
        [Gemini Embedding model](https://ai.google.dev/gemini-api/docs/models/gemini#text-embedding).

        Args:
          content: The base structured datatype containing multi-part content of a message.

              A `Content` includes a `role` field designating the producer of the `Content`
              and a `parts` field containing multi-part data that contains the content of the
              message turn.

          body_model: Required. The model's resource name. This serves as an ID for the Model to use.

              This name should match a model name returned by the `ListModels` method.

              Format: `models/{model}`

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          output_dimensionality: Optional. Optional reduced dimension for the output embedding. If set, excessive
              values in the output embedding are truncated from the end. Supported by newer
              models since 2024 only. You cannot set this value if using the earlier model
              (`models/embedding-001`).

          task_type: Optional. Optional task type for which the embeddings will be used. Not
              supported on earlier models (`models/embedding-001`).

          title: Optional. An optional title for the text. Only applicable when TaskType is
              `RETRIEVAL_DOCUMENT`.

              Note: Specifying a `title` for `RETRIEVAL_DOCUMENT` provides better quality
              embeddings for retrieval.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_model:
            raise ValueError(f"Expected a non-empty value for `path_model` but received {path_model!r}")
        return self._post(
            f"/v1beta/models/{path_model}:embedContent",
            body=maybe_transform(
                {
                    "content": content,
                    "body_model": body_model,
                    "output_dimensionality": output_dimensionality,
                    "task_type": task_type,
                    "title": title,
                },
                model_embed_content_params.ModelEmbedContentParams,
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
                    model_embed_content_params.ModelEmbedContentParams,
                ),
            ),
            cast_to=EmbedContentResponse,
        )

    def embed_text(
        self,
        path_model: str,
        *,
        body_model: str,
        api_empty: model_embed_text_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        text: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelEmbedTextResponse:
        """
        Generates an embedding from the model given an input message.

        Args:
          body_model: Required. The model name to use with the format model=models/{model}.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          text: Optional. The free-form input text that the model will turn into an embedding.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_model:
            raise ValueError(f"Expected a non-empty value for `path_model` but received {path_model!r}")
        return self._post(
            f"/v1beta/models/{path_model}:embedText",
            body=maybe_transform(
                {
                    "body_model": body_model,
                    "text": text,
                },
                model_embed_text_params.ModelEmbedTextParams,
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
                    model_embed_text_params.ModelEmbedTextParams,
                ),
            ),
            cast_to=ModelEmbedTextResponse,
        )

    def generate_answer(
        self,
        model: str,
        *,
        answer_style: Literal["ANSWER_STYLE_UNSPECIFIED", "ABSTRACTIVE", "EXTRACTIVE", "VERBOSE"],
        contents: Iterable[ContentParam],
        api_empty: model_generate_answer_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        inline_passages: model_generate_answer_params.InlinePassages | Omit = omit,
        safety_settings: Iterable[SafetySettingParam] | Omit = omit,
        semantic_retriever: model_generate_answer_params.SemanticRetriever | Omit = omit,
        temperature: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelGenerateAnswerResponse:
        """
        Generates a grounded answer from the model given an input
        `GenerateAnswerRequest`.

        Args:
          answer_style: Required. Style in which answers should be returned.

          contents: Required. The content of the current conversation with the `Model`. For
              single-turn queries, this is a single question to answer. For multi-turn
              queries, this is a repeated field that contains conversation history and the
              last `Content` in the list containing the question.

              Note: `GenerateAnswer` only supports queries in English.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          inline_passages: A repeated list of passages.

          safety_settings: Optional. A list of unique `SafetySetting` instances for blocking unsafe
              content.

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

          semantic_retriever: Configuration for retrieving grounding content from a `Corpus` or `Document`
              created using the Semantic Retriever API.

          temperature: Optional. Controls the randomness of the output.

              Values can range from [0.0,1.0], inclusive. A value closer to 1.0 will produce
              responses that are more varied and creative, while a value closer to 0.0 will
              typically result in more straightforward responses from the model. A low
              temperature (~0.2) is usually recommended for Attributed-Question-Answering use
              cases.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:generateAnswer",
            body=maybe_transform(
                {
                    "answer_style": answer_style,
                    "contents": contents,
                    "inline_passages": inline_passages,
                    "safety_settings": safety_settings,
                    "semantic_retriever": semantic_retriever,
                    "temperature": temperature,
                },
                model_generate_answer_params.ModelGenerateAnswerParams,
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
                    model_generate_answer_params.ModelGenerateAnswerParams,
                ),
            ),
            cast_to=ModelGenerateAnswerResponse,
        )

    def generate_content(
        self,
        path_model: str,
        *,
        contents: Iterable[ContentParam],
        body_model: str,
        api_empty: model_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: model_generate_content_params.GenerationConfig | Omit = omit,
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

          body_model: Required. The name of the `Model` to use for generating the completion.

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
        if not path_model:
            raise ValueError(f"Expected a non-empty value for `path_model` but received {path_model!r}")
        return self._post(
            f"/v1beta/models/{path_model}:generateContent",
            body=maybe_transform(
                {
                    "contents": contents,
                    "body_model": body_model,
                    "cached_content": cached_content,
                    "generation_config": generation_config,
                    "safety_settings": safety_settings,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                },
                model_generate_content_params.ModelGenerateContentParams,
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
                    model_generate_content_params.ModelGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )

    def generate_message(
        self,
        model: str,
        *,
        prompt: MessagePromptParam,
        api_empty: model_generate_message_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        candidate_count: int | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelGenerateMessageResponse:
        """
        Generates a response from the model given an input `MessagePrompt`.

        Args:
          prompt: All of the structured input text passed to the model as a prompt.

              A `MessagePrompt` contains a structured set of fields that provide context for
              the conversation, examples of user input/model output message pairs that prime
              the model to respond in different ways, and the conversation history or list of
              messages representing the alternating turns of the conversation between the user
              and the model.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          candidate_count: Optional. The number of generated response messages to return.

              This value must be between `[1, 8]`, inclusive. If unset, this will default to
              `1`.

          temperature: Optional. Controls the randomness of the output.

              Values can range over `[0.0,1.0]`, inclusive. A value closer to `1.0` will
              produce responses that are more varied, while a value closer to `0.0` will
              typically result in less surprising responses from the model.

          top_k: Optional. The maximum number of tokens to consider when sampling.

              The model uses combined Top-k and nucleus sampling.

              Top-k sampling considers the set of `top_k` most probable tokens.

          top_p: Optional. The maximum cumulative probability of tokens to consider when
              sampling.

              The model uses combined Top-k and nucleus sampling.

              Nucleus sampling considers the smallest set of tokens whose probability sum is
              at least `top_p`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:generateMessage",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "candidate_count": candidate_count,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                model_generate_message_params.ModelGenerateMessageParams,
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
                    model_generate_message_params.ModelGenerateMessageParams,
                ),
            ),
            cast_to=ModelGenerateMessageResponse,
        )

    def generate_text(
        self,
        model: str,
        *,
        prompt: TextPromptParam,
        api_empty: model_generate_text_params.api_empty | Omit = omit,
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
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:generateText",
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
                model_generate_text_params.ModelGenerateTextParams,
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
                    model_generate_text_params.ModelGenerateTextParams,
                ),
            ),
            cast_to=GenerateText,
        )

    def predict(
        self,
        model: str,
        *,
        instances: Iterable[object],
        api_empty: model_predict_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        parameters: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelPredictResponse:
        """Performs a prediction request.

        Args:
          instances: Required.

        The instances that are the input to the prediction call.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          parameters: Optional. The parameters that govern the prediction call.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:predict",
            body=maybe_transform(
                {
                    "instances": instances,
                    "parameters": parameters,
                },
                model_predict_params.ModelPredictParams,
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
                    model_predict_params.ModelPredictParams,
                ),
            ),
            cast_to=ModelPredictResponse,
        )

    def predict_long_running(
        self,
        model: str,
        *,
        instances: Iterable[object],
        api_empty: model_predict_long_running_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        parameters: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelPredictLongRunningResponse:
        """Same as Predict but returns an LRO.

        Args:
          instances: Required.

        The instances that are the input to the prediction call.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          parameters: Optional. The parameters that govern the prediction call.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._post(
            f"/v1beta/models/{model}:predictLongRunning",
            body=maybe_transform(
                {
                    "instances": instances,
                    "parameters": parameters,
                },
                model_predict_long_running_params.ModelPredictLongRunningParams,
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
                    model_predict_long_running_params.ModelPredictLongRunningParams,
                ),
            ),
            cast_to=ModelPredictLongRunningResponse,
        )

    def stream_generate_content(
        self,
        path_model: str,
        *,
        contents: Iterable[ContentParam],
        body_model: str,
        api_empty: model_stream_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: model_stream_generate_content_params.GenerationConfig | Omit = omit,
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

          body_model: Required. The name of the `Model` to use for generating the completion.

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
        if not path_model:
            raise ValueError(f"Expected a non-empty value for `path_model` but received {path_model!r}")
        return self._post(
            f"/v1beta/models/{path_model}:streamGenerateContent",
            body=maybe_transform(
                {
                    "contents": contents,
                    "body_model": body_model,
                    "cached_content": cached_content,
                    "generation_config": generation_config,
                    "safety_settings": safety_settings,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                },
                model_stream_generate_content_params.ModelStreamGenerateContentParams,
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
                    model_stream_generate_content_params.ModelStreamGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )


class AsyncModelsResource(AsyncAPIResource):
    @cached_property
    def operations(self) -> AsyncOperationsResource:
        return AsyncOperationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncModelsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        model: str,
        *,
        api_empty: model_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Model:
        """
        Gets information about a specific `Model` such as its version number, token
        limits,
        [parameters](https://ai.google.dev/gemini-api/docs/models/generative-models#model-parameters)
        and other metadata. Refer to the
        [Gemini models guide](https://ai.google.dev/gemini-api/docs/models/gemini) for
        detailed model information.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._get(
            f"/v1beta/models/{model}",
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
                    model_retrieve_params.ModelRetrieveParams,
                ),
            ),
            cast_to=Model,
        )

    async def list(
        self,
        *,
        api_empty: model_list_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelListResponse:
        """
        Lists the [`Model`s](https://ai.google.dev/gemini-api/docs/models/gemini)
        available through the Gemini API.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: The maximum number of `Models` to return (per page).

              If unspecified, 50 models will be returned per page. This method returns at most
              1000 models per page, even if you pass a larger page_size.

          page_token: A page token, received from a previous `ListModels` call.

              Provide the `page_token` returned by one request as an argument to the next
              request to retrieve the next page.

              When paginating, all other parameters provided to `ListModels` must match the
              call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1beta/models",
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
                        "page_size": page_size,
                        "page_token": page_token,
                    },
                    model_list_params.ModelListParams,
                ),
            ),
            cast_to=ModelListResponse,
        )

    async def async_batch_embed_content(
        self,
        model: str,
        *,
        batch: EmbedContentBatchParam,
        api_empty: model_async_batch_embed_content_params.api_empty | Omit = omit,
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
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:asyncBatchEmbedContent",
            body=await async_maybe_transform(
                {"batch": batch}, model_async_batch_embed_content_params.ModelAsyncBatchEmbedContentParams
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
                    model_async_batch_embed_content_params.ModelAsyncBatchEmbedContentParams,
                ),
            ),
            cast_to=AsyncBatchEmbedContentOperation,
        )

    async def batch_embed_contents(
        self,
        model: str,
        *,
        requests: Iterable[EmbedContentRequestParam],
        api_empty: model_batch_embed_contents_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelBatchEmbedContentsResponse:
        """
        Generates multiple embedding vectors from the input `Content` which consists of
        a batch of strings represented as `EmbedContentRequest` objects.

        Args:
          requests: Required. Embed requests for the batch. The model in each of these requests must
              match the model specified `BatchEmbedContentsRequest.model`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:batchEmbedContents",
            body=await async_maybe_transform(
                {"requests": requests}, model_batch_embed_contents_params.ModelBatchEmbedContentsParams
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
                    model_batch_embed_contents_params.ModelBatchEmbedContentsParams,
                ),
            ),
            cast_to=ModelBatchEmbedContentsResponse,
        )

    async def batch_embed_text(
        self,
        model: str,
        *,
        api_empty: model_batch_embed_text_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        requests: Iterable[EmbedTextRequestParam] | Omit = omit,
        texts: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelBatchEmbedTextResponse:
        """
        Generates multiple embeddings from the model given input text in a synchronous
        call.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          requests: Optional. Embed requests for the batch. Only one of `texts` or `requests` can be
              set.

          texts: Optional. The free-form input texts that the model will turn into an embedding.
              The current limit is 100 texts, over which an error will be thrown.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:batchEmbedText",
            body=await async_maybe_transform(
                {
                    "requests": requests,
                    "texts": texts,
                },
                model_batch_embed_text_params.ModelBatchEmbedTextParams,
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
                    model_batch_embed_text_params.ModelBatchEmbedTextParams,
                ),
            ),
            cast_to=ModelBatchEmbedTextResponse,
        )

    async def batch_generate_content(
        self,
        model: str,
        *,
        batch: GenerateContentBatchParam,
        api_empty: model_batch_generate_content_params.api_empty | Omit = omit,
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
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:batchGenerateContent",
            body=await async_maybe_transform(
                {"batch": batch}, model_batch_generate_content_params.ModelBatchGenerateContentParams
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
                    model_batch_generate_content_params.ModelBatchGenerateContentParams,
                ),
            ),
            cast_to=BatchGenerateContentOperation,
        )

    async def count_message_tokens(
        self,
        model: str,
        *,
        prompt: MessagePromptParam,
        api_empty: model_count_message_tokens_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelCountMessageTokensResponse:
        """
        Runs a model's tokenizer on a string and returns the token count.

        Args:
          prompt: All of the structured input text passed to the model as a prompt.

              A `MessagePrompt` contains a structured set of fields that provide context for
              the conversation, examples of user input/model output message pairs that prime
              the model to respond in different ways, and the conversation history or list of
              messages representing the alternating turns of the conversation between the user
              and the model.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:countMessageTokens",
            body=await async_maybe_transform(
                {"prompt": prompt}, model_count_message_tokens_params.ModelCountMessageTokensParams
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
                    model_count_message_tokens_params.ModelCountMessageTokensParams,
                ),
            ),
            cast_to=ModelCountMessageTokensResponse,
        )

    async def count_text_tokens(
        self,
        model: str,
        *,
        prompt: TextPromptParam,
        api_empty: model_count_text_tokens_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelCountTextTokensResponse:
        """
        Runs a model's tokenizer on a text and returns the token count.

        Args:
          prompt: Text given to the model as a prompt.

              The Model will use this TextPrompt to Generate a text completion.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:countTextTokens",
            body=await async_maybe_transform(
                {"prompt": prompt}, model_count_text_tokens_params.ModelCountTextTokensParams
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
                    model_count_text_tokens_params.ModelCountTextTokensParams,
                ),
            ),
            cast_to=ModelCountTextTokensResponse,
        )

    async def count_tokens(
        self,
        model: str,
        *,
        api_empty: model_count_tokens_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        contents: Iterable[ContentParam] | Omit = omit,
        generate_content_request: GenerateContentRequestParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelCountTokensResponse:
        """Runs a model's tokenizer on input `Content` and returns the token count.

        Refer
        to the [tokens guide](https://ai.google.dev/gemini-api/docs/tokens) to learn
        more about tokens.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          contents: Optional. The input given to the model as a prompt. This field is ignored when
              `generate_content_request` is set.

          generate_content_request: Request to generate a completion from the model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:countTokens",
            body=await async_maybe_transform(
                {
                    "contents": contents,
                    "generate_content_request": generate_content_request,
                },
                model_count_tokens_params.ModelCountTokensParams,
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
                    model_count_tokens_params.ModelCountTokensParams,
                ),
            ),
            cast_to=ModelCountTokensResponse,
        )

    async def embed_content(
        self,
        path_model: str,
        *,
        content: ContentParam,
        body_model: str,
        api_empty: model_embed_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        output_dimensionality: int | Omit = omit,
        task_type: Literal[
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
        | Omit = omit,
        title: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EmbedContentResponse:
        """
        Generates a text embedding vector from the input `Content` using the specified
        [Gemini Embedding model](https://ai.google.dev/gemini-api/docs/models/gemini#text-embedding).

        Args:
          content: The base structured datatype containing multi-part content of a message.

              A `Content` includes a `role` field designating the producer of the `Content`
              and a `parts` field containing multi-part data that contains the content of the
              message turn.

          body_model: Required. The model's resource name. This serves as an ID for the Model to use.

              This name should match a model name returned by the `ListModels` method.

              Format: `models/{model}`

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          output_dimensionality: Optional. Optional reduced dimension for the output embedding. If set, excessive
              values in the output embedding are truncated from the end. Supported by newer
              models since 2024 only. You cannot set this value if using the earlier model
              (`models/embedding-001`).

          task_type: Optional. Optional task type for which the embeddings will be used. Not
              supported on earlier models (`models/embedding-001`).

          title: Optional. An optional title for the text. Only applicable when TaskType is
              `RETRIEVAL_DOCUMENT`.

              Note: Specifying a `title` for `RETRIEVAL_DOCUMENT` provides better quality
              embeddings for retrieval.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_model:
            raise ValueError(f"Expected a non-empty value for `path_model` but received {path_model!r}")
        return await self._post(
            f"/v1beta/models/{path_model}:embedContent",
            body=await async_maybe_transform(
                {
                    "content": content,
                    "body_model": body_model,
                    "output_dimensionality": output_dimensionality,
                    "task_type": task_type,
                    "title": title,
                },
                model_embed_content_params.ModelEmbedContentParams,
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
                    model_embed_content_params.ModelEmbedContentParams,
                ),
            ),
            cast_to=EmbedContentResponse,
        )

    async def embed_text(
        self,
        path_model: str,
        *,
        body_model: str,
        api_empty: model_embed_text_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        text: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelEmbedTextResponse:
        """
        Generates an embedding from the model given an input message.

        Args:
          body_model: Required. The model name to use with the format model=models/{model}.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          text: Optional. The free-form input text that the model will turn into an embedding.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_model:
            raise ValueError(f"Expected a non-empty value for `path_model` but received {path_model!r}")
        return await self._post(
            f"/v1beta/models/{path_model}:embedText",
            body=await async_maybe_transform(
                {
                    "body_model": body_model,
                    "text": text,
                },
                model_embed_text_params.ModelEmbedTextParams,
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
                    model_embed_text_params.ModelEmbedTextParams,
                ),
            ),
            cast_to=ModelEmbedTextResponse,
        )

    async def generate_answer(
        self,
        model: str,
        *,
        answer_style: Literal["ANSWER_STYLE_UNSPECIFIED", "ABSTRACTIVE", "EXTRACTIVE", "VERBOSE"],
        contents: Iterable[ContentParam],
        api_empty: model_generate_answer_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        inline_passages: model_generate_answer_params.InlinePassages | Omit = omit,
        safety_settings: Iterable[SafetySettingParam] | Omit = omit,
        semantic_retriever: model_generate_answer_params.SemanticRetriever | Omit = omit,
        temperature: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelGenerateAnswerResponse:
        """
        Generates a grounded answer from the model given an input
        `GenerateAnswerRequest`.

        Args:
          answer_style: Required. Style in which answers should be returned.

          contents: Required. The content of the current conversation with the `Model`. For
              single-turn queries, this is a single question to answer. For multi-turn
              queries, this is a repeated field that contains conversation history and the
              last `Content` in the list containing the question.

              Note: `GenerateAnswer` only supports queries in English.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          inline_passages: A repeated list of passages.

          safety_settings: Optional. A list of unique `SafetySetting` instances for blocking unsafe
              content.

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

          semantic_retriever: Configuration for retrieving grounding content from a `Corpus` or `Document`
              created using the Semantic Retriever API.

          temperature: Optional. Controls the randomness of the output.

              Values can range from [0.0,1.0], inclusive. A value closer to 1.0 will produce
              responses that are more varied and creative, while a value closer to 0.0 will
              typically result in more straightforward responses from the model. A low
              temperature (~0.2) is usually recommended for Attributed-Question-Answering use
              cases.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:generateAnswer",
            body=await async_maybe_transform(
                {
                    "answer_style": answer_style,
                    "contents": contents,
                    "inline_passages": inline_passages,
                    "safety_settings": safety_settings,
                    "semantic_retriever": semantic_retriever,
                    "temperature": temperature,
                },
                model_generate_answer_params.ModelGenerateAnswerParams,
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
                    model_generate_answer_params.ModelGenerateAnswerParams,
                ),
            ),
            cast_to=ModelGenerateAnswerResponse,
        )

    async def generate_content(
        self,
        path_model: str,
        *,
        contents: Iterable[ContentParam],
        body_model: str,
        api_empty: model_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: model_generate_content_params.GenerationConfig | Omit = omit,
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

          body_model: Required. The name of the `Model` to use for generating the completion.

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
        if not path_model:
            raise ValueError(f"Expected a non-empty value for `path_model` but received {path_model!r}")
        return await self._post(
            f"/v1beta/models/{path_model}:generateContent",
            body=await async_maybe_transform(
                {
                    "contents": contents,
                    "body_model": body_model,
                    "cached_content": cached_content,
                    "generation_config": generation_config,
                    "safety_settings": safety_settings,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                },
                model_generate_content_params.ModelGenerateContentParams,
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
                    model_generate_content_params.ModelGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )

    async def generate_message(
        self,
        model: str,
        *,
        prompt: MessagePromptParam,
        api_empty: model_generate_message_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        candidate_count: int | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelGenerateMessageResponse:
        """
        Generates a response from the model given an input `MessagePrompt`.

        Args:
          prompt: All of the structured input text passed to the model as a prompt.

              A `MessagePrompt` contains a structured set of fields that provide context for
              the conversation, examples of user input/model output message pairs that prime
              the model to respond in different ways, and the conversation history or list of
              messages representing the alternating turns of the conversation between the user
              and the model.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          candidate_count: Optional. The number of generated response messages to return.

              This value must be between `[1, 8]`, inclusive. If unset, this will default to
              `1`.

          temperature: Optional. Controls the randomness of the output.

              Values can range over `[0.0,1.0]`, inclusive. A value closer to `1.0` will
              produce responses that are more varied, while a value closer to `0.0` will
              typically result in less surprising responses from the model.

          top_k: Optional. The maximum number of tokens to consider when sampling.

              The model uses combined Top-k and nucleus sampling.

              Top-k sampling considers the set of `top_k` most probable tokens.

          top_p: Optional. The maximum cumulative probability of tokens to consider when
              sampling.

              The model uses combined Top-k and nucleus sampling.

              Nucleus sampling considers the smallest set of tokens whose probability sum is
              at least `top_p`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:generateMessage",
            body=await async_maybe_transform(
                {
                    "prompt": prompt,
                    "candidate_count": candidate_count,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                model_generate_message_params.ModelGenerateMessageParams,
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
                    model_generate_message_params.ModelGenerateMessageParams,
                ),
            ),
            cast_to=ModelGenerateMessageResponse,
        )

    async def generate_text(
        self,
        model: str,
        *,
        prompt: TextPromptParam,
        api_empty: model_generate_text_params.api_empty | Omit = omit,
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
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:generateText",
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
                model_generate_text_params.ModelGenerateTextParams,
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
                    model_generate_text_params.ModelGenerateTextParams,
                ),
            ),
            cast_to=GenerateText,
        )

    async def predict(
        self,
        model: str,
        *,
        instances: Iterable[object],
        api_empty: model_predict_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        parameters: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelPredictResponse:
        """Performs a prediction request.

        Args:
          instances: Required.

        The instances that are the input to the prediction call.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          parameters: Optional. The parameters that govern the prediction call.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:predict",
            body=await async_maybe_transform(
                {
                    "instances": instances,
                    "parameters": parameters,
                },
                model_predict_params.ModelPredictParams,
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
                    model_predict_params.ModelPredictParams,
                ),
            ),
            cast_to=ModelPredictResponse,
        )

    async def predict_long_running(
        self,
        model: str,
        *,
        instances: Iterable[object],
        api_empty: model_predict_long_running_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        parameters: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ModelPredictLongRunningResponse:
        """Same as Predict but returns an LRO.

        Args:
          instances: Required.

        The instances that are the input to the prediction call.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          parameters: Optional. The parameters that govern the prediction call.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._post(
            f"/v1beta/models/{model}:predictLongRunning",
            body=await async_maybe_transform(
                {
                    "instances": instances,
                    "parameters": parameters,
                },
                model_predict_long_running_params.ModelPredictLongRunningParams,
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
                    model_predict_long_running_params.ModelPredictLongRunningParams,
                ),
            ),
            cast_to=ModelPredictLongRunningResponse,
        )

    async def stream_generate_content(
        self,
        path_model: str,
        *,
        contents: Iterable[ContentParam],
        body_model: str,
        api_empty: model_stream_generate_content_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        cached_content: str | Omit = omit,
        generation_config: model_stream_generate_content_params.GenerationConfig | Omit = omit,
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

          body_model: Required. The name of the `Model` to use for generating the completion.

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
        if not path_model:
            raise ValueError(f"Expected a non-empty value for `path_model` but received {path_model!r}")
        return await self._post(
            f"/v1beta/models/{path_model}:streamGenerateContent",
            body=await async_maybe_transform(
                {
                    "contents": contents,
                    "body_model": body_model,
                    "cached_content": cached_content,
                    "generation_config": generation_config,
                    "safety_settings": safety_settings,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                },
                model_stream_generate_content_params.ModelStreamGenerateContentParams,
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
                    model_stream_generate_content_params.ModelStreamGenerateContentParams,
                ),
            ),
            cast_to=GenerateContentResponse,
        )


class ModelsResourceWithRawResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.retrieve = to_raw_response_wrapper(
            models.retrieve,
        )
        self.list = to_raw_response_wrapper(
            models.list,
        )
        self.async_batch_embed_content = to_raw_response_wrapper(
            models.async_batch_embed_content,
        )
        self.batch_embed_contents = to_raw_response_wrapper(
            models.batch_embed_contents,
        )
        self.batch_embed_text = to_raw_response_wrapper(
            models.batch_embed_text,
        )
        self.batch_generate_content = to_raw_response_wrapper(
            models.batch_generate_content,
        )
        self.count_message_tokens = to_raw_response_wrapper(
            models.count_message_tokens,
        )
        self.count_text_tokens = to_raw_response_wrapper(
            models.count_text_tokens,
        )
        self.count_tokens = to_raw_response_wrapper(
            models.count_tokens,
        )
        self.embed_content = to_raw_response_wrapper(
            models.embed_content,
        )
        self.embed_text = to_raw_response_wrapper(
            models.embed_text,
        )
        self.generate_answer = to_raw_response_wrapper(
            models.generate_answer,
        )
        self.generate_content = to_raw_response_wrapper(
            models.generate_content,
        )
        self.generate_message = to_raw_response_wrapper(
            models.generate_message,
        )
        self.generate_text = to_raw_response_wrapper(
            models.generate_text,
        )
        self.predict = to_raw_response_wrapper(
            models.predict,
        )
        self.predict_long_running = to_raw_response_wrapper(
            models.predict_long_running,
        )
        self.stream_generate_content = to_raw_response_wrapper(
            models.stream_generate_content,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithRawResponse:
        return OperationsResourceWithRawResponse(self._models.operations)


class AsyncModelsResourceWithRawResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.retrieve = async_to_raw_response_wrapper(
            models.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            models.list,
        )
        self.async_batch_embed_content = async_to_raw_response_wrapper(
            models.async_batch_embed_content,
        )
        self.batch_embed_contents = async_to_raw_response_wrapper(
            models.batch_embed_contents,
        )
        self.batch_embed_text = async_to_raw_response_wrapper(
            models.batch_embed_text,
        )
        self.batch_generate_content = async_to_raw_response_wrapper(
            models.batch_generate_content,
        )
        self.count_message_tokens = async_to_raw_response_wrapper(
            models.count_message_tokens,
        )
        self.count_text_tokens = async_to_raw_response_wrapper(
            models.count_text_tokens,
        )
        self.count_tokens = async_to_raw_response_wrapper(
            models.count_tokens,
        )
        self.embed_content = async_to_raw_response_wrapper(
            models.embed_content,
        )
        self.embed_text = async_to_raw_response_wrapper(
            models.embed_text,
        )
        self.generate_answer = async_to_raw_response_wrapper(
            models.generate_answer,
        )
        self.generate_content = async_to_raw_response_wrapper(
            models.generate_content,
        )
        self.generate_message = async_to_raw_response_wrapper(
            models.generate_message,
        )
        self.generate_text = async_to_raw_response_wrapper(
            models.generate_text,
        )
        self.predict = async_to_raw_response_wrapper(
            models.predict,
        )
        self.predict_long_running = async_to_raw_response_wrapper(
            models.predict_long_running,
        )
        self.stream_generate_content = async_to_raw_response_wrapper(
            models.stream_generate_content,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithRawResponse:
        return AsyncOperationsResourceWithRawResponse(self._models.operations)


class ModelsResourceWithStreamingResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.retrieve = to_streamed_response_wrapper(
            models.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            models.list,
        )
        self.async_batch_embed_content = to_streamed_response_wrapper(
            models.async_batch_embed_content,
        )
        self.batch_embed_contents = to_streamed_response_wrapper(
            models.batch_embed_contents,
        )
        self.batch_embed_text = to_streamed_response_wrapper(
            models.batch_embed_text,
        )
        self.batch_generate_content = to_streamed_response_wrapper(
            models.batch_generate_content,
        )
        self.count_message_tokens = to_streamed_response_wrapper(
            models.count_message_tokens,
        )
        self.count_text_tokens = to_streamed_response_wrapper(
            models.count_text_tokens,
        )
        self.count_tokens = to_streamed_response_wrapper(
            models.count_tokens,
        )
        self.embed_content = to_streamed_response_wrapper(
            models.embed_content,
        )
        self.embed_text = to_streamed_response_wrapper(
            models.embed_text,
        )
        self.generate_answer = to_streamed_response_wrapper(
            models.generate_answer,
        )
        self.generate_content = to_streamed_response_wrapper(
            models.generate_content,
        )
        self.generate_message = to_streamed_response_wrapper(
            models.generate_message,
        )
        self.generate_text = to_streamed_response_wrapper(
            models.generate_text,
        )
        self.predict = to_streamed_response_wrapper(
            models.predict,
        )
        self.predict_long_running = to_streamed_response_wrapper(
            models.predict_long_running,
        )
        self.stream_generate_content = to_streamed_response_wrapper(
            models.stream_generate_content,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithStreamingResponse:
        return OperationsResourceWithStreamingResponse(self._models.operations)


class AsyncModelsResourceWithStreamingResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.retrieve = async_to_streamed_response_wrapper(
            models.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            models.list,
        )
        self.async_batch_embed_content = async_to_streamed_response_wrapper(
            models.async_batch_embed_content,
        )
        self.batch_embed_contents = async_to_streamed_response_wrapper(
            models.batch_embed_contents,
        )
        self.batch_embed_text = async_to_streamed_response_wrapper(
            models.batch_embed_text,
        )
        self.batch_generate_content = async_to_streamed_response_wrapper(
            models.batch_generate_content,
        )
        self.count_message_tokens = async_to_streamed_response_wrapper(
            models.count_message_tokens,
        )
        self.count_text_tokens = async_to_streamed_response_wrapper(
            models.count_text_tokens,
        )
        self.count_tokens = async_to_streamed_response_wrapper(
            models.count_tokens,
        )
        self.embed_content = async_to_streamed_response_wrapper(
            models.embed_content,
        )
        self.embed_text = async_to_streamed_response_wrapper(
            models.embed_text,
        )
        self.generate_answer = async_to_streamed_response_wrapper(
            models.generate_answer,
        )
        self.generate_content = async_to_streamed_response_wrapper(
            models.generate_content,
        )
        self.generate_message = async_to_streamed_response_wrapper(
            models.generate_message,
        )
        self.generate_text = async_to_streamed_response_wrapper(
            models.generate_text,
        )
        self.predict = async_to_streamed_response_wrapper(
            models.predict,
        )
        self.predict_long_running = async_to_streamed_response_wrapper(
            models.predict_long_running,
        )
        self.stream_generate_content = async_to_streamed_response_wrapper(
            models.stream_generate_content,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithStreamingResponse:
        return AsyncOperationsResourceWithStreamingResponse(self._models.operations)
