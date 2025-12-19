# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta.corpora import Permission, ListPermissions

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPermissions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_permission(self, client: RobertTest24) -> None:
        permission = client.beta.tuned_models.permissions.create_permission(
            tuned_model="tunedModel",
            role="ROLE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_permission_with_all_params(self, client: RobertTest24) -> None:
        permission = client.beta.tuned_models.permissions.create_permission(
            tuned_model="tunedModel",
            role="ROLE_UNSPECIFIED",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            email_address="emailAddress",
            grantee_type="GRANTEE_TYPE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_permission(self, client: RobertTest24) -> None:
        response = client.beta.tuned_models.permissions.with_raw_response.create_permission(
            tuned_model="tunedModel",
            role="ROLE_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_permission(self, client: RobertTest24) -> None:
        with client.beta.tuned_models.permissions.with_streaming_response.create_permission(
            tuned_model="tunedModel",
            role="ROLE_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(Permission, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_permission(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            client.beta.tuned_models.permissions.with_raw_response.create_permission(
                tuned_model="",
                role="ROLE_UNSPECIFIED",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_permission(self, client: RobertTest24) -> None:
        permission = client.beta.tuned_models.permissions.delete_permission(
            permission="permission",
            tuned_model="tunedModel",
        )
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_permission_with_all_params(self, client: RobertTest24) -> None:
        permission = client.beta.tuned_models.permissions.delete_permission(
            permission="permission",
            tuned_model="tunedModel",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_permission(self, client: RobertTest24) -> None:
        response = client.beta.tuned_models.permissions.with_raw_response.delete_permission(
            permission="permission",
            tuned_model="tunedModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_permission(self, client: RobertTest24) -> None:
        with client.beta.tuned_models.permissions.with_streaming_response.delete_permission(
            permission="permission",
            tuned_model="tunedModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(object, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_permission(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            client.beta.tuned_models.permissions.with_raw_response.delete_permission(
                permission="permission",
                tuned_model="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            client.beta.tuned_models.permissions.with_raw_response.delete_permission(
                permission="",
                tuned_model="tunedModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_permissions(self, client: RobertTest24) -> None:
        permission = client.beta.tuned_models.permissions.list_permissions(
            tuned_model="tunedModel",
        )
        assert_matches_type(ListPermissions, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_permissions_with_all_params(self, client: RobertTest24) -> None:
        permission = client.beta.tuned_models.permissions.list_permissions(
            tuned_model="tunedModel",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(ListPermissions, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_permissions(self, client: RobertTest24) -> None:
        response = client.beta.tuned_models.permissions.with_raw_response.list_permissions(
            tuned_model="tunedModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(ListPermissions, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_permissions(self, client: RobertTest24) -> None:
        with client.beta.tuned_models.permissions.with_streaming_response.list_permissions(
            tuned_model="tunedModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(ListPermissions, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_permissions(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            client.beta.tuned_models.permissions.with_raw_response.list_permissions(
                tuned_model="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_permission(self, client: RobertTest24) -> None:
        permission = client.beta.tuned_models.permissions.retrieve_permission(
            permission="permission",
            tuned_model="tunedModel",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_permission_with_all_params(self, client: RobertTest24) -> None:
        permission = client.beta.tuned_models.permissions.retrieve_permission(
            permission="permission",
            tuned_model="tunedModel",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_permission(self, client: RobertTest24) -> None:
        response = client.beta.tuned_models.permissions.with_raw_response.retrieve_permission(
            permission="permission",
            tuned_model="tunedModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_permission(self, client: RobertTest24) -> None:
        with client.beta.tuned_models.permissions.with_streaming_response.retrieve_permission(
            permission="permission",
            tuned_model="tunedModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(Permission, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_permission(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            client.beta.tuned_models.permissions.with_raw_response.retrieve_permission(
                permission="permission",
                tuned_model="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            client.beta.tuned_models.permissions.with_raw_response.retrieve_permission(
                permission="",
                tuned_model="tunedModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_permission(self, client: RobertTest24) -> None:
        permission = client.beta.tuned_models.permissions.update_permission(
            permission="permission",
            tuned_model="tunedModel",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_permission_with_all_params(self, client: RobertTest24) -> None:
        permission = client.beta.tuned_models.permissions.update_permission(
            permission="permission",
            tuned_model="tunedModel",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            email_address="emailAddress",
            grantee_type="GRANTEE_TYPE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_permission(self, client: RobertTest24) -> None:
        response = client.beta.tuned_models.permissions.with_raw_response.update_permission(
            permission="permission",
            tuned_model="tunedModel",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_permission(self, client: RobertTest24) -> None:
        with client.beta.tuned_models.permissions.with_streaming_response.update_permission(
            permission="permission",
            tuned_model="tunedModel",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(Permission, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_permission(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            client.beta.tuned_models.permissions.with_raw_response.update_permission(
                permission="permission",
                tuned_model="",
                update_mask="updateMask",
                role="ROLE_UNSPECIFIED",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            client.beta.tuned_models.permissions.with_raw_response.update_permission(
                permission="",
                tuned_model="tunedModel",
                update_mask="updateMask",
                role="ROLE_UNSPECIFIED",
            )


class TestAsyncPermissions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_permission(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.tuned_models.permissions.create_permission(
            tuned_model="tunedModel",
            role="ROLE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_permission_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.tuned_models.permissions.create_permission(
            tuned_model="tunedModel",
            role="ROLE_UNSPECIFIED",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            email_address="emailAddress",
            grantee_type="GRANTEE_TYPE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_permission(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.tuned_models.permissions.with_raw_response.create_permission(
            tuned_model="tunedModel",
            role="ROLE_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_permission(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.tuned_models.permissions.with_streaming_response.create_permission(
            tuned_model="tunedModel",
            role="ROLE_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(Permission, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_permission(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            await async_client.beta.tuned_models.permissions.with_raw_response.create_permission(
                tuned_model="",
                role="ROLE_UNSPECIFIED",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_permission(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.tuned_models.permissions.delete_permission(
            permission="permission",
            tuned_model="tunedModel",
        )
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_permission_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.tuned_models.permissions.delete_permission(
            permission="permission",
            tuned_model="tunedModel",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_permission(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.tuned_models.permissions.with_raw_response.delete_permission(
            permission="permission",
            tuned_model="tunedModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_permission(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.tuned_models.permissions.with_streaming_response.delete_permission(
            permission="permission",
            tuned_model="tunedModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(object, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_permission(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            await async_client.beta.tuned_models.permissions.with_raw_response.delete_permission(
                permission="permission",
                tuned_model="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            await async_client.beta.tuned_models.permissions.with_raw_response.delete_permission(
                permission="",
                tuned_model="tunedModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_permissions(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.tuned_models.permissions.list_permissions(
            tuned_model="tunedModel",
        )
        assert_matches_type(ListPermissions, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_permissions_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.tuned_models.permissions.list_permissions(
            tuned_model="tunedModel",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(ListPermissions, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_permissions(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.tuned_models.permissions.with_raw_response.list_permissions(
            tuned_model="tunedModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(ListPermissions, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_permissions(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.tuned_models.permissions.with_streaming_response.list_permissions(
            tuned_model="tunedModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(ListPermissions, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_permissions(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            await async_client.beta.tuned_models.permissions.with_raw_response.list_permissions(
                tuned_model="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_permission(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.tuned_models.permissions.retrieve_permission(
            permission="permission",
            tuned_model="tunedModel",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_permission_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.tuned_models.permissions.retrieve_permission(
            permission="permission",
            tuned_model="tunedModel",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_permission(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.tuned_models.permissions.with_raw_response.retrieve_permission(
            permission="permission",
            tuned_model="tunedModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_permission(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.tuned_models.permissions.with_streaming_response.retrieve_permission(
            permission="permission",
            tuned_model="tunedModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(Permission, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_permission(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            await async_client.beta.tuned_models.permissions.with_raw_response.retrieve_permission(
                permission="permission",
                tuned_model="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            await async_client.beta.tuned_models.permissions.with_raw_response.retrieve_permission(
                permission="",
                tuned_model="tunedModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_permission(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.tuned_models.permissions.update_permission(
            permission="permission",
            tuned_model="tunedModel",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_permission_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.tuned_models.permissions.update_permission(
            permission="permission",
            tuned_model="tunedModel",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            email_address="emailAddress",
            grantee_type="GRANTEE_TYPE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_permission(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.tuned_models.permissions.with_raw_response.update_permission(
            permission="permission",
            tuned_model="tunedModel",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_permission(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.tuned_models.permissions.with_streaming_response.update_permission(
            permission="permission",
            tuned_model="tunedModel",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(Permission, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_permission(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            await async_client.beta.tuned_models.permissions.with_raw_response.update_permission(
                permission="permission",
                tuned_model="",
                update_mask="updateMask",
                role="ROLE_UNSPECIFIED",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            await async_client.beta.tuned_models.permissions.with_raw_response.update_permission(
                permission="",
                tuned_model="tunedModel",
                update_mask="updateMask",
                role="ROLE_UNSPECIFIED",
            )
