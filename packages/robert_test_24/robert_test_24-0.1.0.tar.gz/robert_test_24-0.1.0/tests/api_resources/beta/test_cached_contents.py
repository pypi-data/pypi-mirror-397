# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24._utils import parse_datetime
from robert_test_24.types.beta import (
    CachedContent,
    CachedContentListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCachedContents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: RobertTest24) -> None:
        cached_content = client.beta.cached_contents.create(
            model="model",
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: RobertTest24) -> None:
        cached_content = client.beta.cached_contents.create(
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            contents=[
                {
                    "parts": [
                        {
                            "code_execution_result": {
                                "outcome": "OUTCOME_UNSPECIFIED",
                                "output": "output",
                            },
                            "executable_code": {
                                "code": "code",
                                "language": "LANGUAGE_UNSPECIFIED",
                            },
                            "file_data": {
                                "file_uri": "fileUri",
                                "mime_type": "mimeType",
                            },
                            "function_call": {
                                "name": "name",
                                "id": "id",
                                "args": {"foo": "bar"},
                            },
                            "function_response": {
                                "name": "name",
                                "response": {"foo": "bar"},
                                "id": "id",
                                "parts": [
                                    {
                                        "inline_data": {
                                            "data": "U3RhaW5sZXNzIHJvY2tz",
                                            "mime_type": "mimeType",
                                        }
                                    }
                                ],
                                "scheduling": "SCHEDULING_UNSPECIFIED",
                                "will_continue": True,
                            },
                            "inline_data": {
                                "data": "U3RhaW5sZXNzIHJvY2tz",
                                "mime_type": "mimeType",
                            },
                            "part_metadata": {"foo": "bar"},
                            "text": "text",
                            "thought": True,
                            "thought_signature": "U3RhaW5sZXNzIHJvY2tz",
                            "video_metadata": {
                                "end_offset": "endOffset",
                                "fps": 0,
                                "start_offset": "startOffset",
                            },
                        }
                    ],
                    "role": "role",
                }
            ],
            display_name="displayName",
            expire_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            system_instruction={
                "parts": [
                    {
                        "code_execution_result": {
                            "outcome": "OUTCOME_UNSPECIFIED",
                            "output": "output",
                        },
                        "executable_code": {
                            "code": "code",
                            "language": "LANGUAGE_UNSPECIFIED",
                        },
                        "file_data": {
                            "file_uri": "fileUri",
                            "mime_type": "mimeType",
                        },
                        "function_call": {
                            "name": "name",
                            "id": "id",
                            "args": {"foo": "bar"},
                        },
                        "function_response": {
                            "name": "name",
                            "response": {"foo": "bar"},
                            "id": "id",
                            "parts": [
                                {
                                    "inline_data": {
                                        "data": "U3RhaW5sZXNzIHJvY2tz",
                                        "mime_type": "mimeType",
                                    }
                                }
                            ],
                            "scheduling": "SCHEDULING_UNSPECIFIED",
                            "will_continue": True,
                        },
                        "inline_data": {
                            "data": "U3RhaW5sZXNzIHJvY2tz",
                            "mime_type": "mimeType",
                        },
                        "part_metadata": {"foo": "bar"},
                        "text": "text",
                        "thought": True,
                        "thought_signature": "U3RhaW5sZXNzIHJvY2tz",
                        "video_metadata": {
                            "end_offset": "endOffset",
                            "fps": 0,
                            "start_offset": "startOffset",
                        },
                    }
                ],
                "role": "role",
            },
            tool_config={
                "function_calling_config": {
                    "allowed_function_names": ["string"],
                    "mode": "MODE_UNSPECIFIED",
                },
                "retrieval_config": {
                    "language_code": "languageCode",
                    "lat_lng": {
                        "latitude": 0,
                        "longitude": 0,
                    },
                },
            },
            tools=[
                {
                    "code_execution": {},
                    "computer_use": {
                        "environment": "ENVIRONMENT_UNSPECIFIED",
                        "excluded_predefined_functions": ["string"],
                    },
                    "file_search": {
                        "retrieval_resources": [{"rag_store_name": "ragStoreName"}],
                        "retrieval_config": {
                            "metadata_filter": "metadataFilter",
                            "top_k": 0,
                        },
                    },
                    "function_declarations": [
                        {
                            "description": "description",
                            "name": "name",
                            "behavior": "UNSPECIFIED",
                            "parameters": {
                                "type": "TYPE_UNSPECIFIED",
                                "any_of": [],
                                "default": {},
                                "description": "description",
                                "enum": ["string"],
                                "example": {},
                                "format": "format",
                                "maximum": 0,
                                "max_items": "maxItems",
                                "max_length": "maxLength",
                                "max_properties": "maxProperties",
                                "minimum": 0,
                                "min_items": "minItems",
                                "min_length": "minLength",
                                "min_properties": "minProperties",
                                "nullable": True,
                                "pattern": "pattern",
                                "properties": {},
                                "property_ordering": ["string"],
                                "required": ["string"],
                                "title": "title",
                            },
                            "parameters_json_schema": {},
                            "response": {
                                "type": "TYPE_UNSPECIFIED",
                                "any_of": [],
                                "default": {},
                                "description": "description",
                                "enum": ["string"],
                                "example": {},
                                "format": "format",
                                "maximum": 0,
                                "max_items": "maxItems",
                                "max_length": "maxLength",
                                "max_properties": "maxProperties",
                                "minimum": 0,
                                "min_items": "minItems",
                                "min_length": "minLength",
                                "min_properties": "minProperties",
                                "nullable": True,
                                "pattern": "pattern",
                                "properties": {},
                                "property_ordering": ["string"],
                                "required": ["string"],
                                "title": "title",
                            },
                            "response_json_schema": {},
                        }
                    ],
                    "google_maps": {"enable_widget": True},
                    "google_search": {
                        "time_range_filter": {
                            "end_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                            "start_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                        }
                    },
                    "google_search_retrieval": {
                        "dynamic_retrieval_config": {
                            "dynamic_threshold": 0,
                            "mode": "MODE_UNSPECIFIED",
                        }
                    },
                    "url_context": {},
                }
            ],
            ttl="ttl",
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: RobertTest24) -> None:
        response = client.beta.cached_contents.with_raw_response.create(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cached_content = response.parse()
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: RobertTest24) -> None:
        with client.beta.cached_contents.with_streaming_response.create(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cached_content = response.parse()
            assert_matches_type(CachedContent, cached_content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: RobertTest24) -> None:
        cached_content = client.beta.cached_contents.retrieve(
            id="id",
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: RobertTest24) -> None:
        cached_content = client.beta.cached_contents.retrieve(
            id="id",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: RobertTest24) -> None:
        response = client.beta.cached_contents.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cached_content = response.parse()
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: RobertTest24) -> None:
        with client.beta.cached_contents.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cached_content = response.parse()
            assert_matches_type(CachedContent, cached_content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.cached_contents.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: RobertTest24) -> None:
        cached_content = client.beta.cached_contents.update(
            id="id",
            model="model",
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: RobertTest24) -> None:
        cached_content = client.beta.cached_contents.update(
            id="id",
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            update_mask="updateMask",
            contents=[
                {
                    "parts": [
                        {
                            "code_execution_result": {
                                "outcome": "OUTCOME_UNSPECIFIED",
                                "output": "output",
                            },
                            "executable_code": {
                                "code": "code",
                                "language": "LANGUAGE_UNSPECIFIED",
                            },
                            "file_data": {
                                "file_uri": "fileUri",
                                "mime_type": "mimeType",
                            },
                            "function_call": {
                                "name": "name",
                                "id": "id",
                                "args": {"foo": "bar"},
                            },
                            "function_response": {
                                "name": "name",
                                "response": {"foo": "bar"},
                                "id": "id",
                                "parts": [
                                    {
                                        "inline_data": {
                                            "data": "U3RhaW5sZXNzIHJvY2tz",
                                            "mime_type": "mimeType",
                                        }
                                    }
                                ],
                                "scheduling": "SCHEDULING_UNSPECIFIED",
                                "will_continue": True,
                            },
                            "inline_data": {
                                "data": "U3RhaW5sZXNzIHJvY2tz",
                                "mime_type": "mimeType",
                            },
                            "part_metadata": {"foo": "bar"},
                            "text": "text",
                            "thought": True,
                            "thought_signature": "U3RhaW5sZXNzIHJvY2tz",
                            "video_metadata": {
                                "end_offset": "endOffset",
                                "fps": 0,
                                "start_offset": "startOffset",
                            },
                        }
                    ],
                    "role": "role",
                }
            ],
            display_name="displayName",
            expire_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            system_instruction={
                "parts": [
                    {
                        "code_execution_result": {
                            "outcome": "OUTCOME_UNSPECIFIED",
                            "output": "output",
                        },
                        "executable_code": {
                            "code": "code",
                            "language": "LANGUAGE_UNSPECIFIED",
                        },
                        "file_data": {
                            "file_uri": "fileUri",
                            "mime_type": "mimeType",
                        },
                        "function_call": {
                            "name": "name",
                            "id": "id",
                            "args": {"foo": "bar"},
                        },
                        "function_response": {
                            "name": "name",
                            "response": {"foo": "bar"},
                            "id": "id",
                            "parts": [
                                {
                                    "inline_data": {
                                        "data": "U3RhaW5sZXNzIHJvY2tz",
                                        "mime_type": "mimeType",
                                    }
                                }
                            ],
                            "scheduling": "SCHEDULING_UNSPECIFIED",
                            "will_continue": True,
                        },
                        "inline_data": {
                            "data": "U3RhaW5sZXNzIHJvY2tz",
                            "mime_type": "mimeType",
                        },
                        "part_metadata": {"foo": "bar"},
                        "text": "text",
                        "thought": True,
                        "thought_signature": "U3RhaW5sZXNzIHJvY2tz",
                        "video_metadata": {
                            "end_offset": "endOffset",
                            "fps": 0,
                            "start_offset": "startOffset",
                        },
                    }
                ],
                "role": "role",
            },
            tool_config={
                "function_calling_config": {
                    "allowed_function_names": ["string"],
                    "mode": "MODE_UNSPECIFIED",
                },
                "retrieval_config": {
                    "language_code": "languageCode",
                    "lat_lng": {
                        "latitude": 0,
                        "longitude": 0,
                    },
                },
            },
            tools=[
                {
                    "code_execution": {},
                    "computer_use": {
                        "environment": "ENVIRONMENT_UNSPECIFIED",
                        "excluded_predefined_functions": ["string"],
                    },
                    "file_search": {
                        "retrieval_resources": [{"rag_store_name": "ragStoreName"}],
                        "retrieval_config": {
                            "metadata_filter": "metadataFilter",
                            "top_k": 0,
                        },
                    },
                    "function_declarations": [
                        {
                            "description": "description",
                            "name": "name",
                            "behavior": "UNSPECIFIED",
                            "parameters": {
                                "type": "TYPE_UNSPECIFIED",
                                "any_of": [],
                                "default": {},
                                "description": "description",
                                "enum": ["string"],
                                "example": {},
                                "format": "format",
                                "maximum": 0,
                                "max_items": "maxItems",
                                "max_length": "maxLength",
                                "max_properties": "maxProperties",
                                "minimum": 0,
                                "min_items": "minItems",
                                "min_length": "minLength",
                                "min_properties": "minProperties",
                                "nullable": True,
                                "pattern": "pattern",
                                "properties": {},
                                "property_ordering": ["string"],
                                "required": ["string"],
                                "title": "title",
                            },
                            "parameters_json_schema": {},
                            "response": {
                                "type": "TYPE_UNSPECIFIED",
                                "any_of": [],
                                "default": {},
                                "description": "description",
                                "enum": ["string"],
                                "example": {},
                                "format": "format",
                                "maximum": 0,
                                "max_items": "maxItems",
                                "max_length": "maxLength",
                                "max_properties": "maxProperties",
                                "minimum": 0,
                                "min_items": "minItems",
                                "min_length": "minLength",
                                "min_properties": "minProperties",
                                "nullable": True,
                                "pattern": "pattern",
                                "properties": {},
                                "property_ordering": ["string"],
                                "required": ["string"],
                                "title": "title",
                            },
                            "response_json_schema": {},
                        }
                    ],
                    "google_maps": {"enable_widget": True},
                    "google_search": {
                        "time_range_filter": {
                            "end_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                            "start_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                        }
                    },
                    "google_search_retrieval": {
                        "dynamic_retrieval_config": {
                            "dynamic_threshold": 0,
                            "mode": "MODE_UNSPECIFIED",
                        }
                    },
                    "url_context": {},
                }
            ],
            ttl="ttl",
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: RobertTest24) -> None:
        response = client.beta.cached_contents.with_raw_response.update(
            id="id",
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cached_content = response.parse()
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: RobertTest24) -> None:
        with client.beta.cached_contents.with_streaming_response.update(
            id="id",
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cached_content = response.parse()
            assert_matches_type(CachedContent, cached_content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.cached_contents.with_raw_response.update(
                id="",
                model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: RobertTest24) -> None:
        cached_content = client.beta.cached_contents.list()
        assert_matches_type(CachedContentListResponse, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: RobertTest24) -> None:
        cached_content = client.beta.cached_contents.list(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(CachedContentListResponse, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: RobertTest24) -> None:
        response = client.beta.cached_contents.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cached_content = response.parse()
        assert_matches_type(CachedContentListResponse, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: RobertTest24) -> None:
        with client.beta.cached_contents.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cached_content = response.parse()
            assert_matches_type(CachedContentListResponse, cached_content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: RobertTest24) -> None:
        cached_content = client.beta.cached_contents.delete(
            id="id",
        )
        assert_matches_type(object, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: RobertTest24) -> None:
        cached_content = client.beta.cached_contents.delete(
            id="id",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: RobertTest24) -> None:
        response = client.beta.cached_contents.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cached_content = response.parse()
        assert_matches_type(object, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: RobertTest24) -> None:
        with client.beta.cached_contents.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cached_content = response.parse()
            assert_matches_type(object, cached_content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.cached_contents.with_raw_response.delete(
                id="",
            )


class TestAsyncCachedContents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRobertTest24) -> None:
        cached_content = await async_client.beta.cached_contents.create(
            model="model",
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        cached_content = await async_client.beta.cached_contents.create(
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            contents=[
                {
                    "parts": [
                        {
                            "code_execution_result": {
                                "outcome": "OUTCOME_UNSPECIFIED",
                                "output": "output",
                            },
                            "executable_code": {
                                "code": "code",
                                "language": "LANGUAGE_UNSPECIFIED",
                            },
                            "file_data": {
                                "file_uri": "fileUri",
                                "mime_type": "mimeType",
                            },
                            "function_call": {
                                "name": "name",
                                "id": "id",
                                "args": {"foo": "bar"},
                            },
                            "function_response": {
                                "name": "name",
                                "response": {"foo": "bar"},
                                "id": "id",
                                "parts": [
                                    {
                                        "inline_data": {
                                            "data": "U3RhaW5sZXNzIHJvY2tz",
                                            "mime_type": "mimeType",
                                        }
                                    }
                                ],
                                "scheduling": "SCHEDULING_UNSPECIFIED",
                                "will_continue": True,
                            },
                            "inline_data": {
                                "data": "U3RhaW5sZXNzIHJvY2tz",
                                "mime_type": "mimeType",
                            },
                            "part_metadata": {"foo": "bar"},
                            "text": "text",
                            "thought": True,
                            "thought_signature": "U3RhaW5sZXNzIHJvY2tz",
                            "video_metadata": {
                                "end_offset": "endOffset",
                                "fps": 0,
                                "start_offset": "startOffset",
                            },
                        }
                    ],
                    "role": "role",
                }
            ],
            display_name="displayName",
            expire_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            system_instruction={
                "parts": [
                    {
                        "code_execution_result": {
                            "outcome": "OUTCOME_UNSPECIFIED",
                            "output": "output",
                        },
                        "executable_code": {
                            "code": "code",
                            "language": "LANGUAGE_UNSPECIFIED",
                        },
                        "file_data": {
                            "file_uri": "fileUri",
                            "mime_type": "mimeType",
                        },
                        "function_call": {
                            "name": "name",
                            "id": "id",
                            "args": {"foo": "bar"},
                        },
                        "function_response": {
                            "name": "name",
                            "response": {"foo": "bar"},
                            "id": "id",
                            "parts": [
                                {
                                    "inline_data": {
                                        "data": "U3RhaW5sZXNzIHJvY2tz",
                                        "mime_type": "mimeType",
                                    }
                                }
                            ],
                            "scheduling": "SCHEDULING_UNSPECIFIED",
                            "will_continue": True,
                        },
                        "inline_data": {
                            "data": "U3RhaW5sZXNzIHJvY2tz",
                            "mime_type": "mimeType",
                        },
                        "part_metadata": {"foo": "bar"},
                        "text": "text",
                        "thought": True,
                        "thought_signature": "U3RhaW5sZXNzIHJvY2tz",
                        "video_metadata": {
                            "end_offset": "endOffset",
                            "fps": 0,
                            "start_offset": "startOffset",
                        },
                    }
                ],
                "role": "role",
            },
            tool_config={
                "function_calling_config": {
                    "allowed_function_names": ["string"],
                    "mode": "MODE_UNSPECIFIED",
                },
                "retrieval_config": {
                    "language_code": "languageCode",
                    "lat_lng": {
                        "latitude": 0,
                        "longitude": 0,
                    },
                },
            },
            tools=[
                {
                    "code_execution": {},
                    "computer_use": {
                        "environment": "ENVIRONMENT_UNSPECIFIED",
                        "excluded_predefined_functions": ["string"],
                    },
                    "file_search": {
                        "retrieval_resources": [{"rag_store_name": "ragStoreName"}],
                        "retrieval_config": {
                            "metadata_filter": "metadataFilter",
                            "top_k": 0,
                        },
                    },
                    "function_declarations": [
                        {
                            "description": "description",
                            "name": "name",
                            "behavior": "UNSPECIFIED",
                            "parameters": {
                                "type": "TYPE_UNSPECIFIED",
                                "any_of": [],
                                "default": {},
                                "description": "description",
                                "enum": ["string"],
                                "example": {},
                                "format": "format",
                                "maximum": 0,
                                "max_items": "maxItems",
                                "max_length": "maxLength",
                                "max_properties": "maxProperties",
                                "minimum": 0,
                                "min_items": "minItems",
                                "min_length": "minLength",
                                "min_properties": "minProperties",
                                "nullable": True,
                                "pattern": "pattern",
                                "properties": {},
                                "property_ordering": ["string"],
                                "required": ["string"],
                                "title": "title",
                            },
                            "parameters_json_schema": {},
                            "response": {
                                "type": "TYPE_UNSPECIFIED",
                                "any_of": [],
                                "default": {},
                                "description": "description",
                                "enum": ["string"],
                                "example": {},
                                "format": "format",
                                "maximum": 0,
                                "max_items": "maxItems",
                                "max_length": "maxLength",
                                "max_properties": "maxProperties",
                                "minimum": 0,
                                "min_items": "minItems",
                                "min_length": "minLength",
                                "min_properties": "minProperties",
                                "nullable": True,
                                "pattern": "pattern",
                                "properties": {},
                                "property_ordering": ["string"],
                                "required": ["string"],
                                "title": "title",
                            },
                            "response_json_schema": {},
                        }
                    ],
                    "google_maps": {"enable_widget": True},
                    "google_search": {
                        "time_range_filter": {
                            "end_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                            "start_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                        }
                    },
                    "google_search_retrieval": {
                        "dynamic_retrieval_config": {
                            "dynamic_threshold": 0,
                            "mode": "MODE_UNSPECIFIED",
                        }
                    },
                    "url_context": {},
                }
            ],
            ttl="ttl",
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.cached_contents.with_raw_response.create(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cached_content = await response.parse()
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.cached_contents.with_streaming_response.create(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cached_content = await response.parse()
            assert_matches_type(CachedContent, cached_content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRobertTest24) -> None:
        cached_content = await async_client.beta.cached_contents.retrieve(
            id="id",
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        cached_content = await async_client.beta.cached_contents.retrieve(
            id="id",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.cached_contents.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cached_content = await response.parse()
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.cached_contents.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cached_content = await response.parse()
            assert_matches_type(CachedContent, cached_content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.cached_contents.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncRobertTest24) -> None:
        cached_content = await async_client.beta.cached_contents.update(
            id="id",
            model="model",
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        cached_content = await async_client.beta.cached_contents.update(
            id="id",
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            update_mask="updateMask",
            contents=[
                {
                    "parts": [
                        {
                            "code_execution_result": {
                                "outcome": "OUTCOME_UNSPECIFIED",
                                "output": "output",
                            },
                            "executable_code": {
                                "code": "code",
                                "language": "LANGUAGE_UNSPECIFIED",
                            },
                            "file_data": {
                                "file_uri": "fileUri",
                                "mime_type": "mimeType",
                            },
                            "function_call": {
                                "name": "name",
                                "id": "id",
                                "args": {"foo": "bar"},
                            },
                            "function_response": {
                                "name": "name",
                                "response": {"foo": "bar"},
                                "id": "id",
                                "parts": [
                                    {
                                        "inline_data": {
                                            "data": "U3RhaW5sZXNzIHJvY2tz",
                                            "mime_type": "mimeType",
                                        }
                                    }
                                ],
                                "scheduling": "SCHEDULING_UNSPECIFIED",
                                "will_continue": True,
                            },
                            "inline_data": {
                                "data": "U3RhaW5sZXNzIHJvY2tz",
                                "mime_type": "mimeType",
                            },
                            "part_metadata": {"foo": "bar"},
                            "text": "text",
                            "thought": True,
                            "thought_signature": "U3RhaW5sZXNzIHJvY2tz",
                            "video_metadata": {
                                "end_offset": "endOffset",
                                "fps": 0,
                                "start_offset": "startOffset",
                            },
                        }
                    ],
                    "role": "role",
                }
            ],
            display_name="displayName",
            expire_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            system_instruction={
                "parts": [
                    {
                        "code_execution_result": {
                            "outcome": "OUTCOME_UNSPECIFIED",
                            "output": "output",
                        },
                        "executable_code": {
                            "code": "code",
                            "language": "LANGUAGE_UNSPECIFIED",
                        },
                        "file_data": {
                            "file_uri": "fileUri",
                            "mime_type": "mimeType",
                        },
                        "function_call": {
                            "name": "name",
                            "id": "id",
                            "args": {"foo": "bar"},
                        },
                        "function_response": {
                            "name": "name",
                            "response": {"foo": "bar"},
                            "id": "id",
                            "parts": [
                                {
                                    "inline_data": {
                                        "data": "U3RhaW5sZXNzIHJvY2tz",
                                        "mime_type": "mimeType",
                                    }
                                }
                            ],
                            "scheduling": "SCHEDULING_UNSPECIFIED",
                            "will_continue": True,
                        },
                        "inline_data": {
                            "data": "U3RhaW5sZXNzIHJvY2tz",
                            "mime_type": "mimeType",
                        },
                        "part_metadata": {"foo": "bar"},
                        "text": "text",
                        "thought": True,
                        "thought_signature": "U3RhaW5sZXNzIHJvY2tz",
                        "video_metadata": {
                            "end_offset": "endOffset",
                            "fps": 0,
                            "start_offset": "startOffset",
                        },
                    }
                ],
                "role": "role",
            },
            tool_config={
                "function_calling_config": {
                    "allowed_function_names": ["string"],
                    "mode": "MODE_UNSPECIFIED",
                },
                "retrieval_config": {
                    "language_code": "languageCode",
                    "lat_lng": {
                        "latitude": 0,
                        "longitude": 0,
                    },
                },
            },
            tools=[
                {
                    "code_execution": {},
                    "computer_use": {
                        "environment": "ENVIRONMENT_UNSPECIFIED",
                        "excluded_predefined_functions": ["string"],
                    },
                    "file_search": {
                        "retrieval_resources": [{"rag_store_name": "ragStoreName"}],
                        "retrieval_config": {
                            "metadata_filter": "metadataFilter",
                            "top_k": 0,
                        },
                    },
                    "function_declarations": [
                        {
                            "description": "description",
                            "name": "name",
                            "behavior": "UNSPECIFIED",
                            "parameters": {
                                "type": "TYPE_UNSPECIFIED",
                                "any_of": [],
                                "default": {},
                                "description": "description",
                                "enum": ["string"],
                                "example": {},
                                "format": "format",
                                "maximum": 0,
                                "max_items": "maxItems",
                                "max_length": "maxLength",
                                "max_properties": "maxProperties",
                                "minimum": 0,
                                "min_items": "minItems",
                                "min_length": "minLength",
                                "min_properties": "minProperties",
                                "nullable": True,
                                "pattern": "pattern",
                                "properties": {},
                                "property_ordering": ["string"],
                                "required": ["string"],
                                "title": "title",
                            },
                            "parameters_json_schema": {},
                            "response": {
                                "type": "TYPE_UNSPECIFIED",
                                "any_of": [],
                                "default": {},
                                "description": "description",
                                "enum": ["string"],
                                "example": {},
                                "format": "format",
                                "maximum": 0,
                                "max_items": "maxItems",
                                "max_length": "maxLength",
                                "max_properties": "maxProperties",
                                "minimum": 0,
                                "min_items": "minItems",
                                "min_length": "minLength",
                                "min_properties": "minProperties",
                                "nullable": True,
                                "pattern": "pattern",
                                "properties": {},
                                "property_ordering": ["string"],
                                "required": ["string"],
                                "title": "title",
                            },
                            "response_json_schema": {},
                        }
                    ],
                    "google_maps": {"enable_widget": True},
                    "google_search": {
                        "time_range_filter": {
                            "end_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                            "start_time": parse_datetime("2019-12-27T18:11:19.117Z"),
                        }
                    },
                    "google_search_retrieval": {
                        "dynamic_retrieval_config": {
                            "dynamic_threshold": 0,
                            "mode": "MODE_UNSPECIFIED",
                        }
                    },
                    "url_context": {},
                }
            ],
            ttl="ttl",
        )
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.cached_contents.with_raw_response.update(
            id="id",
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cached_content = await response.parse()
        assert_matches_type(CachedContent, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.cached_contents.with_streaming_response.update(
            id="id",
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cached_content = await response.parse()
            assert_matches_type(CachedContent, cached_content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.cached_contents.with_raw_response.update(
                id="",
                model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRobertTest24) -> None:
        cached_content = await async_client.beta.cached_contents.list()
        assert_matches_type(CachedContentListResponse, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        cached_content = await async_client.beta.cached_contents.list(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(CachedContentListResponse, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.cached_contents.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cached_content = await response.parse()
        assert_matches_type(CachedContentListResponse, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.cached_contents.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cached_content = await response.parse()
            assert_matches_type(CachedContentListResponse, cached_content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRobertTest24) -> None:
        cached_content = await async_client.beta.cached_contents.delete(
            id="id",
        )
        assert_matches_type(object, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        cached_content = await async_client.beta.cached_contents.delete(
            id="id",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(object, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.cached_contents.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cached_content = await response.parse()
        assert_matches_type(object, cached_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.cached_contents.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cached_content = await response.parse()
            assert_matches_type(object, cached_content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.cached_contents.with_raw_response.delete(
                id="",
            )
