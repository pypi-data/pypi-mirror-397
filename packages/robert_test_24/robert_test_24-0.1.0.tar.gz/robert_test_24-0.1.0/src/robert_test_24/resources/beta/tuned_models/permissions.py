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
from ....types.beta.tuned_models import (
    permission_list_permissions_params,
    permission_create_permission_params,
    permission_delete_permission_params,
    permission_update_permission_params,
    permission_retrieve_permission_params,
)
from ....types.beta.corpora.permission import Permission
from ....types.beta.corpora.list_permissions import ListPermissions

__all__ = ["PermissionsResource", "AsyncPermissionsResource"]


class PermissionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PermissionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return PermissionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PermissionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return PermissionsResourceWithStreamingResponse(self)

    def create_permission(
        self,
        tuned_model: str,
        *,
        role: Literal["ROLE_UNSPECIFIED", "OWNER", "WRITER", "READER"],
        api_empty: permission_create_permission_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        email_address: str | Omit = omit,
        grantee_type: Literal["GRANTEE_TYPE_UNSPECIFIED", "USER", "GROUP", "EVERYONE"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Permission:
        """Create a permission to a specific resource.

        Args:
          role: Required.

        The role granted by this permission.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          email_address: Optional. Immutable. The email address of the user of group which this
              permission refers. Field is not set when permission's grantee type is EVERYONE.

          grantee_type: Optional. Immutable. The type of the grantee.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return self._post(
            f"/v1beta/tunedModels/{tuned_model}/permissions",
            body=maybe_transform(
                {
                    "role": role,
                    "email_address": email_address,
                    "grantee_type": grantee_type,
                },
                permission_create_permission_params.PermissionCreatePermissionParams,
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
                    permission_create_permission_params.PermissionCreatePermissionParams,
                ),
            ),
            cast_to=Permission,
        )

    def delete_permission(
        self,
        permission: str,
        *,
        tuned_model: str,
        api_empty: permission_delete_permission_params.api_empty | Omit = omit,
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
        Deletes the permission.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        if not permission:
            raise ValueError(f"Expected a non-empty value for `permission` but received {permission!r}")
        return self._delete(
            f"/v1beta/tunedModels/{tuned_model}/permissions/{permission}",
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
                    permission_delete_permission_params.PermissionDeletePermissionParams,
                ),
            ),
            cast_to=object,
        )

    def list_permissions(
        self,
        tuned_model: str,
        *,
        api_empty: permission_list_permissions_params.api_empty | Omit = omit,
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
    ) -> ListPermissions:
        """
        Lists permissions for the specific resource.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of `Permission`s to return (per page). The service
              may return fewer permissions.

              If unspecified, at most 10 permissions will be returned. This method returns at
              most 1000 permissions per page, even if you pass larger page_size.

          page_token: Optional. A page token, received from a previous `ListPermissions` call.

              Provide the `page_token` returned by one request as an argument to the next
              request to retrieve the next page.

              When paginating, all other parameters provided to `ListPermissions` must match
              the call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return self._get(
            f"/v1beta/tunedModels/{tuned_model}/permissions",
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
                    permission_list_permissions_params.PermissionListPermissionsParams,
                ),
            ),
            cast_to=ListPermissions,
        )

    def retrieve_permission(
        self,
        permission: str,
        *,
        tuned_model: str,
        api_empty: permission_retrieve_permission_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Permission:
        """
        Gets information about a specific Permission.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        if not permission:
            raise ValueError(f"Expected a non-empty value for `permission` but received {permission!r}")
        return self._get(
            f"/v1beta/tunedModels/{tuned_model}/permissions/{permission}",
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
                    permission_retrieve_permission_params.PermissionRetrievePermissionParams,
                ),
            ),
            cast_to=Permission,
        )

    def update_permission(
        self,
        permission: str,
        *,
        tuned_model: str,
        update_mask: str,
        role: Literal["ROLE_UNSPECIFIED", "OWNER", "WRITER", "READER"],
        api_empty: permission_update_permission_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        email_address: str | Omit = omit,
        grantee_type: Literal["GRANTEE_TYPE_UNSPECIFIED", "USER", "GROUP", "EVERYONE"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Permission:
        """Updates the permission.

        Args:
          update_mask:
              Required.

        The list of fields to update. Accepted ones:

              - role (`Permission.role` field)

          role: Required. The role granted by this permission.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          email_address: Optional. Immutable. The email address of the user of group which this
              permission refers. Field is not set when permission's grantee type is EVERYONE.

          grantee_type: Optional. Immutable. The type of the grantee.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        if not permission:
            raise ValueError(f"Expected a non-empty value for `permission` but received {permission!r}")
        return self._patch(
            f"/v1beta/tunedModels/{tuned_model}/permissions/{permission}",
            body=maybe_transform(
                {
                    "role": role,
                    "email_address": email_address,
                    "grantee_type": grantee_type,
                },
                permission_update_permission_params.PermissionUpdatePermissionParams,
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
                    permission_update_permission_params.PermissionUpdatePermissionParams,
                ),
            ),
            cast_to=Permission,
        )


class AsyncPermissionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPermissionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPermissionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPermissionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/RobertCraigie/robert-test-24-python#with_streaming_response
        """
        return AsyncPermissionsResourceWithStreamingResponse(self)

    async def create_permission(
        self,
        tuned_model: str,
        *,
        role: Literal["ROLE_UNSPECIFIED", "OWNER", "WRITER", "READER"],
        api_empty: permission_create_permission_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        email_address: str | Omit = omit,
        grantee_type: Literal["GRANTEE_TYPE_UNSPECIFIED", "USER", "GROUP", "EVERYONE"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Permission:
        """Create a permission to a specific resource.

        Args:
          role: Required.

        The role granted by this permission.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          email_address: Optional. Immutable. The email address of the user of group which this
              permission refers. Field is not set when permission's grantee type is EVERYONE.

          grantee_type: Optional. Immutable. The type of the grantee.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return await self._post(
            f"/v1beta/tunedModels/{tuned_model}/permissions",
            body=await async_maybe_transform(
                {
                    "role": role,
                    "email_address": email_address,
                    "grantee_type": grantee_type,
                },
                permission_create_permission_params.PermissionCreatePermissionParams,
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
                    permission_create_permission_params.PermissionCreatePermissionParams,
                ),
            ),
            cast_to=Permission,
        )

    async def delete_permission(
        self,
        permission: str,
        *,
        tuned_model: str,
        api_empty: permission_delete_permission_params.api_empty | Omit = omit,
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
        Deletes the permission.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        if not permission:
            raise ValueError(f"Expected a non-empty value for `permission` but received {permission!r}")
        return await self._delete(
            f"/v1beta/tunedModels/{tuned_model}/permissions/{permission}",
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
                    permission_delete_permission_params.PermissionDeletePermissionParams,
                ),
            ),
            cast_to=object,
        )

    async def list_permissions(
        self,
        tuned_model: str,
        *,
        api_empty: permission_list_permissions_params.api_empty | Omit = omit,
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
    ) -> ListPermissions:
        """
        Lists permissions for the specific resource.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          page_size: Optional. The maximum number of `Permission`s to return (per page). The service
              may return fewer permissions.

              If unspecified, at most 10 permissions will be returned. This method returns at
              most 1000 permissions per page, even if you pass larger page_size.

          page_token: Optional. A page token, received from a previous `ListPermissions` call.

              Provide the `page_token` returned by one request as an argument to the next
              request to retrieve the next page.

              When paginating, all other parameters provided to `ListPermissions` must match
              the call that provided the page token.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        return await self._get(
            f"/v1beta/tunedModels/{tuned_model}/permissions",
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
                    permission_list_permissions_params.PermissionListPermissionsParams,
                ),
            ),
            cast_to=ListPermissions,
        )

    async def retrieve_permission(
        self,
        permission: str,
        *,
        tuned_model: str,
        api_empty: permission_retrieve_permission_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Permission:
        """
        Gets information about a specific Permission.

        Args:
          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        if not permission:
            raise ValueError(f"Expected a non-empty value for `permission` but received {permission!r}")
        return await self._get(
            f"/v1beta/tunedModels/{tuned_model}/permissions/{permission}",
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
                    permission_retrieve_permission_params.PermissionRetrievePermissionParams,
                ),
            ),
            cast_to=Permission,
        )

    async def update_permission(
        self,
        permission: str,
        *,
        tuned_model: str,
        update_mask: str,
        role: Literal["ROLE_UNSPECIFIED", "OWNER", "WRITER", "READER"],
        api_empty: permission_update_permission_params.api_empty | Omit = omit,
        alt: Literal["json", "media", "proto"] | Omit = omit,
        callback: str | Omit = omit,
        pretty_print: bool | Omit = omit,
        email_address: str | Omit = omit,
        grantee_type: Literal["GRANTEE_TYPE_UNSPECIFIED", "USER", "GROUP", "EVERYONE"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Permission:
        """Updates the permission.

        Args:
          update_mask:
              Required.

        The list of fields to update. Accepted ones:

              - role (`Permission.role` field)

          role: Required. The role granted by this permission.

          alt: Data format for response.

          callback: JSONP

          pretty_print: Returns response with indentations and line breaks.

          email_address: Optional. Immutable. The email address of the user of group which this
              permission refers. Field is not set when permission's grantee type is EVERYONE.

          grantee_type: Optional. Immutable. The type of the grantee.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tuned_model:
            raise ValueError(f"Expected a non-empty value for `tuned_model` but received {tuned_model!r}")
        if not permission:
            raise ValueError(f"Expected a non-empty value for `permission` but received {permission!r}")
        return await self._patch(
            f"/v1beta/tunedModels/{tuned_model}/permissions/{permission}",
            body=await async_maybe_transform(
                {
                    "role": role,
                    "email_address": email_address,
                    "grantee_type": grantee_type,
                },
                permission_update_permission_params.PermissionUpdatePermissionParams,
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
                    permission_update_permission_params.PermissionUpdatePermissionParams,
                ),
            ),
            cast_to=Permission,
        )


class PermissionsResourceWithRawResponse:
    def __init__(self, permissions: PermissionsResource) -> None:
        self._permissions = permissions

        self.create_permission = to_raw_response_wrapper(
            permissions.create_permission,
        )
        self.delete_permission = to_raw_response_wrapper(
            permissions.delete_permission,
        )
        self.list_permissions = to_raw_response_wrapper(
            permissions.list_permissions,
        )
        self.retrieve_permission = to_raw_response_wrapper(
            permissions.retrieve_permission,
        )
        self.update_permission = to_raw_response_wrapper(
            permissions.update_permission,
        )


class AsyncPermissionsResourceWithRawResponse:
    def __init__(self, permissions: AsyncPermissionsResource) -> None:
        self._permissions = permissions

        self.create_permission = async_to_raw_response_wrapper(
            permissions.create_permission,
        )
        self.delete_permission = async_to_raw_response_wrapper(
            permissions.delete_permission,
        )
        self.list_permissions = async_to_raw_response_wrapper(
            permissions.list_permissions,
        )
        self.retrieve_permission = async_to_raw_response_wrapper(
            permissions.retrieve_permission,
        )
        self.update_permission = async_to_raw_response_wrapper(
            permissions.update_permission,
        )


class PermissionsResourceWithStreamingResponse:
    def __init__(self, permissions: PermissionsResource) -> None:
        self._permissions = permissions

        self.create_permission = to_streamed_response_wrapper(
            permissions.create_permission,
        )
        self.delete_permission = to_streamed_response_wrapper(
            permissions.delete_permission,
        )
        self.list_permissions = to_streamed_response_wrapper(
            permissions.list_permissions,
        )
        self.retrieve_permission = to_streamed_response_wrapper(
            permissions.retrieve_permission,
        )
        self.update_permission = to_streamed_response_wrapper(
            permissions.update_permission,
        )


class AsyncPermissionsResourceWithStreamingResponse:
    def __init__(self, permissions: AsyncPermissionsResource) -> None:
        self._permissions = permissions

        self.create_permission = async_to_streamed_response_wrapper(
            permissions.create_permission,
        )
        self.delete_permission = async_to_streamed_response_wrapper(
            permissions.delete_permission,
        )
        self.list_permissions = async_to_streamed_response_wrapper(
            permissions.list_permissions,
        )
        self.retrieve_permission = async_to_streamed_response_wrapper(
            permissions.retrieve_permission,
        )
        self.update_permission = async_to_streamed_response_wrapper(
            permissions.update_permission,
        )
