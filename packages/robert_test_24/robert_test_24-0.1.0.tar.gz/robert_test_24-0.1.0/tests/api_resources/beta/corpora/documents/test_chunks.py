# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta.corpora.documents import (
    Chunk,
    ChunkListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestChunks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: RobertTest24) -> None:
        chunk = client.beta.corpora.documents.chunks.create(
            document="document",
            corpus="corpus",
            data={},
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: RobertTest24) -> None:
        chunk = client.beta.corpora.documents.chunks.create(
            document="document",
            corpus="corpus",
            data={"string_value": "stringValue"},
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            custom_metadata=[
                {
                    "key": "key",
                    "numeric_value": 0,
                    "string_list_value": {"values": ["string"]},
                    "string_value": "stringValue",
                }
            ],
            name="name",
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: RobertTest24) -> None:
        response = client.beta.corpora.documents.chunks.with_raw_response.create(
            document="document",
            corpus="corpus",
            data={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chunk = response.parse()
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: RobertTest24) -> None:
        with client.beta.corpora.documents.chunks.with_streaming_response.create(
            document="document",
            corpus="corpus",
            data={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chunk = response.parse()
            assert_matches_type(Chunk, chunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.create(
                document="document",
                corpus="",
                data={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.create(
                document="",
                corpus="corpus",
                data={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: RobertTest24) -> None:
        chunk = client.beta.corpora.documents.chunks.retrieve(
            chunk="chunk",
            corpus="corpus",
            document="document",
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: RobertTest24) -> None:
        chunk = client.beta.corpora.documents.chunks.retrieve(
            chunk="chunk",
            corpus="corpus",
            document="document",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: RobertTest24) -> None:
        response = client.beta.corpora.documents.chunks.with_raw_response.retrieve(
            chunk="chunk",
            corpus="corpus",
            document="document",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chunk = response.parse()
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: RobertTest24) -> None:
        with client.beta.corpora.documents.chunks.with_streaming_response.retrieve(
            chunk="chunk",
            corpus="corpus",
            document="document",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chunk = response.parse()
            assert_matches_type(Chunk, chunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.retrieve(
                chunk="chunk",
                corpus="",
                document="document",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.retrieve(
                chunk="chunk",
                corpus="corpus",
                document="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `chunk` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.retrieve(
                chunk="",
                corpus="corpus",
                document="document",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: RobertTest24) -> None:
        chunk = client.beta.corpora.documents.chunks.update(
            chunk="chunk",
            corpus="corpus",
            document="document",
            update_mask="updateMask",
            data={},
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: RobertTest24) -> None:
        chunk = client.beta.corpora.documents.chunks.update(
            chunk="chunk",
            corpus="corpus",
            document="document",
            update_mask="updateMask",
            data={"string_value": "stringValue"},
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            custom_metadata=[
                {
                    "key": "key",
                    "numeric_value": 0,
                    "string_list_value": {"values": ["string"]},
                    "string_value": "stringValue",
                }
            ],
            name="name",
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: RobertTest24) -> None:
        response = client.beta.corpora.documents.chunks.with_raw_response.update(
            chunk="chunk",
            corpus="corpus",
            document="document",
            update_mask="updateMask",
            data={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chunk = response.parse()
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: RobertTest24) -> None:
        with client.beta.corpora.documents.chunks.with_streaming_response.update(
            chunk="chunk",
            corpus="corpus",
            document="document",
            update_mask="updateMask",
            data={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chunk = response.parse()
            assert_matches_type(Chunk, chunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.update(
                chunk="chunk",
                corpus="",
                document="document",
                update_mask="updateMask",
                data={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.update(
                chunk="chunk",
                corpus="corpus",
                document="",
                update_mask="updateMask",
                data={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `chunk` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.update(
                chunk="",
                corpus="corpus",
                document="document",
                update_mask="updateMask",
                data={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: RobertTest24) -> None:
        chunk = client.beta.corpora.documents.chunks.list(
            document="document",
            corpus="corpus",
        )
        assert_matches_type(ChunkListResponse, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: RobertTest24) -> None:
        chunk = client.beta.corpora.documents.chunks.list(
            document="document",
            corpus="corpus",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(ChunkListResponse, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: RobertTest24) -> None:
        response = client.beta.corpora.documents.chunks.with_raw_response.list(
            document="document",
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chunk = response.parse()
        assert_matches_type(ChunkListResponse, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: RobertTest24) -> None:
        with client.beta.corpora.documents.chunks.with_streaming_response.list(
            document="document",
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chunk = response.parse()
            assert_matches_type(ChunkListResponse, chunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.list(
                document="document",
                corpus="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.list(
                document="",
                corpus="corpus",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: RobertTest24) -> None:
        chunk = client.beta.corpora.documents.chunks.delete(
            chunk="chunk",
            corpus="corpus",
            document="document",
        )
        assert_matches_type(object, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: RobertTest24) -> None:
        chunk = client.beta.corpora.documents.chunks.delete(
            chunk="chunk",
            corpus="corpus",
            document="document",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: RobertTest24) -> None:
        response = client.beta.corpora.documents.chunks.with_raw_response.delete(
            chunk="chunk",
            corpus="corpus",
            document="document",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chunk = response.parse()
        assert_matches_type(object, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: RobertTest24) -> None:
        with client.beta.corpora.documents.chunks.with_streaming_response.delete(
            chunk="chunk",
            corpus="corpus",
            document="document",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chunk = response.parse()
            assert_matches_type(object, chunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.delete(
                chunk="chunk",
                corpus="",
                document="document",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.delete(
                chunk="chunk",
                corpus="corpus",
                document="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `chunk` but received ''"):
            client.beta.corpora.documents.chunks.with_raw_response.delete(
                chunk="",
                corpus="corpus",
                document="document",
            )


class TestAsyncChunks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRobertTest24) -> None:
        chunk = await async_client.beta.corpora.documents.chunks.create(
            document="document",
            corpus="corpus",
            data={},
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        chunk = await async_client.beta.corpora.documents.chunks.create(
            document="document",
            corpus="corpus",
            data={"string_value": "stringValue"},
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            custom_metadata=[
                {
                    "key": "key",
                    "numeric_value": 0,
                    "string_list_value": {"values": ["string"]},
                    "string_value": "stringValue",
                }
            ],
            name="name",
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.documents.chunks.with_raw_response.create(
            document="document",
            corpus="corpus",
            data={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chunk = await response.parse()
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.documents.chunks.with_streaming_response.create(
            document="document",
            corpus="corpus",
            data={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chunk = await response.parse()
            assert_matches_type(Chunk, chunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.create(
                document="document",
                corpus="",
                data={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.create(
                document="",
                corpus="corpus",
                data={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRobertTest24) -> None:
        chunk = await async_client.beta.corpora.documents.chunks.retrieve(
            chunk="chunk",
            corpus="corpus",
            document="document",
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        chunk = await async_client.beta.corpora.documents.chunks.retrieve(
            chunk="chunk",
            corpus="corpus",
            document="document",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.documents.chunks.with_raw_response.retrieve(
            chunk="chunk",
            corpus="corpus",
            document="document",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chunk = await response.parse()
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.documents.chunks.with_streaming_response.retrieve(
            chunk="chunk",
            corpus="corpus",
            document="document",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chunk = await response.parse()
            assert_matches_type(Chunk, chunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.retrieve(
                chunk="chunk",
                corpus="",
                document="document",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.retrieve(
                chunk="chunk",
                corpus="corpus",
                document="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `chunk` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.retrieve(
                chunk="",
                corpus="corpus",
                document="document",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncRobertTest24) -> None:
        chunk = await async_client.beta.corpora.documents.chunks.update(
            chunk="chunk",
            corpus="corpus",
            document="document",
            update_mask="updateMask",
            data={},
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        chunk = await async_client.beta.corpora.documents.chunks.update(
            chunk="chunk",
            corpus="corpus",
            document="document",
            update_mask="updateMask",
            data={"string_value": "stringValue"},
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            custom_metadata=[
                {
                    "key": "key",
                    "numeric_value": 0,
                    "string_list_value": {"values": ["string"]},
                    "string_value": "stringValue",
                }
            ],
            name="name",
        )
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.documents.chunks.with_raw_response.update(
            chunk="chunk",
            corpus="corpus",
            document="document",
            update_mask="updateMask",
            data={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chunk = await response.parse()
        assert_matches_type(Chunk, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.documents.chunks.with_streaming_response.update(
            chunk="chunk",
            corpus="corpus",
            document="document",
            update_mask="updateMask",
            data={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chunk = await response.parse()
            assert_matches_type(Chunk, chunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.update(
                chunk="chunk",
                corpus="",
                document="document",
                update_mask="updateMask",
                data={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.update(
                chunk="chunk",
                corpus="corpus",
                document="",
                update_mask="updateMask",
                data={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `chunk` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.update(
                chunk="",
                corpus="corpus",
                document="document",
                update_mask="updateMask",
                data={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRobertTest24) -> None:
        chunk = await async_client.beta.corpora.documents.chunks.list(
            document="document",
            corpus="corpus",
        )
        assert_matches_type(ChunkListResponse, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        chunk = await async_client.beta.corpora.documents.chunks.list(
            document="document",
            corpus="corpus",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(ChunkListResponse, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.documents.chunks.with_raw_response.list(
            document="document",
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chunk = await response.parse()
        assert_matches_type(ChunkListResponse, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.documents.chunks.with_streaming_response.list(
            document="document",
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chunk = await response.parse()
            assert_matches_type(ChunkListResponse, chunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.list(
                document="document",
                corpus="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.list(
                document="",
                corpus="corpus",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRobertTest24) -> None:
        chunk = await async_client.beta.corpora.documents.chunks.delete(
            chunk="chunk",
            corpus="corpus",
            document="document",
        )
        assert_matches_type(object, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        chunk = await async_client.beta.corpora.documents.chunks.delete(
            chunk="chunk",
            corpus="corpus",
            document="document",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.documents.chunks.with_raw_response.delete(
            chunk="chunk",
            corpus="corpus",
            document="document",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chunk = await response.parse()
        assert_matches_type(object, chunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.documents.chunks.with_streaming_response.delete(
            chunk="chunk",
            corpus="corpus",
            document="document",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chunk = await response.parse()
            assert_matches_type(object, chunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.delete(
                chunk="chunk",
                corpus="",
                document="document",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.delete(
                chunk="chunk",
                corpus="corpus",
                document="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `chunk` but received ''"):
            await async_client.beta.corpora.documents.chunks.with_raw_response.delete(
                chunk="",
                corpus="corpus",
                document="document",
            )
