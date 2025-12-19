# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.beta.models import operation_list_params, operation_retrieve_params
from ....types.beta.operation import Operation
from ....types.beta.tuned_models.list_operations import ListOperations

__all__ = ["OperationsResource", "AsyncOperationsResource"]


class OperationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return OperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return OperationsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        operation: str,
        *,
        model: str,
        api_empty: operation_retrieve_params.api_empty | Omit = omit,
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
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        if not operation:
            raise ValueError(f"Expected a non-empty value for `operation` but received {operation!r}")
        return self._get(
            f"/v1beta/models/{model}/operations/{operation}",
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
                    operation_retrieve_params.OperationRetrieveParams,
                ),
            ),
            cast_to=Operation,
        )

    def list(
        self,
        model: str,
        *,
        api_empty: operation_list_params.api_empty | Omit = omit,
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
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return self._get(
            f"/v1beta/models/{model}/operations",
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
                    operation_list_params.OperationListParams,
                ),
            ),
            cast_to=ListOperations,
        )


class AsyncOperationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncOperationsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        operation: str,
        *,
        model: str,
        api_empty: operation_retrieve_params.api_empty | Omit = omit,
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
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        if not operation:
            raise ValueError(f"Expected a non-empty value for `operation` but received {operation!r}")
        return await self._get(
            f"/v1beta/models/{model}/operations/{operation}",
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
                    operation_retrieve_params.OperationRetrieveParams,
                ),
            ),
            cast_to=Operation,
        )

    async def list(
        self,
        model: str,
        *,
        api_empty: operation_list_params.api_empty | Omit = omit,
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
        if not model:
            raise ValueError(f"Expected a non-empty value for `model` but received {model!r}")
        return await self._get(
            f"/v1beta/models/{model}/operations",
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
                    operation_list_params.OperationListParams,
                ),
            ),
            cast_to=ListOperations,
        )


class OperationsResourceWithRawResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.retrieve = to_raw_response_wrapper(
            operations.retrieve,
        )
        self.list = to_raw_response_wrapper(
            operations.list,
        )


class AsyncOperationsResourceWithRawResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.retrieve = async_to_raw_response_wrapper(
            operations.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            operations.list,
        )


class OperationsResourceWithStreamingResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.retrieve = to_streamed_response_wrapper(
            operations.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            operations.list,
        )


class AsyncOperationsResourceWithStreamingResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.retrieve = async_to_streamed_response_wrapper(
            operations.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            operations.list,
        )
