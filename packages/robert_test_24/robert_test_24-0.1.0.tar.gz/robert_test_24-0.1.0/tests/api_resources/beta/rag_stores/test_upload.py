# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta import Operation

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUpload:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_operation_status(self, client: RobertTest24) -> None:
        upload = client.beta.rag_stores.upload.get_operation_status(
            operations_id="operationsId",
            rag_stores_id="ragStoresId",
        )
        assert_matches_type(Operation, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_operation_status_with_all_params(self, client: RobertTest24) -> None:
        upload = client.beta.rag_stores.upload.get_operation_status(
            operations_id="operationsId",
            rag_stores_id="ragStoresId",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Operation, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_operation_status(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.upload.with_raw_response.get_operation_status(
            operations_id="operationsId",
            rag_stores_id="ragStoresId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(Operation, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_operation_status(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.upload.with_streaming_response.get_operation_status(
            operations_id="operationsId",
            rag_stores_id="ragStoresId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(Operation, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_operation_status(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_stores_id` but received ''"):
            client.beta.rag_stores.upload.with_raw_response.get_operation_status(
                operations_id="operationsId",
                rag_stores_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operations_id` but received ''"):
            client.beta.rag_stores.upload.with_raw_response.get_operation_status(
                operations_id="",
                rag_stores_id="ragStoresId",
            )


class TestAsyncUpload:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_operation_status(self, async_client: AsyncRobertTest24) -> None:
        upload = await async_client.beta.rag_stores.upload.get_operation_status(
            operations_id="operationsId",
            rag_stores_id="ragStoresId",
        )
        assert_matches_type(Operation, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_operation_status_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        upload = await async_client.beta.rag_stores.upload.get_operation_status(
            operations_id="operationsId",
            rag_stores_id="ragStoresId",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Operation, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_operation_status(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.upload.with_raw_response.get_operation_status(
            operations_id="operationsId",
            rag_stores_id="ragStoresId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(Operation, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_operation_status(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.upload.with_streaming_response.get_operation_status(
            operations_id="operationsId",
            rag_stores_id="ragStoresId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(Operation, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_operation_status(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_stores_id` but received ''"):
            await async_client.beta.rag_stores.upload.with_raw_response.get_operation_status(
                operations_id="operationsId",
                rag_stores_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operations_id` but received ''"):
            await async_client.beta.rag_stores.upload.with_raw_response.get_operation_status(
                operations_id="",
                rag_stores_id="ragStoresId",
            )
