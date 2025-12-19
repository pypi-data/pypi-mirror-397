# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta import (
    GeneratedFile,
    GeneratedFileRetrieveGeneratedFilesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGeneratedFiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: RobertTest24) -> None:
        generated_file = client.beta.generated_files.retrieve(
            generated_file="generatedFile",
        )
        assert_matches_type(GeneratedFile, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: RobertTest24) -> None:
        generated_file = client.beta.generated_files.retrieve(
            generated_file="generatedFile",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(GeneratedFile, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: RobertTest24) -> None:
        response = client.beta.generated_files.with_raw_response.retrieve(
            generated_file="generatedFile",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        generated_file = response.parse()
        assert_matches_type(GeneratedFile, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: RobertTest24) -> None:
        with client.beta.generated_files.with_streaming_response.retrieve(
            generated_file="generatedFile",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            generated_file = response.parse()
            assert_matches_type(GeneratedFile, generated_file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `generated_file` but received ''"):
            client.beta.generated_files.with_raw_response.retrieve(
                generated_file="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_generated_files(self, client: RobertTest24) -> None:
        generated_file = client.beta.generated_files.retrieve_generated_files()
        assert_matches_type(GeneratedFileRetrieveGeneratedFilesResponse, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_generated_files_with_all_params(self, client: RobertTest24) -> None:
        generated_file = client.beta.generated_files.retrieve_generated_files(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(GeneratedFileRetrieveGeneratedFilesResponse, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_generated_files(self, client: RobertTest24) -> None:
        response = client.beta.generated_files.with_raw_response.retrieve_generated_files()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        generated_file = response.parse()
        assert_matches_type(GeneratedFileRetrieveGeneratedFilesResponse, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_generated_files(self, client: RobertTest24) -> None:
        with client.beta.generated_files.with_streaming_response.retrieve_generated_files() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            generated_file = response.parse()
            assert_matches_type(GeneratedFileRetrieveGeneratedFilesResponse, generated_file, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncGeneratedFiles:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRobertTest24) -> None:
        generated_file = await async_client.beta.generated_files.retrieve(
            generated_file="generatedFile",
        )
        assert_matches_type(GeneratedFile, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        generated_file = await async_client.beta.generated_files.retrieve(
            generated_file="generatedFile",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(GeneratedFile, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.generated_files.with_raw_response.retrieve(
            generated_file="generatedFile",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        generated_file = await response.parse()
        assert_matches_type(GeneratedFile, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.generated_files.with_streaming_response.retrieve(
            generated_file="generatedFile",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            generated_file = await response.parse()
            assert_matches_type(GeneratedFile, generated_file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `generated_file` but received ''"):
            await async_client.beta.generated_files.with_raw_response.retrieve(
                generated_file="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_generated_files(self, async_client: AsyncRobertTest24) -> None:
        generated_file = await async_client.beta.generated_files.retrieve_generated_files()
        assert_matches_type(GeneratedFileRetrieveGeneratedFilesResponse, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_generated_files_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        generated_file = await async_client.beta.generated_files.retrieve_generated_files(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(GeneratedFileRetrieveGeneratedFilesResponse, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_generated_files(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.generated_files.with_raw_response.retrieve_generated_files()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        generated_file = await response.parse()
        assert_matches_type(GeneratedFileRetrieveGeneratedFilesResponse, generated_file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_generated_files(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.generated_files.with_streaming_response.retrieve_generated_files() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            generated_file = await response.parse()
            assert_matches_type(GeneratedFileRetrieveGeneratedFilesResponse, generated_file, path=["response"])

        assert cast(Any, response.is_closed) is True
