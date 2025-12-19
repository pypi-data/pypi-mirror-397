# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
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
    cached_content_list_params,
    cached_content_create_params,
    cached_content_delete_params,
    cached_content_update_params,
    cached_content_retrieve_params,
)
from ..._base_client import make_request_options
from ...types.beta.tool_param import ToolParam
from ...types.beta.content_param import ContentParam
from ...types.beta.cached_content import CachedContent
from ...types.beta.tool_config_param import ToolConfigParam
from ...types.beta.cached_content_list_response import CachedContentListResponse

__all__ = ["CachedContentsResource", "AsyncCachedContentsResource"]


class CachedContentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CachedContentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return CachedContentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CachedContentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return CachedContentsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        model: str,
        api_empty: cached_content_create_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        contents: Iterable[ContentParam] | Omit = omit,
        display_name: str | Omit = omit,
        expire_time: Union[str, datetime] | Omit = omit,
        system_instruction: ContentParam | Omit = omit,
        tool_config: ToolConfigParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        ttl: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CachedContent:
        """Creates CachedContent resource.

        Args:
          model:
              Required.

        Immutable. The name of the `Model` to use for cached content Format:
              `models/{model}`

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          contents: Optional. Input only. Immutable. The content to cache.

          display_name: Optional. Immutable. The user-generated meaningful display name of the cached
              content. Maximum 128 Unicode characters.

          expire_time: Timestamp in UTC of when this resource is considered expired. This is _always_
              provided on output, regardless of what was sent on input.

          system_instruction: The base structured datatype containing multi-part content of a message.

              A `Content` includes a `role` field designating the producer of the `Content`
              and a `parts` field containing multi-part data that contains the content of the
              message turn.

          tool_config: The Tool configuration containing parameters for specifying `Tool` use in the
              request.

          tools: Optional. Input only. Immutable. A list of `Tools` the model may use to generate
              the next response

          ttl: Input only. New TTL for this resource, input only.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1beta/cachedContents",
            body=maybe_transform(
                {
                    "model": model,
                    "contents": contents,
                    "display_name": display_name,
                    "expire_time": expire_time,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                    "ttl": ttl,
                },
                cached_content_create_params.CachedContentCreateParams,
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
                    cached_content_create_params.CachedContentCreateParams,
                ),
            ),
            cast_to=CachedContent,
        )

    def retrieve(
        self,
        id: str,
        *,
        api_empty: cached_content_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CachedContent:
        """
        Reads CachedContent resource.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v1beta/cachedContents/{id}",
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
                    cached_content_retrieve_params.CachedContentRetrieveParams,
                ),
            ),
            cast_to=CachedContent,
        )

    def update(
        self,
        id: str,
        *,
        model: str,
        api_empty: cached_content_update_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        update_mask: str | Omit = omit,
        contents: Iterable[ContentParam] | Omit = omit,
        display_name: str | Omit = omit,
        expire_time: Union[str, datetime] | Omit = omit,
        system_instruction: ContentParam | Omit = omit,
        tool_config: ToolConfigParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        ttl: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CachedContent:
        """
        Updates CachedContent resource (only expiration is updatable).

        Args:
          model:
              Required. Immutable. The name of the `Model` to use for cached content Format:
              `models/{model}`

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          update_mask: The list of fields to update.

          contents: Optional. Input only. Immutable. The content to cache.

          display_name: Optional. Immutable. The user-generated meaningful display name of the cached
              content. Maximum 128 Unicode characters.

          expire_time: Timestamp in UTC of when this resource is considered expired. This is _always_
              provided on output, regardless of what was sent on input.

          system_instruction: The base structured datatype containing multi-part content of a message.

              A `Content` includes a `role` field designating the producer of the `Content`
              and a `parts` field containing multi-part data that contains the content of the
              message turn.

          tool_config: The Tool configuration containing parameters for specifying `Tool` use in the
              request.

          tools: Optional. Input only. Immutable. A list of `Tools` the model may use to generate
              the next response

          ttl: Input only. New TTL for this resource, input only.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/v1beta/cachedContents/{id}",
            body=maybe_transform(
                {
                    "model": model,
                    "contents": contents,
                    "display_name": display_name,
                    "expire_time": expire_time,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                    "ttl": ttl,
                },
                cached_content_update_params.CachedContentUpdateParams,
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
                    cached_content_update_params.CachedContentUpdateParams,
                ),
            ),
            cast_to=CachedContent,
        )

    def list(
        self,
        *,
        api_empty: cached_content_list_params.api_empty | Omit = omit,
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
    ) -> CachedContentListResponse:
        """
        Lists CachedContents.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of cached contents to return. The service may
              return fewer than this value. If unspecified, some default (under maximum)
              number of items will be returned. The maximum value is 1000; values above 1000
              will be coerced to 1000.

          page_token: Optional. A page token, received from a previous `ListCachedContents` call.
              Provide this to retrieve the subsequent page.

              When paginating, all other parameters provided to `ListCachedContents` must
              match the call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1beta/cachedContents",
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
                    cached_content_list_params.CachedContentListParams,
                ),
            ),
            cast_to=CachedContentListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        api_empty: cached_content_delete_params.api_empty | Omit = omit,
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
        Deletes CachedContent resource.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/v1beta/cachedContents/{id}",
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
                    cached_content_delete_params.CachedContentDeleteParams,
                ),
            ),
            cast_to=object,
        )


class AsyncCachedContentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCachedContentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCachedContentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCachedContentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncCachedContentsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        model: str,
        api_empty: cached_content_create_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        contents: Iterable[ContentParam] | Omit = omit,
        display_name: str | Omit = omit,
        expire_time: Union[str, datetime] | Omit = omit,
        system_instruction: ContentParam | Omit = omit,
        tool_config: ToolConfigParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        ttl: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CachedContent:
        """Creates CachedContent resource.

        Args:
          model:
              Required.

        Immutable. The name of the `Model` to use for cached content Format:
              `models/{model}`

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          contents: Optional. Input only. Immutable. The content to cache.

          display_name: Optional. Immutable. The user-generated meaningful display name of the cached
              content. Maximum 128 Unicode characters.

          expire_time: Timestamp in UTC of when this resource is considered expired. This is _always_
              provided on output, regardless of what was sent on input.

          system_instruction: The base structured datatype containing multi-part content of a message.

              A `Content` includes a `role` field designating the producer of the `Content`
              and a `parts` field containing multi-part data that contains the content of the
              message turn.

          tool_config: The Tool configuration containing parameters for specifying `Tool` use in the
              request.

          tools: Optional. Input only. Immutable. A list of `Tools` the model may use to generate
              the next response

          ttl: Input only. New TTL for this resource, input only.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1beta/cachedContents",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "contents": contents,
                    "display_name": display_name,
                    "expire_time": expire_time,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                    "ttl": ttl,
                },
                cached_content_create_params.CachedContentCreateParams,
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
                    cached_content_create_params.CachedContentCreateParams,
                ),
            ),
            cast_to=CachedContent,
        )

    async def retrieve(
        self,
        id: str,
        *,
        api_empty: cached_content_retrieve_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CachedContent:
        """
        Reads CachedContent resource.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v1beta/cachedContents/{id}",
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
                    cached_content_retrieve_params.CachedContentRetrieveParams,
                ),
            ),
            cast_to=CachedContent,
        )

    async def update(
        self,
        id: str,
        *,
        model: str,
        api_empty: cached_content_update_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        update_mask: str | Omit = omit,
        contents: Iterable[ContentParam] | Omit = omit,
        display_name: str | Omit = omit,
        expire_time: Union[str, datetime] | Omit = omit,
        system_instruction: ContentParam | Omit = omit,
        tool_config: ToolConfigParam | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        ttl: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CachedContent:
        """
        Updates CachedContent resource (only expiration is updatable).

        Args:
          model:
              Required. Immutable. The name of the `Model` to use for cached content Format:
              `models/{model}`

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          update_mask: The list of fields to update.

          contents: Optional. Input only. Immutable. The content to cache.

          display_name: Optional. Immutable. The user-generated meaningful display name of the cached
              content. Maximum 128 Unicode characters.

          expire_time: Timestamp in UTC of when this resource is considered expired. This is _always_
              provided on output, regardless of what was sent on input.

          system_instruction: The base structured datatype containing multi-part content of a message.

              A `Content` includes a `role` field designating the producer of the `Content`
              and a `parts` field containing multi-part data that contains the content of the
              message turn.

          tool_config: The Tool configuration containing parameters for specifying `Tool` use in the
              request.

          tools: Optional. Input only. Immutable. A list of `Tools` the model may use to generate
              the next response

          ttl: Input only. New TTL for this resource, input only.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/v1beta/cachedContents/{id}",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "contents": contents,
                    "display_name": display_name,
                    "expire_time": expire_time,
                    "system_instruction": system_instruction,
                    "tool_config": tool_config,
                    "tools": tools,
                    "ttl": ttl,
                },
                cached_content_update_params.CachedContentUpdateParams,
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
                    cached_content_update_params.CachedContentUpdateParams,
                ),
            ),
            cast_to=CachedContent,
        )

    async def list(
        self,
        *,
        api_empty: cached_content_list_params.api_empty | Omit = omit,
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
    ) -> CachedContentListResponse:
        """
        Lists CachedContents.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of cached contents to return. The service may
              return fewer than this value. If unspecified, some default (under maximum)
              number of items will be returned. The maximum value is 1000; values above 1000
              will be coerced to 1000.

          page_token: Optional. A page token, received from a previous `ListCachedContents` call.
              Provide this to retrieve the subsequent page.

              When paginating, all other parameters provided to `ListCachedContents` must
              match the call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1beta/cachedContents",
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
                    cached_content_list_params.CachedContentListParams,
                ),
            ),
            cast_to=CachedContentListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        api_empty: cached_content_delete_params.api_empty | Omit = omit,
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
        Deletes CachedContent resource.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/v1beta/cachedContents/{id}",
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
                    cached_content_delete_params.CachedContentDeleteParams,
                ),
            ),
            cast_to=object,
        )


class CachedContentsResourceWithRawResponse:
    def __init__(self, cached_contents: CachedContentsResource) -> None:
        self._cached_contents = cached_contents

        self.create = to_raw_response_wrapper(
            cached_contents.create,
        )
        self.retrieve = to_raw_response_wrapper(
            cached_contents.retrieve,
        )
        self.update = to_raw_response_wrapper(
            cached_contents.update,
        )
        self.list = to_raw_response_wrapper(
            cached_contents.list,
        )
        self.delete = to_raw_response_wrapper(
            cached_contents.delete,
        )


class AsyncCachedContentsResourceWithRawResponse:
    def __init__(self, cached_contents: AsyncCachedContentsResource) -> None:
        self._cached_contents = cached_contents

        self.create = async_to_raw_response_wrapper(
            cached_contents.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            cached_contents.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            cached_contents.update,
        )
        self.list = async_to_raw_response_wrapper(
            cached_contents.list,
        )
        self.delete = async_to_raw_response_wrapper(
            cached_contents.delete,
        )


class CachedContentsResourceWithStreamingResponse:
    def __init__(self, cached_contents: CachedContentsResource) -> None:
        self._cached_contents = cached_contents

        self.create = to_streamed_response_wrapper(
            cached_contents.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            cached_contents.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            cached_contents.update,
        )
        self.list = to_streamed_response_wrapper(
            cached_contents.list,
        )
        self.delete = to_streamed_response_wrapper(
            cached_contents.delete,
        )


class AsyncCachedContentsResourceWithStreamingResponse:
    def __init__(self, cached_contents: AsyncCachedContentsResource) -> None:
        self._cached_contents = cached_contents

        self.create = async_to_streamed_response_wrapper(
            cached_contents.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            cached_contents.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            cached_contents.update,
        )
        self.list = async_to_streamed_response_wrapper(
            cached_contents.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            cached_contents.delete,
        )
