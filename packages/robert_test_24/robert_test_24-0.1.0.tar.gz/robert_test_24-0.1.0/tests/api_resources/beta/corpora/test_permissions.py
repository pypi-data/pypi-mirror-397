# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta.corpora import (
    Permission,
    ListPermissions,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPermissions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: RobertTest24) -> None:
        permission = client.beta.corpora.permissions.create(
            corpus="corpus",
            role="ROLE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: RobertTest24) -> None:
        permission = client.beta.corpora.permissions.create(
            corpus="corpus",
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
    def test_raw_response_create(self, client: RobertTest24) -> None:
        response = client.beta.corpora.permissions.with_raw_response.create(
            corpus="corpus",
            role="ROLE_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: RobertTest24) -> None:
        with client.beta.corpora.permissions.with_streaming_response.create(
            corpus="corpus",
            role="ROLE_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(Permission, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.permissions.with_raw_response.create(
                corpus="",
                role="ROLE_UNSPECIFIED",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: RobertTest24) -> None:
        permission = client.beta.corpora.permissions.retrieve(
            permission="permission",
            corpus="corpus",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: RobertTest24) -> None:
        permission = client.beta.corpora.permissions.retrieve(
            permission="permission",
            corpus="corpus",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: RobertTest24) -> None:
        response = client.beta.corpora.permissions.with_raw_response.retrieve(
            permission="permission",
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: RobertTest24) -> None:
        with client.beta.corpora.permissions.with_streaming_response.retrieve(
            permission="permission",
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(Permission, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.permissions.with_raw_response.retrieve(
                permission="permission",
                corpus="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            client.beta.corpora.permissions.with_raw_response.retrieve(
                permission="",
                corpus="corpus",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: RobertTest24) -> None:
        permission = client.beta.corpora.permissions.update(
            permission="permission",
            corpus="corpus",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: RobertTest24) -> None:
        permission = client.beta.corpora.permissions.update(
            permission="permission",
            corpus="corpus",
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
    def test_raw_response_update(self, client: RobertTest24) -> None:
        response = client.beta.corpora.permissions.with_raw_response.update(
            permission="permission",
            corpus="corpus",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: RobertTest24) -> None:
        with client.beta.corpora.permissions.with_streaming_response.update(
            permission="permission",
            corpus="corpus",
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
    def test_path_params_update(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.permissions.with_raw_response.update(
                permission="permission",
                corpus="",
                update_mask="updateMask",
                role="ROLE_UNSPECIFIED",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            client.beta.corpora.permissions.with_raw_response.update(
                permission="",
                corpus="corpus",
                update_mask="updateMask",
                role="ROLE_UNSPECIFIED",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: RobertTest24) -> None:
        permission = client.beta.corpora.permissions.list(
            corpus="corpus",
        )
        assert_matches_type(ListPermissions, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: RobertTest24) -> None:
        permission = client.beta.corpora.permissions.list(
            corpus="corpus",
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
    def test_raw_response_list(self, client: RobertTest24) -> None:
        response = client.beta.corpora.permissions.with_raw_response.list(
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(ListPermissions, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: RobertTest24) -> None:
        with client.beta.corpora.permissions.with_streaming_response.list(
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(ListPermissions, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.permissions.with_raw_response.list(
                corpus="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: RobertTest24) -> None:
        permission = client.beta.corpora.permissions.delete(
            permission="permission",
            corpus="corpus",
        )
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: RobertTest24) -> None:
        permission = client.beta.corpora.permissions.delete(
            permission="permission",
            corpus="corpus",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: RobertTest24) -> None:
        response = client.beta.corpora.permissions.with_raw_response.delete(
            permission="permission",
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: RobertTest24) -> None:
        with client.beta.corpora.permissions.with_streaming_response.delete(
            permission="permission",
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(object, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.permissions.with_raw_response.delete(
                permission="permission",
                corpus="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            client.beta.corpora.permissions.with_raw_response.delete(
                permission="",
                corpus="corpus",
            )


class TestAsyncPermissions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.corpora.permissions.create(
            corpus="corpus",
            role="ROLE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.corpora.permissions.create(
            corpus="corpus",
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
    async def test_raw_response_create(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.permissions.with_raw_response.create(
            corpus="corpus",
            role="ROLE_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.permissions.with_streaming_response.create(
            corpus="corpus",
            role="ROLE_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(Permission, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.permissions.with_raw_response.create(
                corpus="",
                role="ROLE_UNSPECIFIED",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.corpora.permissions.retrieve(
            permission="permission",
            corpus="corpus",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.corpora.permissions.retrieve(
            permission="permission",
            corpus="corpus",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.permissions.with_raw_response.retrieve(
            permission="permission",
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.permissions.with_streaming_response.retrieve(
            permission="permission",
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(Permission, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.permissions.with_raw_response.retrieve(
                permission="permission",
                corpus="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            await async_client.beta.corpora.permissions.with_raw_response.retrieve(
                permission="",
                corpus="corpus",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.corpora.permissions.update(
            permission="permission",
            corpus="corpus",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
        )
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.corpora.permissions.update(
            permission="permission",
            corpus="corpus",
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
    async def test_raw_response_update(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.permissions.with_raw_response.update(
            permission="permission",
            corpus="corpus",
            update_mask="updateMask",
            role="ROLE_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(Permission, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.permissions.with_streaming_response.update(
            permission="permission",
            corpus="corpus",
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
    async def test_path_params_update(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.permissions.with_raw_response.update(
                permission="permission",
                corpus="",
                update_mask="updateMask",
                role="ROLE_UNSPECIFIED",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            await async_client.beta.corpora.permissions.with_raw_response.update(
                permission="",
                corpus="corpus",
                update_mask="updateMask",
                role="ROLE_UNSPECIFIED",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.corpora.permissions.list(
            corpus="corpus",
        )
        assert_matches_type(ListPermissions, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.corpora.permissions.list(
            corpus="corpus",
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
    async def test_raw_response_list(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.permissions.with_raw_response.list(
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(ListPermissions, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.permissions.with_streaming_response.list(
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(ListPermissions, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.permissions.with_raw_response.list(
                corpus="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.corpora.permissions.delete(
            permission="permission",
            corpus="corpus",
        )
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        permission = await async_client.beta.corpora.permissions.delete(
            permission="permission",
            corpus="corpus",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.permissions.with_raw_response.delete(
            permission="permission",
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = await response.parse()
        assert_matches_type(object, permission, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.permissions.with_streaming_response.delete(
            permission="permission",
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(object, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.permissions.with_raw_response.delete(
                permission="permission",
                corpus="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission` but received ''"):
            await async_client.beta.corpora.permissions.with_raw_response.delete(
                permission="",
                corpus="corpus",
            )
