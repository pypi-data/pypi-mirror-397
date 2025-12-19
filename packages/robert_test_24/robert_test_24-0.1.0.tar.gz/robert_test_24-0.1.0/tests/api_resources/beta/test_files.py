# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta import (
    File,
    FileListResponse,
    FileCreateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: RobertTest24) -> None:
        file = client.beta.files.create()
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: RobertTest24) -> None:
        file = client.beta.files.create(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            file={
                "display_name": "displayName",
                "name": "name",
                "source": "SOURCE_UNSPECIFIED",
            },
        )
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: RobertTest24) -> None:
        response = client.beta.files.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: RobertTest24) -> None:
        with client.beta.files.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileCreateResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: RobertTest24) -> None:
        file = client.beta.files.retrieve(
            file="file",
        )
        assert_matches_type(File, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: RobertTest24) -> None:
        file = client.beta.files.retrieve(
            file="file",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(File, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: RobertTest24) -> None:
        response = client.beta.files.with_raw_response.retrieve(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(File, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: RobertTest24) -> None:
        with client.beta.files.with_streaming_response.retrieve(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(File, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file` but received ''"):
            client.beta.files.with_raw_response.retrieve(
                file="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: RobertTest24) -> None:
        file = client.beta.files.list()
        assert_matches_type(FileListResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: RobertTest24) -> None:
        file = client.beta.files.list(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(FileListResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: RobertTest24) -> None:
        response = client.beta.files.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileListResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: RobertTest24) -> None:
        with client.beta.files.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileListResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: RobertTest24) -> None:
        file = client.beta.files.delete(
            file="file",
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: RobertTest24) -> None:
        file = client.beta.files.delete(
            file="file",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: RobertTest24) -> None:
        response = client.beta.files.with_raw_response.delete(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: RobertTest24) -> None:
        with client.beta.files.with_streaming_response.delete(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(object, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file` but received ''"):
            client.beta.files.with_raw_response.delete(
                file="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_file_download(self, client: RobertTest24) -> None:
        file = client.beta.files.retrieve_file_download(
            file="file",
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_file_download_with_all_params(self, client: RobertTest24) -> None:
        file = client.beta.files.retrieve_file_download(
            file="file",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_file_download(self, client: RobertTest24) -> None:
        response = client.beta.files.with_raw_response.retrieve_file_download(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_file_download(self, client: RobertTest24) -> None:
        with client.beta.files.with_streaming_response.retrieve_file_download(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(object, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_file_download(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file` but received ''"):
            client.beta.files.with_raw_response.retrieve_file_download(
                file="",
            )


class TestAsyncFiles:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRobertTest24) -> None:
        file = await async_client.beta.files.create()
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        file = await async_client.beta.files.create(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            file={
                "display_name": "displayName",
                "name": "name",
                "source": "SOURCE_UNSPECIFIED",
            },
        )
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.files.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.files.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileCreateResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRobertTest24) -> None:
        file = await async_client.beta.files.retrieve(
            file="file",
        )
        assert_matches_type(File, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        file = await async_client.beta.files.retrieve(
            file="file",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(File, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.files.with_raw_response.retrieve(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(File, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.files.with_streaming_response.retrieve(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(File, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file` but received ''"):
            await async_client.beta.files.with_raw_response.retrieve(
                file="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRobertTest24) -> None:
        file = await async_client.beta.files.list()
        assert_matches_type(FileListResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        file = await async_client.beta.files.list(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(FileListResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.files.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileListResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.files.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileListResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRobertTest24) -> None:
        file = await async_client.beta.files.delete(
            file="file",
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        file = await async_client.beta.files.delete(
            file="file",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.files.with_raw_response.delete(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.files.with_streaming_response.delete(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(object, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file` but received ''"):
            await async_client.beta.files.with_raw_response.delete(
                file="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_file_download(self, async_client: AsyncRobertTest24) -> None:
        file = await async_client.beta.files.retrieve_file_download(
            file="file",
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_file_download_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        file = await async_client.beta.files.retrieve_file_download(
            file="file",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_file_download(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.files.with_raw_response.retrieve_file_download(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(object, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_file_download(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.files.with_streaming_response.retrieve_file_download(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(object, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_file_download(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file` but received ''"):
            await async_client.beta.files.with_raw_response.retrieve_file_download(
                file="",
            )
