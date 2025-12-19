# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta import Operation
from robert_test_24.types.beta.tuned_models import ListOperations

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOperations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: RobertTest24) -> None:
        operation = client.beta.models.operations.retrieve(
            operation="operation",
            model="model",
        )
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: RobertTest24) -> None:
        operation = client.beta.models.operations.retrieve(
            operation="operation",
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: RobertTest24) -> None:
        response = client.beta.models.operations.with_raw_response.retrieve(
            operation="operation",
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: RobertTest24) -> None:
        with client.beta.models.operations.with_streaming_response.retrieve(
            operation="operation",
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(Operation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.operations.with_raw_response.retrieve(
                operation="operation",
                model="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation` but received ''"):
            client.beta.models.operations.with_raw_response.retrieve(
                operation="",
                model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: RobertTest24) -> None:
        operation = client.beta.models.operations.list(
            model="model",
        )
        assert_matches_type(ListOperations, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: RobertTest24) -> None:
        operation = client.beta.models.operations.list(
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            filter="filter",
            page_size=0,
            page_token="pageToken",
            return_partial_success=True,
        )
        assert_matches_type(ListOperations, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: RobertTest24) -> None:
        response = client.beta.models.operations.with_raw_response.list(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(ListOperations, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: RobertTest24) -> None:
        with client.beta.models.operations.with_streaming_response.list(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(ListOperations, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.operations.with_raw_response.list(
                model="",
            )


class TestAsyncOperations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRobertTest24) -> None:
        operation = await async_client.beta.models.operations.retrieve(
            operation="operation",
            model="model",
        )
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        operation = await async_client.beta.models.operations.retrieve(
            operation="operation",
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.operations.with_raw_response.retrieve(
            operation="operation",
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.operations.with_streaming_response.retrieve(
            operation="operation",
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(Operation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.operations.with_raw_response.retrieve(
                operation="operation",
                model="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation` but received ''"):
            await async_client.beta.models.operations.with_raw_response.retrieve(
                operation="",
                model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRobertTest24) -> None:
        operation = await async_client.beta.models.operations.list(
            model="model",
        )
        assert_matches_type(ListOperations, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        operation = await async_client.beta.models.operations.list(
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            filter="filter",
            page_size=0,
            page_token="pageToken",
            return_partial_success=True,
        )
        assert_matches_type(ListOperations, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.operations.with_raw_response.list(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(ListOperations, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.operations.with_streaming_response.list(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(ListOperations, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.operations.with_raw_response.list(
                model="",
            )
