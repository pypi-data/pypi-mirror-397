# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta.corpora import (
    DocumentChunksBatchCreateResponse,
    DocumentChunksBatchUpdateResponse,
)
from robert_test_24.types.beta.rag_stores import Document

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocuments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: RobertTest24) -> None:
        document = client.beta.corpora.documents.update(
            document="document",
            corpus="corpus",
            update_mask="updateMask",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: RobertTest24) -> None:
        document = client.beta.corpora.documents.update(
            document="document",
            corpus="corpus",
            update_mask="updateMask",
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
            display_name="displayName",
            name="name",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: RobertTest24) -> None:
        response = client.beta.corpora.documents.with_raw_response.update(
            document="document",
            corpus="corpus",
            update_mask="updateMask",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: RobertTest24) -> None:
        with client.beta.corpora.documents.with_streaming_response.update(
            document="document",
            corpus="corpus",
            update_mask="updateMask",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.documents.with_raw_response.update(
                document="document",
                corpus="",
                update_mask="updateMask",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.corpora.documents.with_raw_response.update(
                document="",
                corpus="corpus",
                update_mask="updateMask",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_chunks_batch_create(self, client: RobertTest24) -> None:
        document = client.beta.corpora.documents.chunks_batch_create(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "parent": "parent",
                }
            ],
        )
        assert_matches_type(DocumentChunksBatchCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_chunks_batch_create_with_all_params(self, client: RobertTest24) -> None:
        document = client.beta.corpora.documents.chunks_batch_create(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {
                        "data": {"string_value": "stringValue"},
                        "custom_metadata": [
                            {
                                "key": "key",
                                "numeric_value": 0,
                                "string_list_value": {"values": ["string"]},
                                "string_value": "stringValue",
                            }
                        ],
                        "name": "name",
                    },
                    "parent": "parent",
                }
            ],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(DocumentChunksBatchCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_chunks_batch_create(self, client: RobertTest24) -> None:
        response = client.beta.corpora.documents.with_raw_response.chunks_batch_create(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "parent": "parent",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentChunksBatchCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_chunks_batch_create(self, client: RobertTest24) -> None:
        with client.beta.corpora.documents.with_streaming_response.chunks_batch_create(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "parent": "parent",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentChunksBatchCreateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_chunks_batch_create(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.documents.with_raw_response.chunks_batch_create(
                document="document",
                corpus="",
                requests=[
                    {
                        "chunk": {"data": {}},
                        "parent": "parent",
                    }
                ],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.corpora.documents.with_raw_response.chunks_batch_create(
                document="",
                corpus="corpus",
                requests=[
                    {
                        "chunk": {"data": {}},
                        "parent": "parent",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_chunks_batch_delete(self, client: RobertTest24) -> None:
        document = client.beta.corpora.documents.chunks_batch_delete(
            document="document",
            corpus="corpus",
            requests=[{"name": "name"}],
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_chunks_batch_delete_with_all_params(self, client: RobertTest24) -> None:
        document = client.beta.corpora.documents.chunks_batch_delete(
            document="document",
            corpus="corpus",
            requests=[{"name": "name"}],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_chunks_batch_delete(self, client: RobertTest24) -> None:
        response = client.beta.corpora.documents.with_raw_response.chunks_batch_delete(
            document="document",
            corpus="corpus",
            requests=[{"name": "name"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_chunks_batch_delete(self, client: RobertTest24) -> None:
        with client.beta.corpora.documents.with_streaming_response.chunks_batch_delete(
            document="document",
            corpus="corpus",
            requests=[{"name": "name"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_chunks_batch_delete(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.documents.with_raw_response.chunks_batch_delete(
                document="document",
                corpus="",
                requests=[{"name": "name"}],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.corpora.documents.with_raw_response.chunks_batch_delete(
                document="",
                corpus="corpus",
                requests=[{"name": "name"}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_chunks_batch_update(self, client: RobertTest24) -> None:
        document = client.beta.corpora.documents.chunks_batch_update(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "update_mask": "updateMask",
                }
            ],
        )
        assert_matches_type(DocumentChunksBatchUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_chunks_batch_update_with_all_params(self, client: RobertTest24) -> None:
        document = client.beta.corpora.documents.chunks_batch_update(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {
                        "data": {"string_value": "stringValue"},
                        "custom_metadata": [
                            {
                                "key": "key",
                                "numeric_value": 0,
                                "string_list_value": {"values": ["string"]},
                                "string_value": "stringValue",
                            }
                        ],
                        "name": "name",
                    },
                    "update_mask": "updateMask",
                }
            ],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(DocumentChunksBatchUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_chunks_batch_update(self, client: RobertTest24) -> None:
        response = client.beta.corpora.documents.with_raw_response.chunks_batch_update(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "update_mask": "updateMask",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentChunksBatchUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_chunks_batch_update(self, client: RobertTest24) -> None:
        with client.beta.corpora.documents.with_streaming_response.chunks_batch_update(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "update_mask": "updateMask",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentChunksBatchUpdateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_chunks_batch_update(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.documents.with_raw_response.chunks_batch_update(
                document="document",
                corpus="",
                requests=[
                    {
                        "chunk": {"data": {}},
                        "update_mask": "updateMask",
                    }
                ],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.corpora.documents.with_raw_response.chunks_batch_update(
                document="",
                corpus="corpus",
                requests=[
                    {
                        "chunk": {"data": {}},
                        "update_mask": "updateMask",
                    }
                ],
            )


class TestAsyncDocuments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.corpora.documents.update(
            document="document",
            corpus="corpus",
            update_mask="updateMask",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.corpora.documents.update(
            document="document",
            corpus="corpus",
            update_mask="updateMask",
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
            display_name="displayName",
            name="name",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.documents.with_raw_response.update(
            document="document",
            corpus="corpus",
            update_mask="updateMask",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.documents.with_streaming_response.update(
            document="document",
            corpus="corpus",
            update_mask="updateMask",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.documents.with_raw_response.update(
                document="document",
                corpus="",
                update_mask="updateMask",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.corpora.documents.with_raw_response.update(
                document="",
                corpus="corpus",
                update_mask="updateMask",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_chunks_batch_create(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.corpora.documents.chunks_batch_create(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "parent": "parent",
                }
            ],
        )
        assert_matches_type(DocumentChunksBatchCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_chunks_batch_create_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.corpora.documents.chunks_batch_create(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {
                        "data": {"string_value": "stringValue"},
                        "custom_metadata": [
                            {
                                "key": "key",
                                "numeric_value": 0,
                                "string_list_value": {"values": ["string"]},
                                "string_value": "stringValue",
                            }
                        ],
                        "name": "name",
                    },
                    "parent": "parent",
                }
            ],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(DocumentChunksBatchCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_chunks_batch_create(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.documents.with_raw_response.chunks_batch_create(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "parent": "parent",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentChunksBatchCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_chunks_batch_create(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.documents.with_streaming_response.chunks_batch_create(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "parent": "parent",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentChunksBatchCreateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_chunks_batch_create(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.documents.with_raw_response.chunks_batch_create(
                document="document",
                corpus="",
                requests=[
                    {
                        "chunk": {"data": {}},
                        "parent": "parent",
                    }
                ],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.corpora.documents.with_raw_response.chunks_batch_create(
                document="",
                corpus="corpus",
                requests=[
                    {
                        "chunk": {"data": {}},
                        "parent": "parent",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_chunks_batch_delete(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.corpora.documents.chunks_batch_delete(
            document="document",
            corpus="corpus",
            requests=[{"name": "name"}],
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_chunks_batch_delete_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.corpora.documents.chunks_batch_delete(
            document="document",
            corpus="corpus",
            requests=[{"name": "name"}],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_chunks_batch_delete(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.documents.with_raw_response.chunks_batch_delete(
            document="document",
            corpus="corpus",
            requests=[{"name": "name"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_chunks_batch_delete(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.documents.with_streaming_response.chunks_batch_delete(
            document="document",
            corpus="corpus",
            requests=[{"name": "name"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_chunks_batch_delete(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.documents.with_raw_response.chunks_batch_delete(
                document="document",
                corpus="",
                requests=[{"name": "name"}],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.corpora.documents.with_raw_response.chunks_batch_delete(
                document="",
                corpus="corpus",
                requests=[{"name": "name"}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_chunks_batch_update(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.corpora.documents.chunks_batch_update(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "update_mask": "updateMask",
                }
            ],
        )
        assert_matches_type(DocumentChunksBatchUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_chunks_batch_update_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.corpora.documents.chunks_batch_update(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {
                        "data": {"string_value": "stringValue"},
                        "custom_metadata": [
                            {
                                "key": "key",
                                "numeric_value": 0,
                                "string_list_value": {"values": ["string"]},
                                "string_value": "stringValue",
                            }
                        ],
                        "name": "name",
                    },
                    "update_mask": "updateMask",
                }
            ],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(DocumentChunksBatchUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_chunks_batch_update(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.documents.with_raw_response.chunks_batch_update(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "update_mask": "updateMask",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentChunksBatchUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_chunks_batch_update(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.documents.with_streaming_response.chunks_batch_update(
            document="document",
            corpus="corpus",
            requests=[
                {
                    "chunk": {"data": {}},
                    "update_mask": "updateMask",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentChunksBatchUpdateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_chunks_batch_update(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.documents.with_raw_response.chunks_batch_update(
                document="document",
                corpus="",
                requests=[
                    {
                        "chunk": {"data": {}},
                        "update_mask": "updateMask",
                    }
                ],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.corpora.documents.with_raw_response.chunks_batch_update(
                document="",
                corpus="corpus",
                requests=[
                    {
                        "chunk": {"data": {}},
                        "update_mask": "updateMask",
                    }
                ],
            )
