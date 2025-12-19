# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24._utils import parse_datetime
from robert_test_24.types.beta import (
    Model,
    GenerateText,
    ModelListResponse,
    EmbedContentResponse,
    ModelPredictResponse,
    ModelEmbedTextResponse,
    GenerateContentResponse,
    ModelCountTokensResponse,
    ModelBatchEmbedTextResponse,
    ModelGenerateAnswerResponse,
    ModelCountTextTokensResponse,
    ModelGenerateMessageResponse,
    BatchGenerateContentOperation,
    AsyncBatchEmbedContentOperation,
    ModelBatchEmbedContentsResponse,
    ModelCountMessageTokensResponse,
    ModelPredictLongRunningResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestModels:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: RobertTest24) -> None:
        model = client.beta.models.retrieve(
            model="model",
        )
        assert_matches_type(Model, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.retrieve(
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Model, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.retrieve(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(Model, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.retrieve(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(Model, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.retrieve(
                model="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: RobertTest24) -> None:
        model = client.beta.models.list()
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.list(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelListResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_async_batch_embed_content(self, client: RobertTest24) -> None:
        model = client.beta.models.async_batch_embed_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        )
        assert_matches_type(AsyncBatchEmbedContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_async_batch_embed_content_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.async_batch_embed_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {
                    "file_name": "fileName",
                    "requests": {
                        "requests": [
                            {
                                "request": {
                                    "content": {
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
                                    "model": "model",
                                    "output_dimensionality": 0,
                                    "task_type": "TASK_TYPE_UNSPECIFIED",
                                    "title": "title",
                                },
                                "metadata": {"foo": "bar"},
                            }
                        ]
                    },
                },
                "model": "model",
                "priority": "priority",
            },
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(AsyncBatchEmbedContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_async_batch_embed_content(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.async_batch_embed_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(AsyncBatchEmbedContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_async_batch_embed_content(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.async_batch_embed_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(AsyncBatchEmbedContentOperation, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_async_batch_embed_content(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.async_batch_embed_content(
                model="",
                batch={
                    "display_name": "displayName",
                    "input_config": {},
                    "model": "model",
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_embed_contents(self, client: RobertTest24) -> None:
        model = client.beta.models.batch_embed_contents(
            model="model",
            requests=[
                {
                    "content": {},
                    "model": "model",
                }
            ],
        )
        assert_matches_type(ModelBatchEmbedContentsResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_embed_contents_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.batch_embed_contents(
            model="model",
            requests=[
                {
                    "content": {
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
                    "model": "model",
                    "output_dimensionality": 0,
                    "task_type": "TASK_TYPE_UNSPECIFIED",
                    "title": "title",
                }
            ],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(ModelBatchEmbedContentsResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_batch_embed_contents(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.batch_embed_contents(
            model="model",
            requests=[
                {
                    "content": {},
                    "model": "model",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelBatchEmbedContentsResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_batch_embed_contents(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.batch_embed_contents(
            model="model",
            requests=[
                {
                    "content": {},
                    "model": "model",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelBatchEmbedContentsResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_batch_embed_contents(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.batch_embed_contents(
                model="",
                requests=[
                    {
                        "content": {},
                        "model": "model",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_embed_text(self, client: RobertTest24) -> None:
        model = client.beta.models.batch_embed_text(
            model="model",
        )
        assert_matches_type(ModelBatchEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_embed_text_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.batch_embed_text(
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            requests=[
                {
                    "model": "model",
                    "text": "text",
                }
            ],
            texts=["string"],
        )
        assert_matches_type(ModelBatchEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_batch_embed_text(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.batch_embed_text(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelBatchEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_batch_embed_text(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.batch_embed_text(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelBatchEmbedTextResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_batch_embed_text(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.batch_embed_text(
                model="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_generate_content(self, client: RobertTest24) -> None:
        model = client.beta.models.batch_generate_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        )
        assert_matches_type(BatchGenerateContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_generate_content_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.batch_generate_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {
                    "file_name": "fileName",
                    "requests": {
                        "requests": [
                            {
                                "request": {
                                    "contents": [
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
                                    "model": "model",
                                    "cached_content": "cachedContent",
                                    "generation_config": {
                                        "_response_json_schema": {},
                                        "candidate_count": 0,
                                        "enable_enhanced_civic_answers": True,
                                        "frequency_penalty": 0,
                                        "image_config": {"aspect_ratio": "aspectRatio"},
                                        "logprobs": 0,
                                        "max_output_tokens": 0,
                                        "media_resolution": "MEDIA_RESOLUTION_UNSPECIFIED",
                                        "presence_penalty": 0,
                                        "response_json_schema": {},
                                        "response_logprobs": True,
                                        "response_mime_type": "responseMimeType",
                                        "response_modalities": ["MODALITY_UNSPECIFIED"],
                                        "response_schema": {
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
                                        "seed": 0,
                                        "speech_config": {
                                            "language_code": "languageCode",
                                            "multi_speaker_voice_config": {
                                                "speaker_voice_configs": [
                                                    {
                                                        "speaker": "speaker",
                                                        "voice_config": {
                                                            "prebuilt_voice_config": {"voice_name": "voiceName"}
                                                        },
                                                    }
                                                ]
                                            },
                                            "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                                        },
                                        "stop_sequences": ["string"],
                                        "temperature": 0,
                                        "thinking_config": {
                                            "include_thoughts": True,
                                            "thinking_budget": 0,
                                        },
                                        "top_k": 0,
                                        "top_p": 0,
                                    },
                                    "safety_settings": [
                                        {
                                            "category": "HARM_CATEGORY_UNSPECIFIED",
                                            "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                                        }
                                    ],
                                    "system_instruction": {
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
                                    "tool_config": {
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
                                    "tools": [
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
                                },
                                "metadata": {"foo": "bar"},
                            }
                        ]
                    },
                },
                "model": "model",
                "priority": "priority",
            },
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(BatchGenerateContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_batch_generate_content(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.batch_generate_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(BatchGenerateContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_batch_generate_content(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.batch_generate_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(BatchGenerateContentOperation, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_batch_generate_content(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.batch_generate_content(
                model="",
                batch={
                    "display_name": "displayName",
                    "input_config": {},
                    "model": "model",
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_count_message_tokens(self, client: RobertTest24) -> None:
        model = client.beta.models.count_message_tokens(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        )
        assert_matches_type(ModelCountMessageTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_count_message_tokens_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.count_message_tokens(
            model="model",
            prompt={
                "messages": [
                    {
                        "content": "content",
                        "author": "author",
                    }
                ],
                "context": "context",
                "examples": [
                    {
                        "input": {
                            "content": "content",
                            "author": "author",
                        },
                        "output": {
                            "content": "content",
                            "author": "author",
                        },
                    }
                ],
            },
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(ModelCountMessageTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_count_message_tokens(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.count_message_tokens(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelCountMessageTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_count_message_tokens(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.count_message_tokens(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelCountMessageTokensResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_count_message_tokens(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.count_message_tokens(
                model="",
                prompt={"messages": [{"content": "content"}]},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_count_text_tokens(self, client: RobertTest24) -> None:
        model = client.beta.models.count_text_tokens(
            model="model",
            prompt={"text": "text"},
        )
        assert_matches_type(ModelCountTextTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_count_text_tokens_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.count_text_tokens(
            model="model",
            prompt={"text": "text"},
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(ModelCountTextTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_count_text_tokens(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.count_text_tokens(
            model="model",
            prompt={"text": "text"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelCountTextTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_count_text_tokens(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.count_text_tokens(
            model="model",
            prompt={"text": "text"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelCountTextTokensResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_count_text_tokens(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.count_text_tokens(
                model="",
                prompt={"text": "text"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_count_tokens(self, client: RobertTest24) -> None:
        model = client.beta.models.count_tokens(
            model="model",
        )
        assert_matches_type(ModelCountTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_count_tokens_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.count_tokens(
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
            generate_content_request={
                "contents": [
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
                "model": "model",
                "cached_content": "cachedContent",
                "generation_config": {
                    "_response_json_schema": {},
                    "candidate_count": 0,
                    "enable_enhanced_civic_answers": True,
                    "frequency_penalty": 0,
                    "image_config": {"aspect_ratio": "aspectRatio"},
                    "logprobs": 0,
                    "max_output_tokens": 0,
                    "media_resolution": "MEDIA_RESOLUTION_UNSPECIFIED",
                    "presence_penalty": 0,
                    "response_json_schema": {},
                    "response_logprobs": True,
                    "response_mime_type": "responseMimeType",
                    "response_modalities": ["MODALITY_UNSPECIFIED"],
                    "response_schema": {
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
                    "seed": 0,
                    "speech_config": {
                        "language_code": "languageCode",
                        "multi_speaker_voice_config": {
                            "speaker_voice_configs": [
                                {
                                    "speaker": "speaker",
                                    "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                                }
                            ]
                        },
                        "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                    },
                    "stop_sequences": ["string"],
                    "temperature": 0,
                    "thinking_config": {
                        "include_thoughts": True,
                        "thinking_budget": 0,
                    },
                    "top_k": 0,
                    "top_p": 0,
                },
                "safety_settings": [
                    {
                        "category": "HARM_CATEGORY_UNSPECIFIED",
                        "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                    }
                ],
                "system_instruction": {
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
                "tool_config": {
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
                "tools": [
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
            },
        )
        assert_matches_type(ModelCountTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_count_tokens(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.count_tokens(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelCountTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_count_tokens(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.count_tokens(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelCountTokensResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_count_tokens(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.count_tokens(
                model="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_embed_content(self, client: RobertTest24) -> None:
        model = client.beta.models.embed_content(
            path_model="model",
            content={},
            body_model="model",
        )
        assert_matches_type(EmbedContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_embed_content_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.embed_content(
            path_model="model",
            content={
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
            body_model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            output_dimensionality=0,
            task_type="TASK_TYPE_UNSPECIFIED",
            title="title",
        )
        assert_matches_type(EmbedContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_embed_content(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.embed_content(
            path_model="model",
            content={},
            body_model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(EmbedContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_embed_content(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.embed_content(
            path_model="model",
            content={},
            body_model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(EmbedContentResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_embed_content(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_model` but received ''"):
            client.beta.models.with_raw_response.embed_content(
                path_model="",
                content={},
                body_model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_embed_text(self, client: RobertTest24) -> None:
        model = client.beta.models.embed_text(
            path_model="model",
            body_model="model",
        )
        assert_matches_type(ModelEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_embed_text_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.embed_text(
            path_model="model",
            body_model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            text="text",
        )
        assert_matches_type(ModelEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_embed_text(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.embed_text(
            path_model="model",
            body_model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_embed_text(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.embed_text(
            path_model="model",
            body_model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelEmbedTextResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_embed_text(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_model` but received ''"):
            client.beta.models.with_raw_response.embed_text(
                path_model="",
                body_model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_answer(self, client: RobertTest24) -> None:
        model = client.beta.models.generate_answer(
            model="model",
            answer_style="ANSWER_STYLE_UNSPECIFIED",
            contents=[{}],
        )
        assert_matches_type(ModelGenerateAnswerResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_answer_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.generate_answer(
            model="model",
            answer_style="ANSWER_STYLE_UNSPECIFIED",
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
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            inline_passages={
                "passages": [
                    {
                        "id": "id",
                        "content": {
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
                    }
                ]
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_UNSPECIFIED",
                    "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                }
            ],
            semantic_retriever={
                "query": {
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
                "source": "source",
                "max_chunks_count": 0,
                "metadata_filters": [
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
                "minimum_relevance_score": 0,
            },
            temperature=0,
        )
        assert_matches_type(ModelGenerateAnswerResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate_answer(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.generate_answer(
            model="model",
            answer_style="ANSWER_STYLE_UNSPECIFIED",
            contents=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelGenerateAnswerResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate_answer(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.generate_answer(
            model="model",
            answer_style="ANSWER_STYLE_UNSPECIFIED",
            contents=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelGenerateAnswerResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_generate_answer(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.generate_answer(
                model="",
                answer_style="ANSWER_STYLE_UNSPECIFIED",
                contents=[{}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_content(self, client: RobertTest24) -> None:
        model = client.beta.models.generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        )
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_content_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.generate_content(
            path_model="model",
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
            body_model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            cached_content="cachedContent",
            generation_config={
                "_response_json_schema": {},
                "candidate_count": 0,
                "enable_enhanced_civic_answers": True,
                "frequency_penalty": 0,
                "image_config": {"aspect_ratio": "aspectRatio"},
                "logprobs": 0,
                "max_output_tokens": 0,
                "media_resolution": "MEDIA_RESOLUTION_UNSPECIFIED",
                "presence_penalty": 0,
                "response_json_schema": {},
                "response_logprobs": True,
                "response_mime_type": "responseMimeType",
                "response_modalities": ["MODALITY_UNSPECIFIED"],
                "response_schema": {
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
                "seed": 0,
                "speech_config": {
                    "language_code": "languageCode",
                    "multi_speaker_voice_config": {
                        "speaker_voice_configs": [
                            {
                                "speaker": "speaker",
                                "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                            }
                        ]
                    },
                    "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                },
                "stop_sequences": ["string"],
                "temperature": 0,
                "thinking_config": {
                    "include_thoughts": True,
                    "thinking_budget": 0,
                },
                "top_k": 0,
                "top_p": 0,
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_UNSPECIFIED",
                    "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                }
            ],
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
        )
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate_content(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate_content(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(GenerateContentResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_generate_content(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_model` but received ''"):
            client.beta.models.with_raw_response.generate_content(
                path_model="",
                contents=[{}],
                body_model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_message(self, client: RobertTest24) -> None:
        model = client.beta.models.generate_message(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        )
        assert_matches_type(ModelGenerateMessageResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_message_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.generate_message(
            model="model",
            prompt={
                "messages": [
                    {
                        "content": "content",
                        "author": "author",
                    }
                ],
                "context": "context",
                "examples": [
                    {
                        "input": {
                            "content": "content",
                            "author": "author",
                        },
                        "output": {
                            "content": "content",
                            "author": "author",
                        },
                    }
                ],
            },
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            candidate_count=0,
            temperature=0,
            top_k=0,
            top_p=0,
        )
        assert_matches_type(ModelGenerateMessageResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate_message(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.generate_message(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelGenerateMessageResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate_message(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.generate_message(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelGenerateMessageResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_generate_message(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.generate_message(
                model="",
                prompt={"messages": [{"content": "content"}]},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_text(self, client: RobertTest24) -> None:
        model = client.beta.models.generate_text(
            model="model",
            prompt={"text": "text"},
        )
        assert_matches_type(GenerateText, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_text_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.generate_text(
            model="model",
            prompt={"text": "text"},
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            candidate_count=0,
            max_output_tokens=0,
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_UNSPECIFIED",
                    "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                }
            ],
            stop_sequences=["string"],
            temperature=0,
            top_k=0,
            top_p=0,
        )
        assert_matches_type(GenerateText, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate_text(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.generate_text(
            model="model",
            prompt={"text": "text"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(GenerateText, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate_text(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.generate_text(
            model="model",
            prompt={"text": "text"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(GenerateText, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_generate_text(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.generate_text(
                model="",
                prompt={"text": "text"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_predict(self, client: RobertTest24) -> None:
        model = client.beta.models.predict(
            model="model",
            instances=[{}],
        )
        assert_matches_type(ModelPredictResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_predict_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.predict(
            model="model",
            instances=[{}],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            parameters={},
        )
        assert_matches_type(ModelPredictResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_predict(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.predict(
            model="model",
            instances=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelPredictResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_predict(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.predict(
            model="model",
            instances=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelPredictResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_predict(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.predict(
                model="",
                instances=[{}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_predict_long_running(self, client: RobertTest24) -> None:
        model = client.beta.models.predict_long_running(
            model="model",
            instances=[{}],
        )
        assert_matches_type(ModelPredictLongRunningResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_predict_long_running_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.predict_long_running(
            model="model",
            instances=[{}],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            parameters={},
        )
        assert_matches_type(ModelPredictLongRunningResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_predict_long_running(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.predict_long_running(
            model="model",
            instances=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelPredictLongRunningResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_predict_long_running(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.predict_long_running(
            model="model",
            instances=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelPredictLongRunningResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_predict_long_running(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            client.beta.models.with_raw_response.predict_long_running(
                model="",
                instances=[{}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_stream_generate_content(self, client: RobertTest24) -> None:
        model = client.beta.models.stream_generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        )
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_stream_generate_content_with_all_params(self, client: RobertTest24) -> None:
        model = client.beta.models.stream_generate_content(
            path_model="model",
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
            body_model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            cached_content="cachedContent",
            generation_config={
                "_response_json_schema": {},
                "candidate_count": 0,
                "enable_enhanced_civic_answers": True,
                "frequency_penalty": 0,
                "image_config": {"aspect_ratio": "aspectRatio"},
                "logprobs": 0,
                "max_output_tokens": 0,
                "media_resolution": "MEDIA_RESOLUTION_UNSPECIFIED",
                "presence_penalty": 0,
                "response_json_schema": {},
                "response_logprobs": True,
                "response_mime_type": "responseMimeType",
                "response_modalities": ["MODALITY_UNSPECIFIED"],
                "response_schema": {
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
                "seed": 0,
                "speech_config": {
                    "language_code": "languageCode",
                    "multi_speaker_voice_config": {
                        "speaker_voice_configs": [
                            {
                                "speaker": "speaker",
                                "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                            }
                        ]
                    },
                    "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                },
                "stop_sequences": ["string"],
                "temperature": 0,
                "thinking_config": {
                    "include_thoughts": True,
                    "thinking_budget": 0,
                },
                "top_k": 0,
                "top_p": 0,
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_UNSPECIFIED",
                    "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                }
            ],
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
        )
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_stream_generate_content(self, client: RobertTest24) -> None:
        response = client.beta.models.with_raw_response.stream_generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_stream_generate_content(self, client: RobertTest24) -> None:
        with client.beta.models.with_streaming_response.stream_generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(GenerateContentResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_stream_generate_content(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_model` but received ''"):
            client.beta.models.with_raw_response.stream_generate_content(
                path_model="",
                contents=[{}],
                body_model="model",
            )


class TestAsyncModels:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.retrieve(
            model="model",
        )
        assert_matches_type(Model, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.retrieve(
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(Model, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.retrieve(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(Model, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.retrieve(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(Model, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.retrieve(
                model="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.list()
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.list(
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            page_size=0,
            page_token="pageToken",
        )
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelListResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_async_batch_embed_content(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.async_batch_embed_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        )
        assert_matches_type(AsyncBatchEmbedContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_async_batch_embed_content_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.async_batch_embed_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {
                    "file_name": "fileName",
                    "requests": {
                        "requests": [
                            {
                                "request": {
                                    "content": {
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
                                    "model": "model",
                                    "output_dimensionality": 0,
                                    "task_type": "TASK_TYPE_UNSPECIFIED",
                                    "title": "title",
                                },
                                "metadata": {"foo": "bar"},
                            }
                        ]
                    },
                },
                "model": "model",
                "priority": "priority",
            },
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(AsyncBatchEmbedContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_async_batch_embed_content(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.async_batch_embed_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(AsyncBatchEmbedContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_async_batch_embed_content(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.async_batch_embed_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(AsyncBatchEmbedContentOperation, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_async_batch_embed_content(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.async_batch_embed_content(
                model="",
                batch={
                    "display_name": "displayName",
                    "input_config": {},
                    "model": "model",
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_embed_contents(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.batch_embed_contents(
            model="model",
            requests=[
                {
                    "content": {},
                    "model": "model",
                }
            ],
        )
        assert_matches_type(ModelBatchEmbedContentsResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_embed_contents_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.batch_embed_contents(
            model="model",
            requests=[
                {
                    "content": {
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
                    "model": "model",
                    "output_dimensionality": 0,
                    "task_type": "TASK_TYPE_UNSPECIFIED",
                    "title": "title",
                }
            ],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(ModelBatchEmbedContentsResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_batch_embed_contents(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.batch_embed_contents(
            model="model",
            requests=[
                {
                    "content": {},
                    "model": "model",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelBatchEmbedContentsResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_batch_embed_contents(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.batch_embed_contents(
            model="model",
            requests=[
                {
                    "content": {},
                    "model": "model",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelBatchEmbedContentsResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_batch_embed_contents(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.batch_embed_contents(
                model="",
                requests=[
                    {
                        "content": {},
                        "model": "model",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_embed_text(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.batch_embed_text(
            model="model",
        )
        assert_matches_type(ModelBatchEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_embed_text_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.batch_embed_text(
            model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            requests=[
                {
                    "model": "model",
                    "text": "text",
                }
            ],
            texts=["string"],
        )
        assert_matches_type(ModelBatchEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_batch_embed_text(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.batch_embed_text(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelBatchEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_batch_embed_text(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.batch_embed_text(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelBatchEmbedTextResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_batch_embed_text(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.batch_embed_text(
                model="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_generate_content(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.batch_generate_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        )
        assert_matches_type(BatchGenerateContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_generate_content_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.batch_generate_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {
                    "file_name": "fileName",
                    "requests": {
                        "requests": [
                            {
                                "request": {
                                    "contents": [
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
                                    "model": "model",
                                    "cached_content": "cachedContent",
                                    "generation_config": {
                                        "_response_json_schema": {},
                                        "candidate_count": 0,
                                        "enable_enhanced_civic_answers": True,
                                        "frequency_penalty": 0,
                                        "image_config": {"aspect_ratio": "aspectRatio"},
                                        "logprobs": 0,
                                        "max_output_tokens": 0,
                                        "media_resolution": "MEDIA_RESOLUTION_UNSPECIFIED",
                                        "presence_penalty": 0,
                                        "response_json_schema": {},
                                        "response_logprobs": True,
                                        "response_mime_type": "responseMimeType",
                                        "response_modalities": ["MODALITY_UNSPECIFIED"],
                                        "response_schema": {
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
                                        "seed": 0,
                                        "speech_config": {
                                            "language_code": "languageCode",
                                            "multi_speaker_voice_config": {
                                                "speaker_voice_configs": [
                                                    {
                                                        "speaker": "speaker",
                                                        "voice_config": {
                                                            "prebuilt_voice_config": {"voice_name": "voiceName"}
                                                        },
                                                    }
                                                ]
                                            },
                                            "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                                        },
                                        "stop_sequences": ["string"],
                                        "temperature": 0,
                                        "thinking_config": {
                                            "include_thoughts": True,
                                            "thinking_budget": 0,
                                        },
                                        "top_k": 0,
                                        "top_p": 0,
                                    },
                                    "safety_settings": [
                                        {
                                            "category": "HARM_CATEGORY_UNSPECIFIED",
                                            "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                                        }
                                    ],
                                    "system_instruction": {
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
                                    "tool_config": {
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
                                    "tools": [
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
                                },
                                "metadata": {"foo": "bar"},
                            }
                        ]
                    },
                },
                "model": "model",
                "priority": "priority",
            },
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(BatchGenerateContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_batch_generate_content(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.batch_generate_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(BatchGenerateContentOperation, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_batch_generate_content(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.batch_generate_content(
            model="model",
            batch={
                "display_name": "displayName",
                "input_config": {},
                "model": "model",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(BatchGenerateContentOperation, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_batch_generate_content(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.batch_generate_content(
                model="",
                batch={
                    "display_name": "displayName",
                    "input_config": {},
                    "model": "model",
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_count_message_tokens(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.count_message_tokens(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        )
        assert_matches_type(ModelCountMessageTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_count_message_tokens_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.count_message_tokens(
            model="model",
            prompt={
                "messages": [
                    {
                        "content": "content",
                        "author": "author",
                    }
                ],
                "context": "context",
                "examples": [
                    {
                        "input": {
                            "content": "content",
                            "author": "author",
                        },
                        "output": {
                            "content": "content",
                            "author": "author",
                        },
                    }
                ],
            },
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(ModelCountMessageTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_count_message_tokens(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.count_message_tokens(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelCountMessageTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_count_message_tokens(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.count_message_tokens(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelCountMessageTokensResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_count_message_tokens(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.count_message_tokens(
                model="",
                prompt={"messages": [{"content": "content"}]},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_count_text_tokens(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.count_text_tokens(
            model="model",
            prompt={"text": "text"},
        )
        assert_matches_type(ModelCountTextTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_count_text_tokens_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.count_text_tokens(
            model="model",
            prompt={"text": "text"},
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
        )
        assert_matches_type(ModelCountTextTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_count_text_tokens(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.count_text_tokens(
            model="model",
            prompt={"text": "text"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelCountTextTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_count_text_tokens(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.count_text_tokens(
            model="model",
            prompt={"text": "text"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelCountTextTokensResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_count_text_tokens(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.count_text_tokens(
                model="",
                prompt={"text": "text"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_count_tokens(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.count_tokens(
            model="model",
        )
        assert_matches_type(ModelCountTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_count_tokens_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.count_tokens(
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
            generate_content_request={
                "contents": [
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
                "model": "model",
                "cached_content": "cachedContent",
                "generation_config": {
                    "_response_json_schema": {},
                    "candidate_count": 0,
                    "enable_enhanced_civic_answers": True,
                    "frequency_penalty": 0,
                    "image_config": {"aspect_ratio": "aspectRatio"},
                    "logprobs": 0,
                    "max_output_tokens": 0,
                    "media_resolution": "MEDIA_RESOLUTION_UNSPECIFIED",
                    "presence_penalty": 0,
                    "response_json_schema": {},
                    "response_logprobs": True,
                    "response_mime_type": "responseMimeType",
                    "response_modalities": ["MODALITY_UNSPECIFIED"],
                    "response_schema": {
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
                    "seed": 0,
                    "speech_config": {
                        "language_code": "languageCode",
                        "multi_speaker_voice_config": {
                            "speaker_voice_configs": [
                                {
                                    "speaker": "speaker",
                                    "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                                }
                            ]
                        },
                        "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                    },
                    "stop_sequences": ["string"],
                    "temperature": 0,
                    "thinking_config": {
                        "include_thoughts": True,
                        "thinking_budget": 0,
                    },
                    "top_k": 0,
                    "top_p": 0,
                },
                "safety_settings": [
                    {
                        "category": "HARM_CATEGORY_UNSPECIFIED",
                        "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                    }
                ],
                "system_instruction": {
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
                "tool_config": {
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
                "tools": [
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
            },
        )
        assert_matches_type(ModelCountTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_count_tokens(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.count_tokens(
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelCountTokensResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_count_tokens(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.count_tokens(
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelCountTokensResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_count_tokens(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.count_tokens(
                model="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_embed_content(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.embed_content(
            path_model="model",
            content={},
            body_model="model",
        )
        assert_matches_type(EmbedContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_embed_content_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.embed_content(
            path_model="model",
            content={
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
            body_model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            output_dimensionality=0,
            task_type="TASK_TYPE_UNSPECIFIED",
            title="title",
        )
        assert_matches_type(EmbedContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_embed_content(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.embed_content(
            path_model="model",
            content={},
            body_model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(EmbedContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_embed_content(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.embed_content(
            path_model="model",
            content={},
            body_model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(EmbedContentResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_embed_content(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_model` but received ''"):
            await async_client.beta.models.with_raw_response.embed_content(
                path_model="",
                content={},
                body_model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_embed_text(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.embed_text(
            path_model="model",
            body_model="model",
        )
        assert_matches_type(ModelEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_embed_text_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.embed_text(
            path_model="model",
            body_model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            text="text",
        )
        assert_matches_type(ModelEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_embed_text(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.embed_text(
            path_model="model",
            body_model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelEmbedTextResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_embed_text(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.embed_text(
            path_model="model",
            body_model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelEmbedTextResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_embed_text(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_model` but received ''"):
            await async_client.beta.models.with_raw_response.embed_text(
                path_model="",
                body_model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_answer(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.generate_answer(
            model="model",
            answer_style="ANSWER_STYLE_UNSPECIFIED",
            contents=[{}],
        )
        assert_matches_type(ModelGenerateAnswerResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_answer_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.generate_answer(
            model="model",
            answer_style="ANSWER_STYLE_UNSPECIFIED",
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
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            inline_passages={
                "passages": [
                    {
                        "id": "id",
                        "content": {
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
                    }
                ]
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_UNSPECIFIED",
                    "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                }
            ],
            semantic_retriever={
                "query": {
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
                "source": "source",
                "max_chunks_count": 0,
                "metadata_filters": [
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
                "minimum_relevance_score": 0,
            },
            temperature=0,
        )
        assert_matches_type(ModelGenerateAnswerResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate_answer(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.generate_answer(
            model="model",
            answer_style="ANSWER_STYLE_UNSPECIFIED",
            contents=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelGenerateAnswerResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate_answer(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.generate_answer(
            model="model",
            answer_style="ANSWER_STYLE_UNSPECIFIED",
            contents=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelGenerateAnswerResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_generate_answer(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.generate_answer(
                model="",
                answer_style="ANSWER_STYLE_UNSPECIFIED",
                contents=[{}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_content(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        )
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_content_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.generate_content(
            path_model="model",
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
            body_model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            cached_content="cachedContent",
            generation_config={
                "_response_json_schema": {},
                "candidate_count": 0,
                "enable_enhanced_civic_answers": True,
                "frequency_penalty": 0,
                "image_config": {"aspect_ratio": "aspectRatio"},
                "logprobs": 0,
                "max_output_tokens": 0,
                "media_resolution": "MEDIA_RESOLUTION_UNSPECIFIED",
                "presence_penalty": 0,
                "response_json_schema": {},
                "response_logprobs": True,
                "response_mime_type": "responseMimeType",
                "response_modalities": ["MODALITY_UNSPECIFIED"],
                "response_schema": {
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
                "seed": 0,
                "speech_config": {
                    "language_code": "languageCode",
                    "multi_speaker_voice_config": {
                        "speaker_voice_configs": [
                            {
                                "speaker": "speaker",
                                "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                            }
                        ]
                    },
                    "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                },
                "stop_sequences": ["string"],
                "temperature": 0,
                "thinking_config": {
                    "include_thoughts": True,
                    "thinking_budget": 0,
                },
                "top_k": 0,
                "top_p": 0,
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_UNSPECIFIED",
                    "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                }
            ],
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
        )
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate_content(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate_content(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(GenerateContentResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_generate_content(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_model` but received ''"):
            await async_client.beta.models.with_raw_response.generate_content(
                path_model="",
                contents=[{}],
                body_model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_message(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.generate_message(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        )
        assert_matches_type(ModelGenerateMessageResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_message_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.generate_message(
            model="model",
            prompt={
                "messages": [
                    {
                        "content": "content",
                        "author": "author",
                    }
                ],
                "context": "context",
                "examples": [
                    {
                        "input": {
                            "content": "content",
                            "author": "author",
                        },
                        "output": {
                            "content": "content",
                            "author": "author",
                        },
                    }
                ],
            },
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            candidate_count=0,
            temperature=0,
            top_k=0,
            top_p=0,
        )
        assert_matches_type(ModelGenerateMessageResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate_message(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.generate_message(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelGenerateMessageResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate_message(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.generate_message(
            model="model",
            prompt={"messages": [{"content": "content"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelGenerateMessageResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_generate_message(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.generate_message(
                model="",
                prompt={"messages": [{"content": "content"}]},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_text(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.generate_text(
            model="model",
            prompt={"text": "text"},
        )
        assert_matches_type(GenerateText, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_text_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.generate_text(
            model="model",
            prompt={"text": "text"},
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            candidate_count=0,
            max_output_tokens=0,
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_UNSPECIFIED",
                    "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                }
            ],
            stop_sequences=["string"],
            temperature=0,
            top_k=0,
            top_p=0,
        )
        assert_matches_type(GenerateText, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate_text(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.generate_text(
            model="model",
            prompt={"text": "text"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(GenerateText, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate_text(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.generate_text(
            model="model",
            prompt={"text": "text"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(GenerateText, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_generate_text(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.generate_text(
                model="",
                prompt={"text": "text"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_predict(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.predict(
            model="model",
            instances=[{}],
        )
        assert_matches_type(ModelPredictResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_predict_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.predict(
            model="model",
            instances=[{}],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            parameters={},
        )
        assert_matches_type(ModelPredictResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_predict(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.predict(
            model="model",
            instances=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelPredictResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_predict(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.predict(
            model="model",
            instances=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelPredictResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_predict(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.predict(
                model="",
                instances=[{}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_predict_long_running(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.predict_long_running(
            model="model",
            instances=[{}],
        )
        assert_matches_type(ModelPredictLongRunningResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_predict_long_running_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.predict_long_running(
            model="model",
            instances=[{}],
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            parameters={},
        )
        assert_matches_type(ModelPredictLongRunningResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_predict_long_running(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.predict_long_running(
            model="model",
            instances=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelPredictLongRunningResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_predict_long_running(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.predict_long_running(
            model="model",
            instances=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelPredictLongRunningResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_predict_long_running(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model` but received ''"):
            await async_client.beta.models.with_raw_response.predict_long_running(
                model="",
                instances=[{}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_stream_generate_content(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.stream_generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        )
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_stream_generate_content_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        model = await async_client.beta.models.stream_generate_content(
            path_model="model",
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
            body_model="model",
            api_empty={"xgafv": "1"},
            alt="json",
            callback="$callback",
            pretty_print=True,
            cached_content="cachedContent",
            generation_config={
                "_response_json_schema": {},
                "candidate_count": 0,
                "enable_enhanced_civic_answers": True,
                "frequency_penalty": 0,
                "image_config": {"aspect_ratio": "aspectRatio"},
                "logprobs": 0,
                "max_output_tokens": 0,
                "media_resolution": "MEDIA_RESOLUTION_UNSPECIFIED",
                "presence_penalty": 0,
                "response_json_schema": {},
                "response_logprobs": True,
                "response_mime_type": "responseMimeType",
                "response_modalities": ["MODALITY_UNSPECIFIED"],
                "response_schema": {
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
                "seed": 0,
                "speech_config": {
                    "language_code": "languageCode",
                    "multi_speaker_voice_config": {
                        "speaker_voice_configs": [
                            {
                                "speaker": "speaker",
                                "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                            }
                        ]
                    },
                    "voice_config": {"prebuilt_voice_config": {"voice_name": "voiceName"}},
                },
                "stop_sequences": ["string"],
                "temperature": 0,
                "thinking_config": {
                    "include_thoughts": True,
                    "thinking_budget": 0,
                },
                "top_k": 0,
                "top_p": 0,
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_UNSPECIFIED",
                    "threshold": "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
                }
            ],
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
        )
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_stream_generate_content(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.models.with_raw_response.stream_generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(GenerateContentResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_stream_generate_content(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.models.with_streaming_response.stream_generate_content(
            path_model="model",
            contents=[{}],
            body_model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(GenerateContentResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_stream_generate_content(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_model` but received ''"):
            await async_client.beta.models.with_raw_response.stream_generate_content(
                path_model="",
                contents=[{}],
                body_model="model",
            )
