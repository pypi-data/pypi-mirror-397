# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
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
from ....types.beta.rag_stores import (
    document_list_params,
    document_query_params,
    document_create_params,
    document_delete_params,
    document_retrieve_params,
)
from ....types.beta.rag_stores.document import Document
from ....types.beta.custom_metadata_param import CustomMetadataParam
from ....types.beta.metadata_filter_param import MetadataFilterParam
from ....types.beta.rag_stores.document_list_response import DocumentListResponse
from ....types.beta.rag_stores.document_query_response import DocumentQueryResponse

__all__ = ["DocumentsResource", "AsyncDocumentsResource"]


class DocumentsResource(SyncAPIResource):
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

    def create(
        self,
        rag_store: str,
        *,
        api_empty: document_create_params.api_empty | Omit = omit,
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
        """
        Creates an empty `Document`.

        Args:
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
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        return self._post(
            f"/v1beta/ragStores/{rag_store}/documents",
            body=maybe_transform(
                {
                    "custom_metadata": custom_metadata,
                    "display_name": display_name,
                    "name": name,
                },
                document_create_params.DocumentCreateParams,
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
                    document_create_params.DocumentCreateParams,
                ),
            ),
            cast_to=Document,
        )

    def retrieve(
        self,
        document: str,
        *,
        rag_store: str,
        api_empty: document_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Document:
        """
        Gets information about a specific `Document`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return self._get(
            f"/v1beta/ragStores/{rag_store}/documents/{document}",
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
                    document_retrieve_params.DocumentRetrieveParams,
                ),
            ),
            cast_to=Document,
        )

    def list(
        self,
        rag_store: str,
        *,
        api_empty: document_list_params.api_empty | Omit = omit,
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
    ) -> DocumentListResponse:
        """
        Lists all `Document`s in a `Corpus`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of `Document`s to return (per page). The service
              may return fewer `Document`s.

              If unspecified, at most 10 `Document`s will be returned. The maximum size limit
              is 20 `Document`s per page.

          page_token: Optional. A page token, received from a previous `ListDocuments` call.

              Provide the `next_page_token` returned in the response as an argument to the
              next request to retrieve the next page.

              When paginating, all other parameters provided to `ListDocuments` must match the
              call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        return self._get(
            f"/v1beta/ragStores/{rag_store}/documents",
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
                    document_list_params.DocumentListParams,
                ),
            ),
            cast_to=DocumentListResponse,
        )

    def delete(
        self,
        document: str,
        *,
        rag_store: str,
        api_empty: document_delete_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        force: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Deletes a `Document`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          force: Optional. If set to true, any `Chunk`s and objects related to this `Document`
              will also be deleted.

              If false (the default), a `FAILED_PRECONDITION` error will be returned if
              `Document` contains any `Chunk`s.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return self._delete(
            f"/v1beta/ragStores/{rag_store}/documents/{document}",
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
                        "force": force,
                    },
                    document_delete_params.DocumentDeleteParams,
                ),
            ),
            cast_to=object,
        )

    def query(
        self,
        document: str,
        *,
        rag_store: str,
        query: str,
        api_empty: document_query_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        metadata_filters: Iterable[MetadataFilterParam] | Omit = omit,
        results_count: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentQueryResponse:
        """Performs semantic search over a `Document`.

        Args:
          query: Required.

        Query string to perform semantic search.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          metadata_filters: Optional. Filter for `Chunk` metadata. Each `MetadataFilter` object should
              correspond to a unique key. Multiple `MetadataFilter` objects are joined by
              logical "AND"s.

              Note: `Document`-level filtering is not supported for this request because a
              `Document` name is already specified.

              Example query: (year >= 2020 OR year < 2010) AND (genre = drama OR genre =
              action)

              `MetadataFilter` object list: metadata_filters = [ {key =
              "chunk.custom_metadata.year" conditions = [{int_value = 2020, operation =
              GREATER_EQUAL}, {int_value = 2010, operation = LESS}}, {key =
              "chunk.custom_metadata.genre" conditions = [{string_value = "drama", operation =
              EQUAL}, {string_value = "action", operation = EQUAL}}]

              Example query for a numeric range of values: (year > 2015 AND year <= 2020)

              `MetadataFilter` object list: metadata_filters = [ {key =
              "chunk.custom_metadata.year" conditions = [{int_value = 2015, operation =
              GREATER}]}, {key = "chunk.custom_metadata.year" conditions = [{int_value = 2020,
              operation = LESS_EQUAL}]}]

              Note: "AND"s for the same key are only supported for numeric values. String
              values only support "OR"s for the same key.

          results_count: Optional. The maximum number of `Chunk`s to return. The service may return fewer
              `Chunk`s.

              If unspecified, at most 10 `Chunk`s will be returned. The maximum specified
              result count is 100.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return self._post(
            f"/v1beta/ragStores/{rag_store}/documents/{document}:query",
            body=maybe_transform(
                {
                    "query": query,
                    "metadata_filters": metadata_filters,
                    "results_count": results_count,
                },
                document_query_params.DocumentQueryParams,
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
                    document_query_params.DocumentQueryParams,
                ),
            ),
            cast_to=DocumentQueryResponse,
        )


class AsyncDocumentsResource(AsyncAPIResource):
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

    async def create(
        self,
        rag_store: str,
        *,
        api_empty: document_create_params.api_empty | Omit = omit,
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
        """
        Creates an empty `Document`.

        Args:
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
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        return await self._post(
            f"/v1beta/ragStores/{rag_store}/documents",
            body=await async_maybe_transform(
                {
                    "custom_metadata": custom_metadata,
                    "display_name": display_name,
                    "name": name,
                },
                document_create_params.DocumentCreateParams,
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
                    document_create_params.DocumentCreateParams,
                ),
            ),
            cast_to=Document,
        )

    async def retrieve(
        self,
        document: str,
        *,
        rag_store: str,
        api_empty: document_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Document:
        """
        Gets information about a specific `Document`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return await self._get(
            f"/v1beta/ragStores/{rag_store}/documents/{document}",
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
                    document_retrieve_params.DocumentRetrieveParams,
                ),
            ),
            cast_to=Document,
        )

    async def list(
        self,
        rag_store: str,
        *,
        api_empty: document_list_params.api_empty | Omit = omit,
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
    ) -> DocumentListResponse:
        """
        Lists all `Document`s in a `Corpus`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of `Document`s to return (per page). The service
              may return fewer `Document`s.

              If unspecified, at most 10 `Document`s will be returned. The maximum size limit
              is 20 `Document`s per page.

          page_token: Optional. A page token, received from a previous `ListDocuments` call.

              Provide the `next_page_token` returned in the response as an argument to the
              next request to retrieve the next page.

              When paginating, all other parameters provided to `ListDocuments` must match the
              call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        return await self._get(
            f"/v1beta/ragStores/{rag_store}/documents",
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
                    document_list_params.DocumentListParams,
                ),
            ),
            cast_to=DocumentListResponse,
        )

    async def delete(
        self,
        document: str,
        *,
        rag_store: str,
        api_empty: document_delete_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        force: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Deletes a `Document`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          force: Optional. If set to true, any `Chunk`s and objects related to this `Document`
              will also be deleted.

              If false (the default), a `FAILED_PRECONDITION` error will be returned if
              `Document` contains any `Chunk`s.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return await self._delete(
            f"/v1beta/ragStores/{rag_store}/documents/{document}",
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
                        "force": force,
                    },
                    document_delete_params.DocumentDeleteParams,
                ),
            ),
            cast_to=object,
        )

    async def query(
        self,
        document: str,
        *,
        rag_store: str,
        query: str,
        api_empty: document_query_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        metadata_filters: Iterable[MetadataFilterParam] | Omit = omit,
        results_count: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentQueryResponse:
        """Performs semantic search over a `Document`.

        Args:
          query: Required.

        Query string to perform semantic search.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          metadata_filters: Optional. Filter for `Chunk` metadata. Each `MetadataFilter` object should
              correspond to a unique key. Multiple `MetadataFilter` objects are joined by
              logical "AND"s.

              Note: `Document`-level filtering is not supported for this request because a
              `Document` name is already specified.

              Example query: (year >= 2020 OR year < 2010) AND (genre = drama OR genre =
              action)

              `MetadataFilter` object list: metadata_filters = [ {key =
              "chunk.custom_metadata.year" conditions = [{int_value = 2020, operation =
              GREATER_EQUAL}, {int_value = 2010, operation = LESS}}, {key =
              "chunk.custom_metadata.genre" conditions = [{string_value = "drama", operation =
              EQUAL}, {string_value = "action", operation = EQUAL}}]

              Example query for a numeric range of values: (year > 2015 AND year <= 2020)

              `MetadataFilter` object list: metadata_filters = [ {key =
              "chunk.custom_metadata.year" conditions = [{int_value = 2015, operation =
              GREATER}]}, {key = "chunk.custom_metadata.year" conditions = [{int_value = 2020,
              operation = LESS_EQUAL}]}]

              Note: "AND"s for the same key are only supported for numeric values. String
              values only support "OR"s for the same key.

          results_count: Optional. The maximum number of `Chunk`s to return. The service may return fewer
              `Chunk`s.

              If unspecified, at most 10 `Chunk`s will be returned. The maximum specified
              result count is 100.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        if not document:
            raise ValueError(f"Expected a non-empty value for `document` but received {document!r}")
        return await self._post(
            f"/v1beta/ragStores/{rag_store}/documents/{document}:query",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "metadata_filters": metadata_filters,
                    "results_count": results_count,
                },
                document_query_params.DocumentQueryParams,
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
                    document_query_params.DocumentQueryParams,
                ),
            ),
            cast_to=DocumentQueryResponse,
        )


class DocumentsResourceWithRawResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.create = to_raw_response_wrapper(
            documents.create,
        )
        self.retrieve = to_raw_response_wrapper(
            documents.retrieve,
        )
        self.list = to_raw_response_wrapper(
            documents.list,
        )
        self.delete = to_raw_response_wrapper(
            documents.delete,
        )
        self.query = to_raw_response_wrapper(
            documents.query,
        )


class AsyncDocumentsResourceWithRawResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.create = async_to_raw_response_wrapper(
            documents.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            documents.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            documents.list,
        )
        self.delete = async_to_raw_response_wrapper(
            documents.delete,
        )
        self.query = async_to_raw_response_wrapper(
            documents.query,
        )


class DocumentsResourceWithStreamingResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.create = to_streamed_response_wrapper(
            documents.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            documents.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            documents.list,
        )
        self.delete = to_streamed_response_wrapper(
            documents.delete,
        )
        self.query = to_streamed_response_wrapper(
            documents.query,
        )


class AsyncDocumentsResourceWithStreamingResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.create = async_to_streamed_response_wrapper(
            documents.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            documents.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            documents.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            documents.delete,
        )
        self.query = async_to_streamed_response_wrapper(
            documents.query,
        )
