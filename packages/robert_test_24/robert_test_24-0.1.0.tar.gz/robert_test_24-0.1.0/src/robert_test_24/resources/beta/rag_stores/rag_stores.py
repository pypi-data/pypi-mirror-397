# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from .upload import (
    UploadResource,
    AsyncUploadResource,
    UploadResourceWithRawResponse,
    AsyncUploadResourceWithRawResponse,
    UploadResourceWithStreamingResponse,
    AsyncUploadResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from .documents import (
    DocumentsResource,
    AsyncDocumentsResource,
    DocumentsResourceWithRawResponse,
    AsyncDocumentsResourceWithRawResponse,
    DocumentsResourceWithStreamingResponse,
    AsyncDocumentsResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....types.beta import (
    rag_store_list_params,
    rag_store_create_params,
    rag_store_delete_params,
    rag_store_update_params,
    rag_store_retrieve_params,
    rag_store_upload_to_rag_store_params,
    rag_store_get_operation_status_params,
)
from ...._base_client import make_request_options
from ....types.beta.operation import Operation
from ....types.beta.rag_store import RagStore
from ....types.beta.custom_metadata_param import CustomMetadataParam
from ....types.beta.rag_store_list_response import RagStoreListResponse
from ....types.beta.rag_store_upload_to_rag_store_response import RagStoreUploadToRagStoreResponse

__all__ = ["RagStoresResource", "AsyncRagStoresResource"]


class RagStoresResource(SyncAPIResource):
    @cached_property
    def documents(self) -> DocumentsResource:
        return DocumentsResource(self._client)

    @cached_property
    def upload(self) -> UploadResource:
        return UploadResource(self._client)

    @cached_property
    def with_raw_response(self) -> RagStoresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return RagStoresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RagStoresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return RagStoresResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        api_empty: rag_store_create_params.api_empty | Omit = omit,
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
    ) -> RagStore:
        """
        Creates an empty `RagStore`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          display_name: Optional. The human-readable display name for the `RagStore`. The display name
              must be no more than 512 characters in length, including spaces. Example: "Docs
              on Semantic Retriever"

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1beta/ragStores",
            body=maybe_transform({"display_name": display_name}, rag_store_create_params.RagStoreCreateParams),
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
                    rag_store_create_params.RagStoreCreateParams,
                ),
            ),
            cast_to=RagStore,
        )

    def retrieve(
        self,
        rag_store: str,
        *,
        api_empty: rag_store_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RagStore:
        """
        Gets information about a specific `RagStore`.

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
        return self._get(
            f"/v1beta/ragStores/{rag_store}",
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
                    rag_store_retrieve_params.RagStoreRetrieveParams,
                ),
            ),
            cast_to=RagStore,
        )

    def update(
        self,
        rag_store: str,
        *,
        update_mask: str,
        api_empty: rag_store_update_params.api_empty | Omit = omit,
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
    ) -> RagStore:
        """Updates a `RagStore`.

        Args:
          update_mask: Required.

        The list of fields to update. Currently, this only supports updating
              `display_name`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          display_name: Optional. The human-readable display name for the `RagStore`. The display name
              must be no more than 512 characters in length, including spaces. Example: "Docs
              on Semantic Retriever"

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        return self._patch(
            f"/v1beta/ragStores/{rag_store}",
            body=maybe_transform({"display_name": display_name}, rag_store_update_params.RagStoreUpdateParams),
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
                    rag_store_update_params.RagStoreUpdateParams,
                ),
            ),
            cast_to=RagStore,
        )

    def list(
        self,
        *,
        api_empty: rag_store_list_params.api_empty | Omit = omit,
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
    ) -> RagStoreListResponse:
        """
        Lists all `RagStores` owned by the user.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of `RagStores` to return (per page). The service
              may return fewer `RagStores`.

              If unspecified, at most 10 `RagStores` will be returned. The maximum size limit
              is 20 `RagStores` per page.

          page_token: Optional. A page token, received from a previous `ListRagStores` call.

              Provide the `next_page_token` returned in the response as an argument to the
              next request to retrieve the next page.

              When paginating, all other parameters provided to `ListRagStores` must match the
              call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1beta/ragStores",
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
                    rag_store_list_params.RagStoreListParams,
                ),
            ),
            cast_to=RagStoreListResponse,
        )

    def delete(
        self,
        rag_store: str,
        *,
        api_empty: rag_store_delete_params.api_empty | Omit = omit,
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
        Deletes a `RagStore`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          force: Optional. If set to true, any `Document`s and objects related to this `RagStore`
              will also be deleted.

              If false (the default), a `FAILED_PRECONDITION` error will be returned if
              `RagStore` contains any `Document`s.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        return self._delete(
            f"/v1beta/ragStores/{rag_store}",
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
                    rag_store_delete_params.RagStoreDeleteParams,
                ),
            ),
            cast_to=object,
        )

    def get_operation_status(
        self,
        operation: str,
        *,
        rag_store: str,
        api_empty: rag_store_get_operation_status_params.api_empty | Omit = omit,
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
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        if not operation:
            raise ValueError(f"Expected a non-empty value for `operation` but received {operation!r}")
        return self._get(
            f"/v1beta/ragStores/{rag_store}/operations/{operation}",
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
                    rag_store_get_operation_status_params.RagStoreGetOperationStatusParams,
                ),
            ),
            cast_to=Operation,
        )

    def upload_to_rag_store(
        self,
        rag_store: str,
        *,
        api_empty: rag_store_upload_to_rag_store_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        chunking_config: rag_store_upload_to_rag_store_params.ChunkingConfig | Omit = omit,
        custom_metadata: Iterable[CustomMetadataParam] | Omit = omit,
        display_name: str | Omit = omit,
        mime_type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RagStoreUploadToRagStoreResponse:
        """
        Uploads data to a ragStore, preprocesses and chunks before storing it in a
        RagStore Document.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          chunking_config: Parameters for telling the service how to chunk the file. inspired by
              google3/cloud/ai/platform/extension/lib/retrieval/config/chunker_config.proto

          custom_metadata: Custom metadata to be associated with the data.

          display_name: Optional. Display name of the created document.

          mime_type: Optional. MIME type of the data. If not provided, it will be inferred from the
              uploaded content.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        return self._post(
            f"/v1beta/ragStores/{rag_store}:uploadToRagStore",
            body=maybe_transform(
                {
                    "chunking_config": chunking_config,
                    "custom_metadata": custom_metadata,
                    "display_name": display_name,
                    "mime_type": mime_type,
                },
                rag_store_upload_to_rag_store_params.RagStoreUploadToRagStoreParams,
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
                    rag_store_upload_to_rag_store_params.RagStoreUploadToRagStoreParams,
                ),
            ),
            cast_to=RagStoreUploadToRagStoreResponse,
        )


class AsyncRagStoresResource(AsyncAPIResource):
    @cached_property
    def documents(self) -> AsyncDocumentsResource:
        return AsyncDocumentsResource(self._client)

    @cached_property
    def upload(self) -> AsyncUploadResource:
        return AsyncUploadResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRagStoresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRagStoresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRagStoresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncRagStoresResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        api_empty: rag_store_create_params.api_empty | Omit = omit,
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
    ) -> RagStore:
        """
        Creates an empty `RagStore`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          display_name: Optional. The human-readable display name for the `RagStore`. The display name
              must be no more than 512 characters in length, including spaces. Example: "Docs
              on Semantic Retriever"

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1beta/ragStores",
            body=await async_maybe_transform(
                {"display_name": display_name}, rag_store_create_params.RagStoreCreateParams
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
                    rag_store_create_params.RagStoreCreateParams,
                ),
            ),
            cast_to=RagStore,
        )

    async def retrieve(
        self,
        rag_store: str,
        *,
        api_empty: rag_store_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RagStore:
        """
        Gets information about a specific `RagStore`.

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
        return await self._get(
            f"/v1beta/ragStores/{rag_store}",
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
                    rag_store_retrieve_params.RagStoreRetrieveParams,
                ),
            ),
            cast_to=RagStore,
        )

    async def update(
        self,
        rag_store: str,
        *,
        update_mask: str,
        api_empty: rag_store_update_params.api_empty | Omit = omit,
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
    ) -> RagStore:
        """Updates a `RagStore`.

        Args:
          update_mask: Required.

        The list of fields to update. Currently, this only supports updating
              `display_name`.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          display_name: Optional. The human-readable display name for the `RagStore`. The display name
              must be no more than 512 characters in length, including spaces. Example: "Docs
              on Semantic Retriever"

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        return await self._patch(
            f"/v1beta/ragStores/{rag_store}",
            body=await async_maybe_transform(
                {"display_name": display_name}, rag_store_update_params.RagStoreUpdateParams
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
                    rag_store_update_params.RagStoreUpdateParams,
                ),
            ),
            cast_to=RagStore,
        )

    async def list(
        self,
        *,
        api_empty: rag_store_list_params.api_empty | Omit = omit,
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
    ) -> RagStoreListResponse:
        """
        Lists all `RagStores` owned by the user.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of `RagStores` to return (per page). The service
              may return fewer `RagStores`.

              If unspecified, at most 10 `RagStores` will be returned. The maximum size limit
              is 20 `RagStores` per page.

          page_token: Optional. A page token, received from a previous `ListRagStores` call.

              Provide the `next_page_token` returned in the response as an argument to the
              next request to retrieve the next page.

              When paginating, all other parameters provided to `ListRagStores` must match the
              call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1beta/ragStores",
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
                    rag_store_list_params.RagStoreListParams,
                ),
            ),
            cast_to=RagStoreListResponse,
        )

    async def delete(
        self,
        rag_store: str,
        *,
        api_empty: rag_store_delete_params.api_empty | Omit = omit,
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
        Deletes a `RagStore`.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          force: Optional. If set to true, any `Document`s and objects related to this `RagStore`
              will also be deleted.

              If false (the default), a `FAILED_PRECONDITION` error will be returned if
              `RagStore` contains any `Document`s.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        return await self._delete(
            f"/v1beta/ragStores/{rag_store}",
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
                    rag_store_delete_params.RagStoreDeleteParams,
                ),
            ),
            cast_to=object,
        )

    async def get_operation_status(
        self,
        operation: str,
        *,
        rag_store: str,
        api_empty: rag_store_get_operation_status_params.api_empty | Omit = omit,
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
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        if not operation:
            raise ValueError(f"Expected a non-empty value for `operation` but received {operation!r}")
        return await self._get(
            f"/v1beta/ragStores/{rag_store}/operations/{operation}",
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
                    rag_store_get_operation_status_params.RagStoreGetOperationStatusParams,
                ),
            ),
            cast_to=Operation,
        )

    async def upload_to_rag_store(
        self,
        rag_store: str,
        *,
        api_empty: rag_store_upload_to_rag_store_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        chunking_config: rag_store_upload_to_rag_store_params.ChunkingConfig | Omit = omit,
        custom_metadata: Iterable[CustomMetadataParam] | Omit = omit,
        display_name: str | Omit = omit,
        mime_type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RagStoreUploadToRagStoreResponse:
        """
        Uploads data to a ragStore, preprocesses and chunks before storing it in a
        RagStore Document.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          chunking_config: Parameters for telling the service how to chunk the file. inspired by
              google3/cloud/ai/platform/extension/lib/retrieval/config/chunker_config.proto

          custom_metadata: Custom metadata to be associated with the data.

          display_name: Optional. Display name of the created document.

          mime_type: Optional. MIME type of the data. If not provided, it will be inferred from the
              uploaded content.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not rag_store:
            raise ValueError(f"Expected a non-empty value for `rag_store` but received {rag_store!r}")
        return await self._post(
            f"/v1beta/ragStores/{rag_store}:uploadToRagStore",
            body=await async_maybe_transform(
                {
                    "chunking_config": chunking_config,
                    "custom_metadata": custom_metadata,
                    "display_name": display_name,
                    "mime_type": mime_type,
                },
                rag_store_upload_to_rag_store_params.RagStoreUploadToRagStoreParams,
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
                    rag_store_upload_to_rag_store_params.RagStoreUploadToRagStoreParams,
                ),
            ),
            cast_to=RagStoreUploadToRagStoreResponse,
        )


class RagStoresResourceWithRawResponse:
    def __init__(self, rag_stores: RagStoresResource) -> None:
        self._rag_stores = rag_stores

        self.create = to_raw_response_wrapper(
            rag_stores.create,
        )
        self.retrieve = to_raw_response_wrapper(
            rag_stores.retrieve,
        )
        self.update = to_raw_response_wrapper(
            rag_stores.update,
        )
        self.list = to_raw_response_wrapper(
            rag_stores.list,
        )
        self.delete = to_raw_response_wrapper(
            rag_stores.delete,
        )
        self.get_operation_status = to_raw_response_wrapper(
            rag_stores.get_operation_status,
        )
        self.upload_to_rag_store = to_raw_response_wrapper(
            rag_stores.upload_to_rag_store,
        )

    @cached_property
    def documents(self) -> DocumentsResourceWithRawResponse:
        return DocumentsResourceWithRawResponse(self._rag_stores.documents)

    @cached_property
    def upload(self) -> UploadResourceWithRawResponse:
        return UploadResourceWithRawResponse(self._rag_stores.upload)


class AsyncRagStoresResourceWithRawResponse:
    def __init__(self, rag_stores: AsyncRagStoresResource) -> None:
        self._rag_stores = rag_stores

        self.create = async_to_raw_response_wrapper(
            rag_stores.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            rag_stores.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            rag_stores.update,
        )
        self.list = async_to_raw_response_wrapper(
            rag_stores.list,
        )
        self.delete = async_to_raw_response_wrapper(
            rag_stores.delete,
        )
        self.get_operation_status = async_to_raw_response_wrapper(
            rag_stores.get_operation_status,
        )
        self.upload_to_rag_store = async_to_raw_response_wrapper(
            rag_stores.upload_to_rag_store,
        )

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithRawResponse:
        return AsyncDocumentsResourceWithRawResponse(self._rag_stores.documents)

    @cached_property
    def upload(self) -> AsyncUploadResourceWithRawResponse:
        return AsyncUploadResourceWithRawResponse(self._rag_stores.upload)


class RagStoresResourceWithStreamingResponse:
    def __init__(self, rag_stores: RagStoresResource) -> None:
        self._rag_stores = rag_stores

        self.create = to_streamed_response_wrapper(
            rag_stores.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            rag_stores.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            rag_stores.update,
        )
        self.list = to_streamed_response_wrapper(
            rag_stores.list,
        )
        self.delete = to_streamed_response_wrapper(
            rag_stores.delete,
        )
        self.get_operation_status = to_streamed_response_wrapper(
            rag_stores.get_operation_status,
        )
        self.upload_to_rag_store = to_streamed_response_wrapper(
            rag_stores.upload_to_rag_store,
        )

    @cached_property
    def documents(self) -> DocumentsResourceWithStreamingResponse:
        return DocumentsResourceWithStreamingResponse(self._rag_stores.documents)

    @cached_property
    def upload(self) -> UploadResourceWithStreamingResponse:
        return UploadResourceWithStreamingResponse(self._rag_stores.upload)


class AsyncRagStoresResourceWithStreamingResponse:
    def __init__(self, rag_stores: AsyncRagStoresResource) -> None:
        self._rag_stores = rag_stores

        self.create = async_to_streamed_response_wrapper(
            rag_stores.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            rag_stores.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            rag_stores.update,
        )
        self.list = async_to_streamed_response_wrapper(
            rag_stores.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            rag_stores.delete,
        )
        self.get_operation_status = async_to_streamed_response_wrapper(
            rag_stores.get_operation_status,
        )
        self.upload_to_rag_store = async_to_streamed_response_wrapper(
            rag_stores.upload_to_rag_store,
        )

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithStreamingResponse:
        return AsyncDocumentsResourceWithStreamingResponse(self._rag_stores.documents)

    @cached_property
    def upload(self) -> AsyncUploadResourceWithStreamingResponse:
        return AsyncUploadResourceWithStreamingResponse(self._rag_stores.upload)
