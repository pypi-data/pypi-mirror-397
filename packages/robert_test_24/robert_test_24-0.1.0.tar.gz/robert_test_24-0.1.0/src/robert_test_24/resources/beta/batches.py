# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
    batch_list_params,
    batch_delete_params,
    batch_retrieve_params,
    batch_generate_content_batch_cancel_params,
    batch_update_generate_content_batch_update_embed_content_batch_params,
    batch_update_generate_content_batch_update_generate_content_batch_params,
)
from ..._base_client import make_request_options
from ...types.beta.operation import Operation
from ...types.beta.embed_content_batch import EmbedContentBatch
from ...types.beta.generate_content_batch import GenerateContentBatch
from ...types.beta.tuned_models.list_operations import ListOperations

__all__ = ["BatchesResource", "AsyncBatchesResource"]


class BatchesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BatchesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return BatchesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BatchesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return BatchesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        generate_content_batch: str,
        *,
        api_empty: batch_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Operation:
        """Gets the latest state of a long-running operation.

        Clients can use this method
        to poll the operation result at intervals as recommended by the API service.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generate_content_batch:
            raise ValueError(
                f"Expected a non-empty value for `generate_content_batch` but received {generate_content_batch!r}"
            )
        return self._get(
            f"/v1beta/batches/{generate_content_batch}",
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
                    batch_retrieve_params.BatchRetrieveParams,
                ),
            ),
            cast_to=Operation,
        )

    def list(
        self,
        *,
        api_empty: batch_list_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        filter: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        return_partial_success: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ListOperations:
        """Lists operations that match the specified filter in the request.

        If the server
        doesn't support this method, it returns `UNIMPLEMENTED`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          filter: The standard list filter.

          page_size: The standard list page size.

          page_token: The standard list page token.

          return_partial_success: When set to `true`, operations that are reachable are returned as normal, and
              those that are unreachable are returned in the
              [ListOperationsResponse.unreachable] field.

              This can only be `true` when reading across collections e.g. when `parent` is
              set to `"projects/example/locations/-"`.

              This field is not by default supported and will result in an `UNIMPLEMENTED`
              error if set unless explicitly documented otherwise in service or product
              specific documentation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1beta/batches",
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
                        "return_partial_success": return_partial_success,
                    },
                    batch_list_params.BatchListParams,
                ),
            ),
            cast_to=ListOperations,
        )

    def delete(
        self,
        generate_content_batch: str,
        *,
        api_empty: batch_delete_params.api_empty | Omit = omit,
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
        """Deletes a long-running operation.

        This method indicates that the client is no
        longer interested in the operation result. It does not cancel the operation. If
        the server doesn't support this method, it returns
        `google.rpc.Code.UNIMPLEMENTED`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generate_content_batch:
            raise ValueError(
                f"Expected a non-empty value for `generate_content_batch` but received {generate_content_batch!r}"
            )
        return self._delete(
            f"/v1beta/batches/{generate_content_batch}",
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
                    batch_delete_params.BatchDeleteParams,
                ),
            ),
            cast_to=object,
        )

    def generate_content_batch_cancel(
        self,
        generate_content_batch: str,
        *,
        api_empty: batch_generate_content_batch_cancel_params.api_empty | Omit = omit,
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
        """Starts asynchronous cancellation on a long-running operation.

        The server makes a
        best effort to cancel the operation, but success is not guaranteed. If the
        server doesn't support this method, it returns `google.rpc.Code.UNIMPLEMENTED`.
        Clients can use Operations.GetOperation or other methods to check whether the
        cancellation succeeded or whether the operation completed despite cancellation.
        On successful cancellation, the operation is not deleted; instead, it becomes an
        operation with an Operation.error value with a google.rpc.Status.code of `1`,
        corresponding to `Code.CANCELLED`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generate_content_batch:
            raise ValueError(
                f"Expected a non-empty value for `generate_content_batch` but received {generate_content_batch!r}"
            )
        return self._post(
            f"/v1beta/batches/{generate_content_batch}:cancel",
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
                    batch_generate_content_batch_cancel_params.BatchGenerateContentBatchCancelParams,
                ),
            ),
            cast_to=object,
        )

    def update_generate_content_batch_update_embed_content_batch(
        self,
        generate_content_batch: str,
        *,
        display_name: str,
        input_config: batch_update_generate_content_batch_update_embed_content_batch_params.InputConfig,
        model: str,
        api_empty: batch_update_generate_content_batch_update_embed_content_batch_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        update_mask: str | Omit = omit,
        priority: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EmbedContentBatch:
        """
        Updates a batch of EmbedContent requests for batch processing.

        Args:
          display_name: Required. The user-defined name of this batch.

          input_config: Configures the input to the batch request.

          model: Required. The name of the `Model` to use for generating the completion.

              Format: `models/{model}`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          update_mask: Optional. The list of fields to update.

          priority: Optional. The priority of the batch. Batches with a higher priority value will
              be processed before batches with a lower priority value. Negative values are
              allowed. Default is 0.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generate_content_batch:
            raise ValueError(
                f"Expected a non-empty value for `generate_content_batch` but received {generate_content_batch!r}"
            )
        return self._patch(
            f"/v1beta/batches/{generate_content_batch}:updateEmbedContentBatch",
            body=maybe_transform(
                {
                    "display_name": display_name,
                    "input_config": input_config,
                    "model": model,
                    "priority": priority,
                },
                batch_update_generate_content_batch_update_embed_content_batch_params.BatchUpdateGenerateContentBatchUpdateEmbedContentBatchParams,
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
                    batch_update_generate_content_batch_update_embed_content_batch_params.BatchUpdateGenerateContentBatchUpdateEmbedContentBatchParams,
                ),
            ),
            cast_to=EmbedContentBatch,
        )

    def update_generate_content_batch_update_generate_content_batch(
        self,
        generate_content_batch: str,
        *,
        display_name: str,
        input_config: batch_update_generate_content_batch_update_generate_content_batch_params.InputConfig,
        model: str,
        api_empty: batch_update_generate_content_batch_update_generate_content_batch_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        update_mask: str | Omit = omit,
        priority: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GenerateContentBatch:
        """
        Updates a batch of GenerateContent requests for batch processing.

        Args:
          display_name: Required. The user-defined name of this batch.

          input_config: Configures the input to the batch request.

          model: Required. The name of the `Model` to use for generating the completion.

              Format: `models/{model}`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          update_mask: Optional. The list of fields to update.

          priority: Optional. The priority of the batch. Batches with a higher priority value will
              be processed before batches with a lower priority value. Negative values are
              allowed. Default is 0.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generate_content_batch:
            raise ValueError(
                f"Expected a non-empty value for `generate_content_batch` but received {generate_content_batch!r}"
            )
        return self._patch(
            f"/v1beta/batches/{generate_content_batch}:updateGenerateContentBatch",
            body=maybe_transform(
                {
                    "display_name": display_name,
                    "input_config": input_config,
                    "model": model,
                    "priority": priority,
                },
                batch_update_generate_content_batch_update_generate_content_batch_params.BatchUpdateGenerateContentBatchUpdateGenerateContentBatchParams,
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
                    batch_update_generate_content_batch_update_generate_content_batch_params.BatchUpdateGenerateContentBatchUpdateGenerateContentBatchParams,
                ),
            ),
            cast_to=GenerateContentBatch,
        )


class AsyncBatchesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBatchesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBatchesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBatchesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncBatchesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        generate_content_batch: str,
        *,
        api_empty: batch_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Operation:
        """Gets the latest state of a long-running operation.

        Clients can use this method
        to poll the operation result at intervals as recommended by the API service.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generate_content_batch:
            raise ValueError(
                f"Expected a non-empty value for `generate_content_batch` but received {generate_content_batch!r}"
            )
        return await self._get(
            f"/v1beta/batches/{generate_content_batch}",
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
                    batch_retrieve_params.BatchRetrieveParams,
                ),
            ),
            cast_to=Operation,
        )

    async def list(
        self,
        *,
        api_empty: batch_list_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        filter: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        return_partial_success: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ListOperations:
        """Lists operations that match the specified filter in the request.

        If the server
        doesn't support this method, it returns `UNIMPLEMENTED`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          filter: The standard list filter.

          page_size: The standard list page size.

          page_token: The standard list page token.

          return_partial_success: When set to `true`, operations that are reachable are returned as normal, and
              those that are unreachable are returned in the
              [ListOperationsResponse.unreachable] field.

              This can only be `true` when reading across collections e.g. when `parent` is
              set to `"projects/example/locations/-"`.

              This field is not by default supported and will result in an `UNIMPLEMENTED`
              error if set unless explicitly documented otherwise in service or product
              specific documentation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1beta/batches",
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
                        "return_partial_success": return_partial_success,
                    },
                    batch_list_params.BatchListParams,
                ),
            ),
            cast_to=ListOperations,
        )

    async def delete(
        self,
        generate_content_batch: str,
        *,
        api_empty: batch_delete_params.api_empty | Omit = omit,
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
        """Deletes a long-running operation.

        This method indicates that the client is no
        longer interested in the operation result. It does not cancel the operation. If
        the server doesn't support this method, it returns
        `google.rpc.Code.UNIMPLEMENTED`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generate_content_batch:
            raise ValueError(
                f"Expected a non-empty value for `generate_content_batch` but received {generate_content_batch!r}"
            )
        return await self._delete(
            f"/v1beta/batches/{generate_content_batch}",
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
                    batch_delete_params.BatchDeleteParams,
                ),
            ),
            cast_to=object,
        )

    async def generate_content_batch_cancel(
        self,
        generate_content_batch: str,
        *,
        api_empty: batch_generate_content_batch_cancel_params.api_empty | Omit = omit,
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
        """Starts asynchronous cancellation on a long-running operation.

        The server makes a
        best effort to cancel the operation, but success is not guaranteed. If the
        server doesn't support this method, it returns `google.rpc.Code.UNIMPLEMENTED`.
        Clients can use Operations.GetOperation or other methods to check whether the
        cancellation succeeded or whether the operation completed despite cancellation.
        On successful cancellation, the operation is not deleted; instead, it becomes an
        operation with an Operation.error value with a google.rpc.Status.code of `1`,
        corresponding to `Code.CANCELLED`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generate_content_batch:
            raise ValueError(
                f"Expected a non-empty value for `generate_content_batch` but received {generate_content_batch!r}"
            )
        return await self._post(
            f"/v1beta/batches/{generate_content_batch}:cancel",
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
                    batch_generate_content_batch_cancel_params.BatchGenerateContentBatchCancelParams,
                ),
            ),
            cast_to=object,
        )

    async def update_generate_content_batch_update_embed_content_batch(
        self,
        generate_content_batch: str,
        *,
        display_name: str,
        input_config: batch_update_generate_content_batch_update_embed_content_batch_params.InputConfig,
        model: str,
        api_empty: batch_update_generate_content_batch_update_embed_content_batch_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        update_mask: str | Omit = omit,
        priority: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EmbedContentBatch:
        """
        Updates a batch of EmbedContent requests for batch processing.

        Args:
          display_name: Required. The user-defined name of this batch.

          input_config: Configures the input to the batch request.

          model: Required. The name of the `Model` to use for generating the completion.

              Format: `models/{model}`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          update_mask: Optional. The list of fields to update.

          priority: Optional. The priority of the batch. Batches with a higher priority value will
              be processed before batches with a lower priority value. Negative values are
              allowed. Default is 0.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generate_content_batch:
            raise ValueError(
                f"Expected a non-empty value for `generate_content_batch` but received {generate_content_batch!r}"
            )
        return await self._patch(
            f"/v1beta/batches/{generate_content_batch}:updateEmbedContentBatch",
            body=await async_maybe_transform(
                {
                    "display_name": display_name,
                    "input_config": input_config,
                    "model": model,
                    "priority": priority,
                },
                batch_update_generate_content_batch_update_embed_content_batch_params.BatchUpdateGenerateContentBatchUpdateEmbedContentBatchParams,
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
                    batch_update_generate_content_batch_update_embed_content_batch_params.BatchUpdateGenerateContentBatchUpdateEmbedContentBatchParams,
                ),
            ),
            cast_to=EmbedContentBatch,
        )

    async def update_generate_content_batch_update_generate_content_batch(
        self,
        generate_content_batch: str,
        *,
        display_name: str,
        input_config: batch_update_generate_content_batch_update_generate_content_batch_params.InputConfig,
        model: str,
        api_empty: batch_update_generate_content_batch_update_generate_content_batch_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        update_mask: str | Omit = omit,
        priority: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GenerateContentBatch:
        """
        Updates a batch of GenerateContent requests for batch processing.

        Args:
          display_name: Required. The user-defined name of this batch.

          input_config: Configures the input to the batch request.

          model: Required. The name of the `Model` to use for generating the completion.

              Format: `models/{model}`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          update_mask: Optional. The list of fields to update.

          priority: Optional. The priority of the batch. Batches with a higher priority value will
              be processed before batches with a lower priority value. Negative values are
              allowed. Default is 0.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generate_content_batch:
            raise ValueError(
                f"Expected a non-empty value for `generate_content_batch` but received {generate_content_batch!r}"
            )
        return await self._patch(
            f"/v1beta/batches/{generate_content_batch}:updateGenerateContentBatch",
            body=await async_maybe_transform(
                {
                    "display_name": display_name,
                    "input_config": input_config,
                    "model": model,
                    "priority": priority,
                },
                batch_update_generate_content_batch_update_generate_content_batch_params.BatchUpdateGenerateContentBatchUpdateGenerateContentBatchParams,
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
                    batch_update_generate_content_batch_update_generate_content_batch_params.BatchUpdateGenerateContentBatchUpdateGenerateContentBatchParams,
                ),
            ),
            cast_to=GenerateContentBatch,
        )


class BatchesResourceWithRawResponse:
    def __init__(self, batches: BatchesResource) -> None:
        self._batches = batches

        self.retrieve = to_raw_response_wrapper(
            batches.retrieve,
        )
        self.list = to_raw_response_wrapper(
            batches.list,
        )
        self.delete = to_raw_response_wrapper(
            batches.delete,
        )
        self.generate_content_batch_cancel = to_raw_response_wrapper(
            batches.generate_content_batch_cancel,
        )
        self.update_generate_content_batch_update_embed_content_batch = to_raw_response_wrapper(
            batches.update_generate_content_batch_update_embed_content_batch,
        )
        self.update_generate_content_batch_update_generate_content_batch = to_raw_response_wrapper(
            batches.update_generate_content_batch_update_generate_content_batch,
        )


class AsyncBatchesResourceWithRawResponse:
    def __init__(self, batches: AsyncBatchesResource) -> None:
        self._batches = batches

        self.retrieve = async_to_raw_response_wrapper(
            batches.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            batches.list,
        )
        self.delete = async_to_raw_response_wrapper(
            batches.delete,
        )
        self.generate_content_batch_cancel = async_to_raw_response_wrapper(
            batches.generate_content_batch_cancel,
        )
        self.update_generate_content_batch_update_embed_content_batch = async_to_raw_response_wrapper(
            batches.update_generate_content_batch_update_embed_content_batch,
        )
        self.update_generate_content_batch_update_generate_content_batch = async_to_raw_response_wrapper(
            batches.update_generate_content_batch_update_generate_content_batch,
        )


class BatchesResourceWithStreamingResponse:
    def __init__(self, batches: BatchesResource) -> None:
        self._batches = batches

        self.retrieve = to_streamed_response_wrapper(
            batches.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            batches.list,
        )
        self.delete = to_streamed_response_wrapper(
            batches.delete,
        )
        self.generate_content_batch_cancel = to_streamed_response_wrapper(
            batches.generate_content_batch_cancel,
        )
        self.update_generate_content_batch_update_embed_content_batch = to_streamed_response_wrapper(
            batches.update_generate_content_batch_update_embed_content_batch,
        )
        self.update_generate_content_batch_update_generate_content_batch = to_streamed_response_wrapper(
            batches.update_generate_content_batch_update_generate_content_batch,
        )


class AsyncBatchesResourceWithStreamingResponse:
    def __init__(self, batches: AsyncBatchesResource) -> None:
        self._batches = batches

        self.retrieve = async_to_streamed_response_wrapper(
            batches.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            batches.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            batches.delete,
        )
        self.generate_content_batch_cancel = async_to_streamed_response_wrapper(
            batches.generate_content_batch_cancel,
        )
        self.update_generate_content_batch_update_embed_content_batch = async_to_streamed_response_wrapper(
            batches.update_generate_content_batch_update_embed_content_batch,
        )
        self.update_generate_content_batch_update_generate_content_batch = async_to_streamed_response_wrapper(
            batches.update_generate_content_batch_update_generate_content_batch,
        )
