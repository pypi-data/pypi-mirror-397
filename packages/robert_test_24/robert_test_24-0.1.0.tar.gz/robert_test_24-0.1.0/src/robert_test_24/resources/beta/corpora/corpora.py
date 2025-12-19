# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
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
    corpora_list_params,
    corpora_create_params,
    corpora_delete_params,
    corpora_update_params,
    corpora_retrieve_params,
    corpora_corpus_query_params,
)
from ...._base_client import make_request_options
from .documents.documents import (
    DocumentsResource,
    AsyncDocumentsResource,
    DocumentsResourceWithRawResponse,
    AsyncDocumentsResourceWithRawResponse,
    DocumentsResourceWithStreamingResponse,
    AsyncDocumentsResourceWithStreamingResponse,
)
from ....types.beta.corpus import Corpus
from ....types.beta.operation import Operation
from ....types.beta.corpora_list_response import CorporaListResponse
from ....types.beta.metadata_filter_param import MetadataFilterParam
from ....types.beta.corpora_corpus_query_response import CorporaCorpusQueryResponse

__all__ = ["CorporaResource", "AsyncCorporaResource"]


class CorporaResource(SyncAPIResource):
    @cached_property
    def permissions(self) -> PermissionsResource:
        return PermissionsResource(self._client)

    @cached_property
    def documents(self) -> DocumentsResource:
        return DocumentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> CorporaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return CorporaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CorporaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return CorporaResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        api_empty: corpora_create_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        display_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Corpus:
        """
        Creates an empty `Corpus`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          display_name: Optional. The human-readable display name for the `Corpus`. The display name
              must be no more than 512 characters in length, including spaces. Example: "Docs
              on Semantic Retriever"

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1beta/corpora",
            body=maybe_transform({"display_name": display_name}, corpora_create_params.CorporaCreateParams),
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
                    corpora_create_params.CorporaCreateParams,
                ),
            ),
            cast_to=Corpus,
        )

    def retrieve(
        self,
        operation: str,
        *,
        corpus: str,
        api_empty: corpora_retrieve_params.api_empty | Omit = omit,
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
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not operation:
            raise ValueError(f"Expected a non-empty value for `operation` but received {operation!r}")
        return self._get(
            f"/v1beta/corpora/{corpus}/operations/{operation}",
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
                    corpora_retrieve_params.CorporaRetrieveParams,
                ),
            ),
            cast_to=Operation,
        )

    def update(
        self,
        corpus: str,
        *,
        update_mask: str,
        api_empty: corpora_update_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        display_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Corpus:
        """Updates a `Corpus`.

        Args:
          update_mask: Required.

        The list of fields to update. Currently, this only supports updating
              `display_name`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          display_name: Optional. The human-readable display name for the `Corpus`. The display name
              must be no more than 512 characters in length, including spaces. Example: "Docs
              on Semantic Retriever"

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        return self._patch(
            f"/v1beta/corpora/{corpus}",
            body=maybe_transform({"display_name": display_name}, corpora_update_params.CorporaUpdateParams),
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
                    corpora_update_params.CorporaUpdateParams,
                ),
            ),
            cast_to=Corpus,
        )

    def list(
        self,
        *,
        api_empty: corpora_list_params.api_empty | Omit = omit,
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
    ) -> CorporaListResponse:
        """
        Lists all `Corpora` owned by the user.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of `Corpora` to return (per page). The service may
              return fewer `Corpora`.

              If unspecified, at most 10 `Corpora` will be returned. The maximum size limit is
              20 `Corpora` per page.

          page_token: Optional. A page token, received from a previous `ListCorpora` call.

              Provide the `next_page_token` returned in the response as an argument to the
              next request to retrieve the next page.

              When paginating, all other parameters provided to `ListCorpora` must match the
              call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1beta/corpora",
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
                    corpora_list_params.CorporaListParams,
                ),
            ),
            cast_to=CorporaListResponse,
        )

    def delete(
        self,
        corpus: str,
        *,
        api_empty: corpora_delete_params.api_empty | Omit = omit,
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
        Deletes a `Corpus`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          force: Optional. If set to true, any `Document`s and objects related to this `Corpus`
              will also be deleted.

              If false (the default), a `FAILED_PRECONDITION` error will be returned if
              `Corpus` contains any `Document`s.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        return self._delete(
            f"/v1beta/corpora/{corpus}",
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
                    corpora_delete_params.CorporaDeleteParams,
                ),
            ),
            cast_to=object,
        )

    def corpus_query(
        self,
        corpus: str,
        *,
        query: str,
        api_empty: corpora_corpus_query_params.api_empty | Omit = omit,
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
    ) -> CorporaCorpusQueryResponse:
        """Performs semantic search over a `Corpus`.

        Args:
          query: Required.

        Query string to perform semantic search.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          metadata_filters: Optional. Filter for `Chunk` and `Document` metadata. Each `MetadataFilter`
              object should correspond to a unique key. Multiple `MetadataFilter` objects are
              joined by logical "AND"s.

              Example query at document level: (year >= 2020 OR year < 2010) AND (genre =
              drama OR genre = action)

              `MetadataFilter` object list: metadata_filters = [ {key =
              "document.custom_metadata.year" conditions = [{int_value = 2020, operation =
              GREATER_EQUAL}, {int_value = 2010, operation = LESS}]}, {key =
              "document.custom_metadata.year" conditions = [{int_value = 2020, operation =
              GREATER_EQUAL}, {int_value = 2010, operation = LESS}]}, {key =
              "document.custom_metadata.genre" conditions = [{string_value = "drama",
              operation = EQUAL}, {string_value = "action", operation = EQUAL}]}]

              Example query at chunk level for a numeric range of values: (year > 2015 AND
              year <= 2020)

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
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        return self._post(
            f"/v1beta/corpora/{corpus}:query",
            body=maybe_transform(
                {
                    "query": query,
                    "metadata_filters": metadata_filters,
                    "results_count": results_count,
                },
                corpora_corpus_query_params.CorporaCorpusQueryParams,
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
                    corpora_corpus_query_params.CorporaCorpusQueryParams,
                ),
            ),
            cast_to=CorporaCorpusQueryResponse,
        )


class AsyncCorporaResource(AsyncAPIResource):
    @cached_property
    def permissions(self) -> AsyncPermissionsResource:
        return AsyncPermissionsResource(self._client)

    @cached_property
    def documents(self) -> AsyncDocumentsResource:
        return AsyncDocumentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCorporaResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCorporaResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCorporaResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncCorporaResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        api_empty: corpora_create_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        display_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Corpus:
        """
        Creates an empty `Corpus`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          display_name: Optional. The human-readable display name for the `Corpus`. The display name
              must be no more than 512 characters in length, including spaces. Example: "Docs
              on Semantic Retriever"

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1beta/corpora",
            body=await async_maybe_transform({"display_name": display_name}, corpora_create_params.CorporaCreateParams),
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
                    corpora_create_params.CorporaCreateParams,
                ),
            ),
            cast_to=Corpus,
        )

    async def retrieve(
        self,
        operation: str,
        *,
        corpus: str,
        api_empty: corpora_retrieve_params.api_empty | Omit = omit,
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
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        if not operation:
            raise ValueError(f"Expected a non-empty value for `operation` but received {operation!r}")
        return await self._get(
            f"/v1beta/corpora/{corpus}/operations/{operation}",
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
                    corpora_retrieve_params.CorporaRetrieveParams,
                ),
            ),
            cast_to=Operation,
        )

    async def update(
        self,
        corpus: str,
        *,
        update_mask: str,
        api_empty: corpora_update_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        display_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Corpus:
        """Updates a `Corpus`.

        Args:
          update_mask: Required.

        The list of fields to update. Currently, this only supports updating
              `display_name`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          display_name: Optional. The human-readable display name for the `Corpus`. The display name
              must be no more than 512 characters in length, including spaces. Example: "Docs
              on Semantic Retriever"

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        return await self._patch(
            f"/v1beta/corpora/{corpus}",
            body=await async_maybe_transform({"display_name": display_name}, corpora_update_params.CorporaUpdateParams),
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
                    corpora_update_params.CorporaUpdateParams,
                ),
            ),
            cast_to=Corpus,
        )

    async def list(
        self,
        *,
        api_empty: corpora_list_params.api_empty | Omit = omit,
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
    ) -> CorporaListResponse:
        """
        Lists all `Corpora` owned by the user.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of `Corpora` to return (per page). The service may
              return fewer `Corpora`.

              If unspecified, at most 10 `Corpora` will be returned. The maximum size limit is
              20 `Corpora` per page.

          page_token: Optional. A page token, received from a previous `ListCorpora` call.

              Provide the `next_page_token` returned in the response as an argument to the
              next request to retrieve the next page.

              When paginating, all other parameters provided to `ListCorpora` must match the
              call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1beta/corpora",
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
                    corpora_list_params.CorporaListParams,
                ),
            ),
            cast_to=CorporaListResponse,
        )

    async def delete(
        self,
        corpus: str,
        *,
        api_empty: corpora_delete_params.api_empty | Omit = omit,
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
        Deletes a `Corpus`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          force: Optional. If set to true, any `Document`s and objects related to this `Corpus`
              will also be deleted.

              If false (the default), a `FAILED_PRECONDITION` error will be returned if
              `Corpus` contains any `Document`s.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        return await self._delete(
            f"/v1beta/corpora/{corpus}",
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
                    corpora_delete_params.CorporaDeleteParams,
                ),
            ),
            cast_to=object,
        )

    async def corpus_query(
        self,
        corpus: str,
        *,
        query: str,
        api_empty: corpora_corpus_query_params.api_empty | Omit = omit,
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
    ) -> CorporaCorpusQueryResponse:
        """Performs semantic search over a `Corpus`.

        Args:
          query: Required.

        Query string to perform semantic search.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          metadata_filters: Optional. Filter for `Chunk` and `Document` metadata. Each `MetadataFilter`
              object should correspond to a unique key. Multiple `MetadataFilter` objects are
              joined by logical "AND"s.

              Example query at document level: (year >= 2020 OR year < 2010) AND (genre =
              drama OR genre = action)

              `MetadataFilter` object list: metadata_filters = [ {key =
              "document.custom_metadata.year" conditions = [{int_value = 2020, operation =
              GREATER_EQUAL}, {int_value = 2010, operation = LESS}]}, {key =
              "document.custom_metadata.year" conditions = [{int_value = 2020, operation =
              GREATER_EQUAL}, {int_value = 2010, operation = LESS}]}, {key =
              "document.custom_metadata.genre" conditions = [{string_value = "drama",
              operation = EQUAL}, {string_value = "action", operation = EQUAL}]}]

              Example query at chunk level for a numeric range of values: (year > 2015 AND
              year <= 2020)

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
        if not corpus:
            raise ValueError(f"Expected a non-empty value for `corpus` but received {corpus!r}")
        return await self._post(
            f"/v1beta/corpora/{corpus}:query",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "metadata_filters": metadata_filters,
                    "results_count": results_count,
                },
                corpora_corpus_query_params.CorporaCorpusQueryParams,
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
                    corpora_corpus_query_params.CorporaCorpusQueryParams,
                ),
            ),
            cast_to=CorporaCorpusQueryResponse,
        )


class CorporaResourceWithRawResponse:
    def __init__(self, corpora: CorporaResource) -> None:
        self._corpora = corpora

        self.create = to_raw_response_wrapper(
            corpora.create,
        )
        self.retrieve = to_raw_response_wrapper(
            corpora.retrieve,
        )
        self.update = to_raw_response_wrapper(
            corpora.update,
        )
        self.list = to_raw_response_wrapper(
            corpora.list,
        )
        self.delete = to_raw_response_wrapper(
            corpora.delete,
        )
        self.corpus_query = to_raw_response_wrapper(
            corpora.corpus_query,
        )

    @cached_property
    def permissions(self) -> PermissionsResourceWithRawResponse:
        return PermissionsResourceWithRawResponse(self._corpora.permissions)

    @cached_property
    def documents(self) -> DocumentsResourceWithRawResponse:
        return DocumentsResourceWithRawResponse(self._corpora.documents)


class AsyncCorporaResourceWithRawResponse:
    def __init__(self, corpora: AsyncCorporaResource) -> None:
        self._corpora = corpora

        self.create = async_to_raw_response_wrapper(
            corpora.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            corpora.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            corpora.update,
        )
        self.list = async_to_raw_response_wrapper(
            corpora.list,
        )
        self.delete = async_to_raw_response_wrapper(
            corpora.delete,
        )
        self.corpus_query = async_to_raw_response_wrapper(
            corpora.corpus_query,
        )

    @cached_property
    def permissions(self) -> AsyncPermissionsResourceWithRawResponse:
        return AsyncPermissionsResourceWithRawResponse(self._corpora.permissions)

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithRawResponse:
        return AsyncDocumentsResourceWithRawResponse(self._corpora.documents)


class CorporaResourceWithStreamingResponse:
    def __init__(self, corpora: CorporaResource) -> None:
        self._corpora = corpora

        self.create = to_streamed_response_wrapper(
            corpora.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            corpora.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            corpora.update,
        )
        self.list = to_streamed_response_wrapper(
            corpora.list,
        )
        self.delete = to_streamed_response_wrapper(
            corpora.delete,
        )
        self.corpus_query = to_streamed_response_wrapper(
            corpora.corpus_query,
        )

    @cached_property
    def permissions(self) -> PermissionsResourceWithStreamingResponse:
        return PermissionsResourceWithStreamingResponse(self._corpora.permissions)

    @cached_property
    def documents(self) -> DocumentsResourceWithStreamingResponse:
        return DocumentsResourceWithStreamingResponse(self._corpora.documents)


class AsyncCorporaResourceWithStreamingResponse:
    def __init__(self, corpora: AsyncCorporaResource) -> None:
        self._corpora = corpora

        self.create = async_to_streamed_response_wrapper(
            corpora.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            corpora.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            corpora.update,
        )
        self.list = async_to_streamed_response_wrapper(
            corpora.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            corpora.delete,
        )
        self.corpus_query = async_to_streamed_response_wrapper(
            corpora.corpus_query,
        )

    @cached_property
    def permissions(self) -> AsyncPermissionsResourceWithStreamingResponse:
        return AsyncPermissionsResourceWithStreamingResponse(self._corpora.permissions)

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithStreamingResponse:
        return AsyncDocumentsResourceWithStreamingResponse(self._corpora.documents)
