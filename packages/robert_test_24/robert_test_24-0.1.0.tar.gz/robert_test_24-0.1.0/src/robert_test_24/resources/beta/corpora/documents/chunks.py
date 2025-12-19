# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.beta.corpora.documents import (
    chunk_list_params,
    chunk_create_params,
    chunk_delete_params,
    chunk_update_params,
    chunk_retrieve_params,
)
from .....types.beta.custom_metadata_param import CustomMetadataParam
from .....types.beta.corpora.documents.chunk import Chunk
from .....types.beta.corpora.documents.chunk_list_response import ChunkListResponse

__all__ = ["ChunksResource", "AsyncChunksResource"]


class ChunksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ChunksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return ChunksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChunksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return ChunksResourceWithStreamingResponse(self)

    def create(
        self,
        document: str,
        *,
        corpus: str,
        data: chunk_create_params.Data,
        api_empty: chunk_create_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        custom_metadata: Iterable[CustomMetadataParam] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Chunk:
        """
        Creates a `Chunk`.

        Args:
          data: Extracted data that represents the `Chunk` content.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          custom_metadata: Optional. User provided custom metadata stored as key-value pairs. The maximum
              number of `CustomMetadata` per chunk is 20.

          name: Immutable. Identifier. The `Chunk` resource name. The ID (name excluding the
              "corpora/_/documents/_/chunks/" prefix) can contain up to 40 characters that are
              lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If
              the name is empty on create, a random 12-character unique ID will be generated.
              Example: `corpora/{corpus_id}/documents/{document_id}/chunks/123a456b789c`

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return self._post(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks",
            body=maybe_transform(
                {
                    "data": data,
                    "custom_metadata": custom_metadata,
                    "name": name,
                },
                chunk_create_params.ChunkCreateParams,
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
                    chunk_create_params.ChunkCreateParams,
                ),
            ),
            cast_to=Chunk,
        )

    def retrieve(
        self,
        chunk: str,
        *,
        corpus: str,
        document: str,
        api_empty: chunk_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Chunk:
        """
        Gets information about a specific `Chunk`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        if not chunk:
            raise ValueError(f"Expected a non-empty value for `chunk` but received {chunk!r}")
        return self._get(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks/{chunk}",
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
                    chunk_retrieve_params.ChunkRetrieveParams,
                ),
            ),
            cast_to=Chunk,
        )

    def update(
        self,
        chunk: str,
        *,
        corpus: str,
        document: str,
        update_mask: str,
        data: chunk_update_params.Data,
        api_empty: chunk_update_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        custom_metadata: Iterable[CustomMetadataParam] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Chunk:
        """Updates a `Chunk`.

        Args:
          update_mask: Required.

        The list of fields to update. Currently, this only supports updating
              `custom_metadata` and `data`.

          data: Extracted data that represents the `Chunk` content.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          custom_metadata: Optional. User provided custom metadata stored as key-value pairs. The maximum
              number of `CustomMetadata` per chunk is 20.

          name: Immutable. Identifier. The `Chunk` resource name. The ID (name excluding the
              "corpora/_/documents/_/chunks/" prefix) can contain up to 40 characters that are
              lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If
              the name is empty on create, a random 12-character unique ID will be generated.
              Example: `corpora/{corpus_id}/documents/{document_id}/chunks/123a456b789c`

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        if not chunk:
            raise ValueError(f"Expected a non-empty value for `chunk` but received {chunk!r}")
        return self._patch(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks/{chunk}",
            body=maybe_transform(
                {
                    "data": data,
                    "custom_metadata": custom_metadata,
                    "name": name,
                },
                chunk_update_params.ChunkUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "update_mask": update_mask,
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    chunk_update_params.ChunkUpdateParams,
                ),
            ),
            cast_to=Chunk,
        )

    def list(
        self,
        document: str,
        *,
        corpus: str,
        api_empty: chunk_list_params.api_empty | Omit = omit,
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
    ) -> ChunkListResponse:
        """
        Lists all `Chunk`s in a `Document`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of `Chunk`s to return (per page). The service may
              return fewer `Chunk`s.

              If unspecified, at most 10 `Chunk`s will be returned. The maximum size limit is
              100 `Chunk`s per page.

          page_token: Optional. A page token, received from a previous `ListChunks` call.

              Provide the `next_page_token` returned in the response as an argument to the
              next request to retrieve the next page.

              When paginating, all other parameters provided to `ListChunks` must match the
              call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return self._get(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks",
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
                    chunk_list_params.ChunkListParams,
                ),
            ),
            cast_to=ChunkListResponse,
        )

    def delete(
        self,
        chunk: str,
        *,
        corpus: str,
        document: str,
        api_empty: chunk_delete_params.api_empty | Omit = omit,
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
        Deletes a `Chunk`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        if not chunk:
            raise ValueError(f"Expected a non-empty value for `chunk` but received {chunk!r}")
        return self._delete(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks/{chunk}",
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
                    chunk_delete_params.ChunkDeleteParams,
                ),
            ),
            cast_to=object,
        )


class AsyncChunksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncChunksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncChunksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChunksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncChunksResourceWithStreamingResponse(self)

    async def create(
        self,
        document: str,
        *,
        corpus: str,
        data: chunk_create_params.Data,
        api_empty: chunk_create_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        custom_metadata: Iterable[CustomMetadataParam] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Chunk:
        """
        Creates a `Chunk`.

        Args:
          data: Extracted data that represents the `Chunk` content.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          custom_metadata: Optional. User provided custom metadata stored as key-value pairs. The maximum
              number of `CustomMetadata` per chunk is 20.

          name: Immutable. Identifier. The `Chunk` resource name. The ID (name excluding the
              "corpora/_/documents/_/chunks/" prefix) can contain up to 40 characters that are
              lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If
              the name is empty on create, a random 12-character unique ID will be generated.
              Example: `corpora/{corpus_id}/documents/{document_id}/chunks/123a456b789c`

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return await self._post(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks",
            body=await async_maybe_transform(
                {
                    "data": data,
                    "custom_metadata": custom_metadata,
                    "name": name,
                },
                chunk_create_params.ChunkCreateParams,
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
                    chunk_create_params.ChunkCreateParams,
                ),
            ),
            cast_to=Chunk,
        )

    async def retrieve(
        self,
        chunk: str,
        *,
        corpus: str,
        document: str,
        api_empty: chunk_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Chunk:
        """
        Gets information about a specific `Chunk`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        if not chunk:
            raise ValueError(f"Expected a non-empty value for `chunk` but received {chunk!r}")
        return await self._get(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks/{chunk}",
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
                    chunk_retrieve_params.ChunkRetrieveParams,
                ),
            ),
            cast_to=Chunk,
        )

    async def update(
        self,
        chunk: str,
        *,
        corpus: str,
        document: str,
        update_mask: str,
        data: chunk_update_params.Data,
        api_empty: chunk_update_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        custom_metadata: Iterable[CustomMetadataParam] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Chunk:
        """Updates a `Chunk`.

        Args:
          update_mask: Required.

        The list of fields to update. Currently, this only supports updating
              `custom_metadata` and `data`.

          data: Extracted data that represents the `Chunk` content.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          custom_metadata: Optional. User provided custom metadata stored as key-value pairs. The maximum
              number of `CustomMetadata` per chunk is 20.

          name: Immutable. Identifier. The `Chunk` resource name. The ID (name excluding the
              "corpora/_/documents/_/chunks/" prefix) can contain up to 40 characters that are
              lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If
              the name is empty on create, a random 12-character unique ID will be generated.
              Example: `corpora/{corpus_id}/documents/{document_id}/chunks/123a456b789c`

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        if not chunk:
            raise ValueError(f"Expected a non-empty value for `chunk` but received {chunk!r}")
        return await self._patch(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks/{chunk}",
            body=await async_maybe_transform(
                {
                    "data": data,
                    "custom_metadata": custom_metadata,
                    "name": name,
                },
                chunk_update_params.ChunkUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "update_mask": update_mask,
                        "api_empty": api_empty,
                        "alt": alt,
                        "callback": callback,
                        "pretty_print": pretty_print,
                    },
                    chunk_update_params.ChunkUpdateParams,
                ),
            ),
            cast_to=Chunk,
        )

    async def list(
        self,
        document: str,
        *,
        corpus: str,
        api_empty: chunk_list_params.api_empty | Omit = omit,
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
    ) -> ChunkListResponse:
        """
        Lists all `Chunk`s in a `Document`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of `Chunk`s to return (per page). The service may
              return fewer `Chunk`s.

              If unspecified, at most 10 `Chunk`s will be returned. The maximum size limit is
              100 `Chunk`s per page.

          page_token: Optional. A page token, received from a previous `ListChunks` call.

              Provide the `next_page_token` returned in the response as an argument to the
              next request to retrieve the next page.

              When paginating, all other parameters provided to `ListChunks` must match the
              call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return await self._get(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks",
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
                    chunk_list_params.ChunkListParams,
                ),
            ),
            cast_to=ChunkListResponse,
        )

    async def delete(
        self,
        chunk: str,
        *,
        corpus: str,
        document: str,
        api_empty: chunk_delete_params.api_empty | Omit = omit,
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
        Deletes a `Chunk`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        if not chunk:
            raise ValueError(f"Expected a non-empty value for `chunk` but received {chunk!r}")
        return await self._delete(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks/{chunk}",
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
                    chunk_delete_params.ChunkDeleteParams,
                ),
            ),
            cast_to=object,
        )


class ChunksResourceWithRawResponse:
    def __init__(self, chunks: ChunksResource) -> None:
        self._chunks = chunks

        self.create = to_raw_response_wrapper(
            chunks.create,
        )
        self.retrieve = to_raw_response_wrapper(
            chunks.retrieve,
        )
        self.update = to_raw_response_wrapper(
            chunks.update,
        )
        self.list = to_raw_response_wrapper(
            chunks.list,
        )
        self.delete = to_raw_response_wrapper(
            chunks.delete,
        )


class AsyncChunksResourceWithRawResponse:
    def __init__(self, chunks: AsyncChunksResource) -> None:
        self._chunks = chunks

        self.create = async_to_raw_response_wrapper(
            chunks.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            chunks.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            chunks.update,
        )
        self.list = async_to_raw_response_wrapper(
            chunks.list,
        )
        self.delete = async_to_raw_response_wrapper(
            chunks.delete,
        )


class ChunksResourceWithStreamingResponse:
    def __init__(self, chunks: ChunksResource) -> None:
        self._chunks = chunks

        self.create = to_streamed_response_wrapper(
            chunks.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            chunks.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            chunks.update,
        )
        self.list = to_streamed_response_wrapper(
            chunks.list,
        )
        self.delete = to_streamed_response_wrapper(
            chunks.delete,
        )


class AsyncChunksResourceWithStreamingResponse:
    def __init__(self, chunks: AsyncChunksResource) -> None:
        self._chunks = chunks

        self.create = async_to_streamed_response_wrapper(
            chunks.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            chunks.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            chunks.update,
        )
        self.list = async_to_streamed_response_wrapper(
            chunks.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            chunks.delete,
        )
