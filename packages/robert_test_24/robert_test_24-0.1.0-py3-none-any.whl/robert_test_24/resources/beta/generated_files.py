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
from ...types.beta import generated_file_retrieve_params, generated_file_retrieve_generated_files_params
from ..._base_client import make_request_options
from ...types.beta.generated_file import GeneratedFile
from ...types.beta.generated_file_retrieve_generated_files_response import GeneratedFileRetrieveGeneratedFilesResponse

__all__ = ["GeneratedFilesResource", "AsyncGeneratedFilesResource"]


class GeneratedFilesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GeneratedFilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return GeneratedFilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GeneratedFilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return GeneratedFilesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        generated_file: str,
        *,
        api_empty: generated_file_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GeneratedFile:
        """Gets a generated file.

        When calling this method via REST, only the metadata of
        the generated file is returned. To retrieve the file content via REST, add
        alt=media as a query parameter.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generated_file:
            raise ValueError(f"Expected a non-empty value for `generated_file` but received {generated_file!r}")
        return self._get(
            f"/v1beta/generatedFiles/{generated_file}",
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
                    generated_file_retrieve_params.GeneratedFileRetrieveParams,
                ),
            ),
            cast_to=GeneratedFile,
        )

    def retrieve_generated_files(
        self,
        *,
        api_empty: generated_file_retrieve_generated_files_params.api_empty | Omit = omit,
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
    ) -> GeneratedFileRetrieveGeneratedFilesResponse:
        """
        Lists the generated files owned by the requesting project.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. Maximum number of `GeneratedFile`s to return per page. If unspecified,
              defaults to 10. Maximum `page_size` is 50.

          page_token: Optional. A page token from a previous `ListGeneratedFiles` call.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1beta/generatedFiles",
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
                    generated_file_retrieve_generated_files_params.GeneratedFileRetrieveGeneratedFilesParams,
                ),
            ),
            cast_to=GeneratedFileRetrieveGeneratedFilesResponse,
        )


class AsyncGeneratedFilesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGeneratedFilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncGeneratedFilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGeneratedFilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncGeneratedFilesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        generated_file: str,
        *,
        api_empty: generated_file_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GeneratedFile:
        """Gets a generated file.

        When calling this method via REST, only the metadata of
        the generated file is returned. To retrieve the file content via REST, add
        alt=media as a query parameter.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not generated_file:
            raise ValueError(f"Expected a non-empty value for `generated_file` but received {generated_file!r}")
        return await self._get(
            f"/v1beta/generatedFiles/{generated_file}",
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
                    generated_file_retrieve_params.GeneratedFileRetrieveParams,
                ),
            ),
            cast_to=GeneratedFile,
        )

    async def retrieve_generated_files(
        self,
        *,
        api_empty: generated_file_retrieve_generated_files_params.api_empty | Omit = omit,
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
    ) -> GeneratedFileRetrieveGeneratedFilesResponse:
        """
        Lists the generated files owned by the requesting project.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. Maximum number of `GeneratedFile`s to return per page. If unspecified,
              defaults to 10. Maximum `page_size` is 50.

          page_token: Optional. A page token from a previous `ListGeneratedFiles` call.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1beta/generatedFiles",
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
                    generated_file_retrieve_generated_files_params.GeneratedFileRetrieveGeneratedFilesParams,
                ),
            ),
            cast_to=GeneratedFileRetrieveGeneratedFilesResponse,
        )


class GeneratedFilesResourceWithRawResponse:
    def __init__(self, generated_files: GeneratedFilesResource) -> None:
        self._generated_files = generated_files

        self.retrieve = to_raw_response_wrapper(
            generated_files.retrieve,
        )
        self.retrieve_generated_files = to_raw_response_wrapper(
            generated_files.retrieve_generated_files,
        )


class AsyncGeneratedFilesResourceWithRawResponse:
    def __init__(self, generated_files: AsyncGeneratedFilesResource) -> None:
        self._generated_files = generated_files

        self.retrieve = async_to_raw_response_wrapper(
            generated_files.retrieve,
        )
        self.retrieve_generated_files = async_to_raw_response_wrapper(
            generated_files.retrieve_generated_files,
        )


class GeneratedFilesResourceWithStreamingResponse:
    def __init__(self, generated_files: GeneratedFilesResource) -> None:
        self._generated_files = generated_files

        self.retrieve = to_streamed_response_wrapper(
            generated_files.retrieve,
        )
        self.retrieve_generated_files = to_streamed_response_wrapper(
            generated_files.retrieve_generated_files,
        )


class AsyncGeneratedFilesResourceWithStreamingResponse:
    def __init__(self, generated_files: AsyncGeneratedFilesResource) -> None:
        self._generated_files = generated_files

        self.retrieve = async_to_streamed_response_wrapper(
            generated_files.retrieve,
        )
        self.retrieve_generated_files = async_to_streamed_response_wrapper(
            generated_files.retrieve_generated_files,
        )
