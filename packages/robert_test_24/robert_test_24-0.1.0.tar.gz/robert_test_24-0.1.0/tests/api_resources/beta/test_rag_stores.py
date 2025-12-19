# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta import (
    RagStore,
    Operation,
    RagStoreListResponse,
    RagStoreUploadToRagStoreResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRagStores:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.create()
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.create(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            display_name="displayName",
        )
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = response.parse()
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = response.parse()
            assert_matches_type(RagStore, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.retrieve(
            rag_store="ragStore",
        )
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.retrieve(
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.with_raw_response.retrieve(
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = response.parse()
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.with_streaming_response.retrieve(
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = response.parse()
            assert_matches_type(RagStore, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            client.beta.rag_stores.with_raw_response.retrieve(
                rag_store="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.update(
            rag_store="ragStore",
            update_mask="updateMask",
        )
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.update(
            rag_store="ragStore",
            update_mask="updateMask",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            display_name="displayName",
        )
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.with_raw_response.update(
            rag_store="ragStore",
            update_mask="updateMask",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = response.parse()
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.with_streaming_response.update(
            rag_store="ragStore",
            update_mask="updateMask",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = response.parse()
            assert_matches_type(RagStore, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            client.beta.rag_stores.with_raw_response.update(
                rag_store="",
                update_mask="updateMask",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.list()
        assert_matches_type(RagStoreListResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.list(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(RagStoreListResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = response.parse()
        assert_matches_type(RagStoreListResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = response.parse()
            assert_matches_type(RagStoreListResponse, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.delete(
            rag_store="ragStore",
        )
        assert_matches_type(object, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.delete(
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            force=True,
        )
        assert_matches_type(object, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.with_raw_response.delete(
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = response.parse()
        assert_matches_type(object, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.with_streaming_response.delete(
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = response.parse()
            assert_matches_type(object, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            client.beta.rag_stores.with_raw_response.delete(
                rag_store="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_operation_status(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.get_operation_status(
            operation="operation",
            rag_store="ragStore",
        )
        assert_matches_type(Operation, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_operation_status_with_all_params(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.get_operation_status(
            operation="operation",
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Operation, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_operation_status(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.with_raw_response.get_operation_status(
            operation="operation",
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = response.parse()
        assert_matches_type(Operation, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_operation_status(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.with_streaming_response.get_operation_status(
            operation="operation",
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = response.parse()
            assert_matches_type(Operation, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_operation_status(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            client.beta.rag_stores.with_raw_response.get_operation_status(
                operation="operation",
                rag_store="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation` but received ''"):
            client.beta.rag_stores.with_raw_response.get_operation_status(
                operation="",
                rag_store="ragStore",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_to_rag_store(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.upload_to_rag_store(
            rag_store="ragStore",
        )
        assert_matches_type(RagStoreUploadToRagStoreResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_to_rag_store_with_all_params(self, client: RobertTest24) -> None:
        rag_store = client.beta.rag_stores.upload_to_rag_store(
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            chunking_config={
                "white_space_config": {
                    "max_overlap_tokens": 0,
                    "max_tokens_per_chunk": 0,
                }
            },
            custom_metadata=[
                {
                    "key": "key",
                    "numeric_value": 0,
                    "string_list_value": {"values": ["string"]},
                    "string_value": "stringValue",
                }
            ],
            display_name="displayName",
            mime_type="mimeType",
        )
        assert_matches_type(RagStoreUploadToRagStoreResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upload_to_rag_store(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.with_raw_response.upload_to_rag_store(
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = response.parse()
        assert_matches_type(RagStoreUploadToRagStoreResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upload_to_rag_store(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.with_streaming_response.upload_to_rag_store(
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = response.parse()
            assert_matches_type(RagStoreUploadToRagStoreResponse, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_upload_to_rag_store(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            client.beta.rag_stores.with_raw_response.upload_to_rag_store(
                rag_store="",
            )


class TestAsyncRagStores:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.create()
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.create(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            display_name="displayName",
        )
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = await response.parse()
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = await response.parse()
            assert_matches_type(RagStore, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.retrieve(
            rag_store="ragStore",
        )
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.retrieve(
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.with_raw_response.retrieve(
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = await response.parse()
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.with_streaming_response.retrieve(
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = await response.parse()
            assert_matches_type(RagStore, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            await async_client.beta.rag_stores.with_raw_response.retrieve(
                rag_store="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.update(
            rag_store="ragStore",
            update_mask="updateMask",
        )
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.update(
            rag_store="ragStore",
            update_mask="updateMask",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            display_name="displayName",
        )
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.with_raw_response.update(
            rag_store="ragStore",
            update_mask="updateMask",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = await response.parse()
        assert_matches_type(RagStore, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.with_streaming_response.update(
            rag_store="ragStore",
            update_mask="updateMask",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = await response.parse()
            assert_matches_type(RagStore, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            await async_client.beta.rag_stores.with_raw_response.update(
                rag_store="",
                update_mask="updateMask",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.list()
        assert_matches_type(RagStoreListResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.list(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(RagStoreListResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = await response.parse()
        assert_matches_type(RagStoreListResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = await response.parse()
            assert_matches_type(RagStoreListResponse, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.delete(
            rag_store="ragStore",
        )
        assert_matches_type(object, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.delete(
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            force=True,
        )
        assert_matches_type(object, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.with_raw_response.delete(
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = await response.parse()
        assert_matches_type(object, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.with_streaming_response.delete(
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = await response.parse()
            assert_matches_type(object, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            await async_client.beta.rag_stores.with_raw_response.delete(
                rag_store="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_operation_status(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.get_operation_status(
            operation="operation",
            rag_store="ragStore",
        )
        assert_matches_type(Operation, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_operation_status_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.get_operation_status(
            operation="operation",
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Operation, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_operation_status(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.with_raw_response.get_operation_status(
            operation="operation",
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = await response.parse()
        assert_matches_type(Operation, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_operation_status(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.with_streaming_response.get_operation_status(
            operation="operation",
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = await response.parse()
            assert_matches_type(Operation, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_operation_status(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            await async_client.beta.rag_stores.with_raw_response.get_operation_status(
                operation="operation",
                rag_store="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation` but received ''"):
            await async_client.beta.rag_stores.with_raw_response.get_operation_status(
                operation="",
                rag_store="ragStore",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_to_rag_store(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.upload_to_rag_store(
            rag_store="ragStore",
        )
        assert_matches_type(RagStoreUploadToRagStoreResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_to_rag_store_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        rag_store = await async_client.beta.rag_stores.upload_to_rag_store(
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            chunking_config={
                "white_space_config": {
                    "max_overlap_tokens": 0,
                    "max_tokens_per_chunk": 0,
                }
            },
            custom_metadata=[
                {
                    "key": "key",
                    "numeric_value": 0,
                    "string_list_value": {"values": ["string"]},
                    "string_value": "stringValue",
                }
            ],
            display_name="displayName",
            mime_type="mimeType",
        )
        assert_matches_type(RagStoreUploadToRagStoreResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upload_to_rag_store(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.with_raw_response.upload_to_rag_store(
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rag_store = await response.parse()
        assert_matches_type(RagStoreUploadToRagStoreResponse, rag_store, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upload_to_rag_store(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.with_streaming_response.upload_to_rag_store(
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rag_store = await response.parse()
            assert_matches_type(RagStoreUploadToRagStoreResponse, rag_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_upload_to_rag_store(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            await async_client.beta.rag_stores.with_raw_response.upload_to_rag_store(
                rag_store="",
            )
