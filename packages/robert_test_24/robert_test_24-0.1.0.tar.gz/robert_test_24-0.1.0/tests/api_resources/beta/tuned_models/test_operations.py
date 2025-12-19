# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta import Operation
from robert_test_24.types.beta.tuned_models import (
    ListOperations,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOperations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_operations(self, client: RobertTest24) -> None:
        operation = client.beta.tuned_models.operations.list_operations(
            tuned_model="tunedModel",
        )
        assert_matches_type(ListOperations, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_operations_with_all_params(self, client: RobertTest24) -> None:
        operation = client.beta.tuned_models.operations.list_operations(
            tuned_model="tunedModel",
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
    def test_raw_response_list_operations(self, client: RobertTest24) -> None:
        response = client.beta.tuned_models.operations.with_raw_response.list_operations(
            tuned_model="tunedModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(ListOperations, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_operations(self, client: RobertTest24) -> None:
        with client.beta.tuned_models.operations.with_streaming_response.list_operations(
            tuned_model="tunedModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(ListOperations, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_operations(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            client.beta.tuned_models.operations.with_raw_response.list_operations(
                tuned_model="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_operation(self, client: RobertTest24) -> None:
        operation = client.beta.tuned_models.operations.retrieve_operation(
            operation="operation",
            tuned_model="tunedModel",
        )
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_operation_with_all_params(self, client: RobertTest24) -> None:
        operation = client.beta.tuned_models.operations.retrieve_operation(
            operation="operation",
            tuned_model="tunedModel",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_operation(self, client: RobertTest24) -> None:
        response = client.beta.tuned_models.operations.with_raw_response.retrieve_operation(
            operation="operation",
            tuned_model="tunedModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_operation(self, client: RobertTest24) -> None:
        with client.beta.tuned_models.operations.with_streaming_response.retrieve_operation(
            operation="operation",
            tuned_model="tunedModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(Operation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_operation(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            client.beta.tuned_models.operations.with_raw_response.retrieve_operation(
                operation="operation",
                tuned_model="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation` but received ''"):
            client.beta.tuned_models.operations.with_raw_response.retrieve_operation(
                operation="",
                tuned_model="tunedModel",
            )


class TestAsyncOperations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_operations(self, async_client: AsyncRobertTest24) -> None:
        operation = await async_client.beta.tuned_models.operations.list_operations(
            tuned_model="tunedModel",
        )
        assert_matches_type(ListOperations, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_operations_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        operation = await async_client.beta.tuned_models.operations.list_operations(
            tuned_model="tunedModel",
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
    async def test_raw_response_list_operations(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.tuned_models.operations.with_raw_response.list_operations(
            tuned_model="tunedModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(ListOperations, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_operations(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.tuned_models.operations.with_streaming_response.list_operations(
            tuned_model="tunedModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(ListOperations, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_operations(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            await async_client.beta.tuned_models.operations.with_raw_response.list_operations(
                tuned_model="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_operation(self, async_client: AsyncRobertTest24) -> None:
        operation = await async_client.beta.tuned_models.operations.retrieve_operation(
            operation="operation",
            tuned_model="tunedModel",
        )
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_operation_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        operation = await async_client.beta.tuned_models.operations.retrieve_operation(
            operation="operation",
            tuned_model="tunedModel",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_operation(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.tuned_models.operations.with_raw_response.retrieve_operation(
            operation="operation",
            tuned_model="tunedModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(Operation, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_operation(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.tuned_models.operations.with_streaming_response.retrieve_operation(
            operation="operation",
            tuned_model="tunedModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(Operation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_operation(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tuned_model` but received ''"):
            await async_client.beta.tuned_models.operations.with_raw_response.retrieve_operation(
                operation="operation",
                tuned_model="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation` but received ''"):
            await async_client.beta.tuned_models.operations.with_raw_response.retrieve_operation(
                operation="",
                tuned_model="tunedModel",
            )
