# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24.types.beta import (
    Corpus,
    Operation,
    CorporaListResponse,
    CorporaCorpusQueryResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCorpora:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.create()
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.create(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            display_name="displayName",
        )
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: RobertTest24) -> None:
        response = client.beta.corpora.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = response.parse()
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: RobertTest24) -> None:
        with client.beta.corpora.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = response.parse()
            assert_matches_type(Corpus, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.retrieve(
            operation="operation",
            corpus="corpus",
        )
        assert_matches_type(Operation, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.retrieve(
            operation="operation",
            corpus="corpus",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Operation, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: RobertTest24) -> None:
        response = client.beta.corpora.with_raw_response.retrieve(
            operation="operation",
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = response.parse()
        assert_matches_type(Operation, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: RobertTest24) -> None:
        with client.beta.corpora.with_streaming_response.retrieve(
            operation="operation",
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = response.parse()
            assert_matches_type(Operation, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.with_raw_response.retrieve(
                operation="operation",
                corpus="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation` but received ''"):
            client.beta.corpora.with_raw_response.retrieve(
                operation="",
                corpus="corpus",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.update(
            corpus="corpus",
            update_mask="updateMask",
        )
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.update(
            corpus="corpus",
            update_mask="updateMask",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            display_name="displayName",
        )
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: RobertTest24) -> None:
        response = client.beta.corpora.with_raw_response.update(
            corpus="corpus",
            update_mask="updateMask",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = response.parse()
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: RobertTest24) -> None:
        with client.beta.corpora.with_streaming_response.update(
            corpus="corpus",
            update_mask="updateMask",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = response.parse()
            assert_matches_type(Corpus, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.with_raw_response.update(
                corpus="",
                update_mask="updateMask",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.list()
        assert_matches_type(CorporaListResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.list(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(CorporaListResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: RobertTest24) -> None:
        response = client.beta.corpora.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = response.parse()
        assert_matches_type(CorporaListResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: RobertTest24) -> None:
        with client.beta.corpora.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = response.parse()
            assert_matches_type(CorporaListResponse, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.delete(
            corpus="corpus",
        )
        assert_matches_type(object, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.delete(
            corpus="corpus",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            force=True,
        )
        assert_matches_type(object, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: RobertTest24) -> None:
        response = client.beta.corpora.with_raw_response.delete(
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = response.parse()
        assert_matches_type(object, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: RobertTest24) -> None:
        with client.beta.corpora.with_streaming_response.delete(
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = response.parse()
            assert_matches_type(object, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.with_raw_response.delete(
                corpus="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_corpus_query(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.corpus_query(
            corpus="corpus",
            query="query",
        )
        assert_matches_type(CorporaCorpusQueryResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_corpus_query_with_all_params(self, client: RobertTest24) -> None:
        corpora = client.beta.corpora.corpus_query(
            corpus="corpus",
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
        assert_matches_type(CorporaCorpusQueryResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_corpus_query(self, client: RobertTest24) -> None:
        response = client.beta.corpora.with_raw_response.corpus_query(
            corpus="corpus",
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = response.parse()
        assert_matches_type(CorporaCorpusQueryResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_corpus_query(self, client: RobertTest24) -> None:
        with client.beta.corpora.with_streaming_response.corpus_query(
            corpus="corpus",
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = response.parse()
            assert_matches_type(CorporaCorpusQueryResponse, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_corpus_query(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            client.beta.corpora.with_raw_response.corpus_query(
                corpus="",
                query="query",
            )


class TestAsyncCorpora:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.create()
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.create(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            display_name="displayName",
        )
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = await response.parse()
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = await response.parse()
            assert_matches_type(Corpus, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.retrieve(
            operation="operation",
            corpus="corpus",
        )
        assert_matches_type(Operation, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.retrieve(
            operation="operation",
            corpus="corpus",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Operation, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.with_raw_response.retrieve(
            operation="operation",
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = await response.parse()
        assert_matches_type(Operation, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.with_streaming_response.retrieve(
            operation="operation",
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = await response.parse()
            assert_matches_type(Operation, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.with_raw_response.retrieve(
                operation="operation",
                corpus="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation` but received ''"):
            await async_client.beta.corpora.with_raw_response.retrieve(
                operation="",
                corpus="corpus",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.update(
            corpus="corpus",
            update_mask="updateMask",
        )
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.update(
            corpus="corpus",
            update_mask="updateMask",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            display_name="displayName",
        )
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.with_raw_response.update(
            corpus="corpus",
            update_mask="updateMask",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = await response.parse()
        assert_matches_type(Corpus, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.with_streaming_response.update(
            corpus="corpus",
            update_mask="updateMask",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = await response.parse()
            assert_matches_type(Corpus, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.with_raw_response.update(
                corpus="",
                update_mask="updateMask",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.list()
        assert_matches_type(CorporaListResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.list(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(CorporaListResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = await response.parse()
        assert_matches_type(CorporaListResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = await response.parse()
            assert_matches_type(CorporaListResponse, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.delete(
            corpus="corpus",
        )
        assert_matches_type(object, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.delete(
            corpus="corpus",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            force=True,
        )
        assert_matches_type(object, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.with_raw_response.delete(
            corpus="corpus",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = await response.parse()
        assert_matches_type(object, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.with_streaming_response.delete(
            corpus="corpus",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = await response.parse()
            assert_matches_type(object, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.with_raw_response.delete(
                corpus="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_corpus_query(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.corpus_query(
            corpus="corpus",
            query="query",
        )
        assert_matches_type(CorporaCorpusQueryResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_corpus_query_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        corpora = await async_client.beta.corpora.corpus_query(
            corpus="corpus",
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
        assert_matches_type(CorporaCorpusQueryResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_corpus_query(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.corpora.with_raw_response.corpus_query(
            corpus="corpus",
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        corpora = await response.parse()
        assert_matches_type(CorporaCorpusQueryResponse, corpora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_corpus_query(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.corpora.with_streaming_response.corpus_query(
            corpus="corpus",
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            corpora = await response.parse()
            assert_matches_type(CorporaCorpusQueryResponse, corpora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_corpus_query(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `corpus` but received ''"):
            await async_client.beta.corpora.with_raw_response.corpus_query(
                corpus="",
                query="query",
            )
