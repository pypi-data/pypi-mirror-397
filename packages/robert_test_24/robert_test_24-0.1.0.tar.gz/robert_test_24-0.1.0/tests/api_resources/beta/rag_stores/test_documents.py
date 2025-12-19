# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta.rag_stores import (
    Document,
    DocumentListResponse,
    DocumentQueryResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocuments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: RobertTest24) -> None:
        document = client.beta.rag_stores.documents.create(
            rag_store="ragStore",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: RobertTest24) -> None:
        document = client.beta.rag_stores.documents.create(
            rag_store="ragStore",
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
    def test_raw_response_create(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.documents.with_raw_response.create(
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.documents.with_streaming_response.create(
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            client.beta.rag_stores.documents.with_raw_response.create(
                rag_store="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: RobertTest24) -> None:
        document = client.beta.rag_stores.documents.retrieve(
            document="document",
            rag_store="ragStore",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: RobertTest24) -> None:
        document = client.beta.rag_stores.documents.retrieve(
            document="document",
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.documents.with_raw_response.retrieve(
            document="document",
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.documents.with_streaming_response.retrieve(
            document="document",
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            client.beta.rag_stores.documents.with_raw_response.retrieve(
                document="document",
                rag_store="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.rag_stores.documents.with_raw_response.retrieve(
                document="",
                rag_store="ragStore",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: RobertTest24) -> None:
        document = client.beta.rag_stores.documents.list(
            rag_store="ragStore",
        )
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: RobertTest24) -> None:
        document = client.beta.rag_stores.documents.list(
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.documents.with_raw_response.list(
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.documents.with_streaming_response.list(
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentListResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            client.beta.rag_stores.documents.with_raw_response.list(
                rag_store="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: RobertTest24) -> None:
        document = client.beta.rag_stores.documents.delete(
            document="document",
            rag_store="ragStore",
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: RobertTest24) -> None:
        document = client.beta.rag_stores.documents.delete(
            document="document",
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            force=True,
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.documents.with_raw_response.delete(
            document="document",
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.documents.with_streaming_response.delete(
            document="document",
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            client.beta.rag_stores.documents.with_raw_response.delete(
                document="document",
                rag_store="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.rag_stores.documents.with_raw_response.delete(
                document="",
                rag_store="ragStore",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_query(self, client: RobertTest24) -> None:
        document = client.beta.rag_stores.documents.query(
            document="document",
            rag_store="ragStore",
            query="query",
        )
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_query_with_all_params(self, client: RobertTest24) -> None:
        document = client.beta.rag_stores.documents.query(
            document="document",
            rag_store="ragStore",
            query="query",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            metadata_filters=[
                {
                    "conditions": [
                        {
                            "operation": "OPERATOR_UNSPECIFIED",
                            "numeric_value": 0,
                            "string_value": "stringValue",
                        }
                    ],
                    "key": "key",
                }
            ],
            results_count=0,
        )
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_query(self, client: RobertTest24) -> None:
        response = client.beta.rag_stores.documents.with_raw_response.query(
            document="document",
            rag_store="ragStore",
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_query(self, client: RobertTest24) -> None:
        with client.beta.rag_stores.documents.with_streaming_response.query(
            document="document",
            rag_store="ragStore",
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentQueryResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_query(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            client.beta.rag_stores.documents.with_raw_response.query(
                document="document",
                rag_store="",
                query="query",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            client.beta.rag_stores.documents.with_raw_response.query(
                document="",
                rag_store="ragStore",
                query="query",
            )


class TestAsyncDocuments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.rag_stores.documents.create(
            rag_store="ragStore",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.rag_stores.documents.create(
            rag_store="ragStore",
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
    async def test_raw_response_create(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.documents.with_raw_response.create(
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.documents.with_streaming_response.create(
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            await async_client.beta.rag_stores.documents.with_raw_response.create(
                rag_store="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.rag_stores.documents.retrieve(
            document="document",
            rag_store="ragStore",
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.rag_stores.documents.retrieve(
            document="document",
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.documents.with_raw_response.retrieve(
            document="document",
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(Document, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.documents.with_streaming_response.retrieve(
            document="document",
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(Document, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            await async_client.beta.rag_stores.documents.with_raw_response.retrieve(
                document="document",
                rag_store="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.rag_stores.documents.with_raw_response.retrieve(
                document="",
                rag_store="ragStore",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.rag_stores.documents.list(
            rag_store="ragStore",
        )
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.rag_stores.documents.list(
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.documents.with_raw_response.list(
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.documents.with_streaming_response.list(
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentListResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            await async_client.beta.rag_stores.documents.with_raw_response.list(
                rag_store="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.rag_stores.documents.delete(
            document="document",
            rag_store="ragStore",
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.rag_stores.documents.delete(
            document="document",
            rag_store="ragStore",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            force=True,
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.documents.with_raw_response.delete(
            document="document",
            rag_store="ragStore",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.documents.with_streaming_response.delete(
            document="document",
            rag_store="ragStore",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            await async_client.beta.rag_stores.documents.with_raw_response.delete(
                document="document",
                rag_store="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.rag_stores.documents.with_raw_response.delete(
                document="",
                rag_store="ragStore",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_query(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.rag_stores.documents.query(
            document="document",
            rag_store="ragStore",
            query="query",
        )
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_query_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        document = await async_client.beta.rag_stores.documents.query(
            document="document",
            rag_store="ragStore",
            query="query",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            metadata_filters=[
                {
                    "conditions": [
                        {
                            "operation": "OPERATOR_UNSPECIFIED",
                            "numeric_value": 0,
                            "string_value": "stringValue",
                        }
                    ],
                    "key": "key",
                }
            ],
            results_count=0,
        )
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_query(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.rag_stores.documents.with_raw_response.query(
            document="document",
            rag_store="ragStore",
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentQueryResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_query(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.rag_stores.documents.with_streaming_response.query(
            document="document",
            rag_store="ragStore",
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentQueryResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_query(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rag_store` but received ''"):
            await async_client.beta.rag_stores.documents.with_raw_response.query(
                document="document",
                rag_store="",
                query="query",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document` but received ''"):
            await async_client.beta.rag_stores.documents.with_raw_response.query(
                document="",
                rag_store="ragStore",
                query="query",
            )
