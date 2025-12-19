# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from .chunks import (
    ChunksResource,
    AsyncChunksResource,
    ChunksResourceWithRawResponse,
    AsyncChunksResourceWithRawResponse,
    ChunksResourceWithStreamingResponse,
    AsyncChunksResourceWithStreamingResponse,
)
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
from .....types.beta.corpora import (
    document_update_params,
    document_chunks_batch_create_params,
    document_chunks_batch_delete_params,
    document_chunks_batch_update_params,
)
from .....types.beta.rag_stores.document import Document
from .....types.beta.custom_metadata_param import CustomMetadataParam
from .....types.beta.corpora.document_chunks_batch_create_response import DocumentChunksBatchCreateResponse
from .....types.beta.corpora.document_chunks_batch_update_response import DocumentChunksBatchUpdateResponse

__all__ = ["DocumentsResource", "AsyncDocumentsResource"]


class DocumentsResource(SyncAPIResource):
    @cached_property
    def chunks(self) -> ChunksResource:
        return ChunksResource(self._client)

    @cached_property
    def with_raw_response(self) -> DocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return DocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return DocumentsResourceWithStreamingResponse(self)

    def update(
        self,
        document: str,
        *,
        corpus: str,
        update_mask: str,
        api_empty: document_update_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        custom_metadata: Iterable[CustomMetadataParam] | Omit = omit,
        display_name: str | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Document:
        """Updates a `Document`.

        Args:
          update_mask: Required.

        The list of fields to update. Currently, this only supports updating
              `display_name` and `custom_metadata`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          custom_metadata: Optional. User provided custom metadata stored as key-value pairs used for
              querying. A `Document` can have a maximum of 20 `CustomMetadata`.

          display_name: Optional. The human-readable display name for the `Document`. The display name
              must be no more than 512 characters in length, including spaces. Example:
              "Semantic Retriever Documentation"

          name: Immutable. Identifier. The `Document` resource name. The ID (name excluding the
              "ragStores/\\**/documents/" prefix) can contain up to 40 characters that are
              lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If
              the name is empty on create, a unique name will be derived from `display_name`
              along with a 12 character random suffix. Example:
              `ragStores/{corpus_id}/documents/my-awesome-doc-123a456b789c`

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return self._patch(
            f"/v1beta/corpora/{corpus}/documents/{document}",
            body=maybe_transform(
                {
                    "custom_metadata": custom_metadata,
                    "display_name": display_name,
                    "name": name,
                },
                document_update_params.DocumentUpdateParams,
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
                    document_update_params.DocumentUpdateParams,
                ),
            ),
            cast_to=Document,
        )

    def chunks_batch_create(
        self,
        document: str,
        *,
        corpus: str,
        requests: Iterable[document_chunks_batch_create_params.Request],
        api_empty: document_chunks_batch_create_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentChunksBatchCreateResponse:
        """Batch create `Chunk`s.

        Args:
          requests: Required.

        The request messages specifying the `Chunk`s to create. A maximum of
              100 `Chunk`s can be created in a batch.

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
        return self._post(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks:batchCreate",
            body=maybe_transform(
                {"requests": requests}, document_chunks_batch_create_params.DocumentChunksBatchCreateParams
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
                    document_chunks_batch_create_params.DocumentChunksBatchCreateParams,
                ),
            ),
            cast_to=DocumentChunksBatchCreateResponse,
        )

    def chunks_batch_delete(
        self,
        document: str,
        *,
        corpus: str,
        requests: Iterable[document_chunks_batch_delete_params.Request],
        api_empty: document_chunks_batch_delete_params.api_empty | Omit = omit,
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
        """Batch delete `Chunk`s.

        Args:
          requests: Required.

        The request messages specifying the `Chunk`s to delete.

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
        return self._post(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks:batchDelete",
            body=maybe_transform(
                {"requests": requests}, document_chunks_batch_delete_params.DocumentChunksBatchDeleteParams
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
                    document_chunks_batch_delete_params.DocumentChunksBatchDeleteParams,
                ),
            ),
            cast_to=object,
        )

    def chunks_batch_update(
        self,
        document: str,
        *,
        corpus: str,
        requests: Iterable[document_chunks_batch_update_params.Request],
        api_empty: document_chunks_batch_update_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentChunksBatchUpdateResponse:
        """Batch update `Chunk`s.

        Args:
          requests: Required.

        The request messages specifying the `Chunk`s to update. A maximum of
              100 `Chunk`s can be updated in a batch.

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
        return self._post(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks:batchUpdate",
            body=maybe_transform(
                {"requests": requests}, document_chunks_batch_update_params.DocumentChunksBatchUpdateParams
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
                    document_chunks_batch_update_params.DocumentChunksBatchUpdateParams,
                ),
            ),
            cast_to=DocumentChunksBatchUpdateResponse,
        )


class AsyncDocumentsResource(AsyncAPIResource):
    @cached_property
    def chunks(self) -> AsyncChunksResource:
        return AsyncChunksResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncDocumentsResourceWithStreamingResponse(self)

    async def update(
        self,
        document: str,
        *,
        corpus: str,
        update_mask: str,
        api_empty: document_update_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        custom_metadata: Iterable[CustomMetadataParam] | Omit = omit,
        display_name: str | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Document:
        """Updates a `Document`.

        Args:
          update_mask: Required.

        The list of fields to update. Currently, this only supports updating
              `display_name` and `custom_metadata`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          custom_metadata: Optional. User provided custom metadata stored as key-value pairs used for
              querying. A `Document` can have a maximum of 20 `CustomMetadata`.

          display_name: Optional. The human-readable display name for the `Document`. The display name
              must be no more than 512 characters in length, including spaces. Example:
              "Semantic Retriever Documentation"

          name: Immutable. Identifier. The `Document` resource name. The ID (name excluding the
              "ragStores/\\**/documents/" prefix) can contain up to 40 characters that are
              lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If
              the name is empty on create, a unique name will be derived from `display_name`
              along with a 12 character random suffix. Example:
              `ragStores/{corpus_id}/documents/my-awesome-doc-123a456b789c`

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return await self._patch(
            f"/v1beta/corpora/{corpus}/documents/{document}",
            body=await async_maybe_transform(
                {
                    "custom_metadata": custom_metadata,
                    "display_name": display_name,
                    "name": name,
                },
                document_update_params.DocumentUpdateParams,
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
                    document_update_params.DocumentUpdateParams,
                ),
            ),
            cast_to=Document,
        )

    async def chunks_batch_create(
        self,
        document: str,
        *,
        corpus: str,
        requests: Iterable[document_chunks_batch_create_params.Request],
        api_empty: document_chunks_batch_create_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentChunksBatchCreateResponse:
        """Batch create `Chunk`s.

        Args:
          requests: Required.

        The request messages specifying the `Chunk`s to create. A maximum of
              100 `Chunk`s can be created in a batch.

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
        return await self._post(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks:batchCreate",
            body=await async_maybe_transform(
                {"requests": requests}, document_chunks_batch_create_params.DocumentChunksBatchCreateParams
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
                    document_chunks_batch_create_params.DocumentChunksBatchCreateParams,
                ),
            ),
            cast_to=DocumentChunksBatchCreateResponse,
        )

    async def chunks_batch_delete(
        self,
        document: str,
        *,
        corpus: str,
        requests: Iterable[document_chunks_batch_delete_params.Request],
        api_empty: document_chunks_batch_delete_params.api_empty | Omit = omit,
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
        """Batch delete `Chunk`s.

        Args:
          requests: Required.

        The request messages specifying the `Chunk`s to delete.

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
        return await self._post(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks:batchDelete",
            body=await async_maybe_transform(
                {"requests": requests}, document_chunks_batch_delete_params.DocumentChunksBatchDeleteParams
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
                    document_chunks_batch_delete_params.DocumentChunksBatchDeleteParams,
                ),
            ),
            cast_to=object,
        )

    async def chunks_batch_update(
        self,
        document: str,
        *,
        corpus: str,
        requests: Iterable[document_chunks_batch_update_params.Request],
        api_empty: document_chunks_batch_update_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentChunksBatchUpdateResponse:
        """Batch update `Chunk`s.

        Args:
          requests: Required.

        The request messages specifying the `Chunk`s to update. A maximum of
              100 `Chunk`s can be updated in a batch.

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
        return await self._post(
            f"/v1beta/corpora/{corpus}/documents/{document}/chunks:batchUpdate",
            body=await async_maybe_transform(
                {"requests": requests}, document_chunks_batch_update_params.DocumentChunksBatchUpdateParams
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
                    document_chunks_batch_update_params.DocumentChunksBatchUpdateParams,
                ),
            ),
            cast_to=DocumentChunksBatchUpdateResponse,
        )


class DocumentsResourceWithRawResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.update = to_raw_response_wrapper(
            documents.update,
        )
        self.chunks_batch_create = to_raw_response_wrapper(
            documents.chunks_batch_create,
        )
        self.chunks_batch_delete = to_raw_response_wrapper(
            documents.chunks_batch_delete,
        )
        self.chunks_batch_update = to_raw_response_wrapper(
            documents.chunks_batch_update,
        )

    @cached_property
    def chunks(self) -> ChunksResourceWithRawResponse:
        return ChunksResourceWithRawResponse(self._documents.chunks)


class AsyncDocumentsResourceWithRawResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.update = async_to_raw_response_wrapper(
            documents.update,
        )
        self.chunks_batch_create = async_to_raw_response_wrapper(
            documents.chunks_batch_create,
        )
        self.chunks_batch_delete = async_to_raw_response_wrapper(
            documents.chunks_batch_delete,
        )
        self.chunks_batch_update = async_to_raw_response_wrapper(
            documents.chunks_batch_update,
        )

    @cached_property
    def chunks(self) -> AsyncChunksResourceWithRawResponse:
        return AsyncChunksResourceWithRawResponse(self._documents.chunks)


class DocumentsResourceWithStreamingResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.update = to_streamed_response_wrapper(
            documents.update,
        )
        self.chunks_batch_create = to_streamed_response_wrapper(
            documents.chunks_batch_create,
        )
        self.chunks_batch_delete = to_streamed_response_wrapper(
            documents.chunks_batch_delete,
        )
        self.chunks_batch_update = to_streamed_response_wrapper(
            documents.chunks_batch_update,
        )

    @cached_property
    def chunks(self) -> ChunksResourceWithStreamingResponse:
        return ChunksResourceWithStreamingResponse(self._documents.chunks)


class AsyncDocumentsResourceWithStreamingResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.update = async_to_streamed_response_wrapper(
            documents.update,
        )
        self.chunks_batch_create = async_to_streamed_response_wrapper(
            documents.chunks_batch_create,
        )
        self.chunks_batch_delete = async_to_streamed_response_wrapper(
            documents.chunks_batch_delete,
        )
        self.chunks_batch_update = async_to_streamed_response_wrapper(
            documents.chunks_batch_update,
        )

    @cached_property
    def chunks(self) -> AsyncChunksResourceWithStreamingResponse:
        return AsyncChunksResourceWithStreamingResponse(self._documents.chunks)
