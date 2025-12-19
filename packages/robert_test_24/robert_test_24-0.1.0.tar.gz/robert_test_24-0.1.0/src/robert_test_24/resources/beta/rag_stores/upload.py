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
from ....types.beta.operation import Operation
from ....types.beta.rag_stores import upload_get_operation_status_params

__all__ = ["UploadResource", "AsyncUploadResource"]


class UploadResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UploadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return UploadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UploadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return UploadResourceWithStreamingResponse(self)

    def get_operation_status(
        self,
        operations_id: str,
        *,
        rag_stores_id: str,
        api_empty: upload_get_operation_status_params.api_empty | Omit = omit,
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
        if not rag_stores_id:
            raise ValueError(f"Expected a non-empty value for `rag_stores_id` but received {rag_stores_id!r}")
        if not operations_id:
            raise ValueError(f"Expected a non-empty value for `operations_id` but received {operations_id!r}")
        return self._get(
            f"/v1beta/ragStores/{rag_stores_id}/upload/operations/{operations_id}",
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
                    upload_get_operation_status_params.UploadGetOperationStatusParams,
                ),
            ),
            cast_to=Operation,
        )


class AsyncUploadResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUploadResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUploadResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUploadResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncUploadResourceWithStreamingResponse(self)

    async def get_operation_status(
        self,
        operations_id: str,
        *,
        rag_stores_id: str,
        api_empty: upload_get_operation_status_params.api_empty | Omit = omit,
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
        if not rag_stores_id:
            raise ValueError(f"Expected a non-empty value for `rag_stores_id` but received {rag_stores_id!r}")
        if not operations_id:
            raise ValueError(f"Expected a non-empty value for `operations_id` but received {operations_id!r}")
        return await self._get(
            f"/v1beta/ragStores/{rag_stores_id}/upload/operations/{operations_id}",
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
                    upload_get_operation_status_params.UploadGetOperationStatusParams,
                ),
            ),
            cast_to=Operation,
        )


class UploadResourceWithRawResponse:
    def __init__(self, upload: UploadResource) -> None:
        self._upload = upload

        self.get_operation_status = to_raw_response_wrapper(
            upload.get_operation_status,
        )


class AsyncUploadResourceWithRawResponse:
    def __init__(self, upload: AsyncUploadResource) -> None:
        self._upload = upload

        self.get_operation_status = async_to_raw_response_wrapper(
            upload.get_operation_status,
        )


class UploadResourceWithStreamingResponse:
    def __init__(self, upload: UploadResource) -> None:
        self._upload = upload

        self.get_operation_status = to_streamed_response_wrapper(
            upload.get_operation_status,
        )


class AsyncUploadResourceWithStreamingResponse:
    def __init__(self, upload: AsyncUploadResource) -> None:
        self._upload = upload

        self.get_operation_status = async_to_streamed_response_wrapper(
            upload.get_operation_status,
        )
