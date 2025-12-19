# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from robert_test_24 import RobertTest24, AsyncRobertTest24
from robert_test_24._utils import parse_datetime
from robert_test_24.types.beta import (
    GenerateContentResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDynamic:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_dynamic_id_generate_content(self, client: RobertTest24) -> None:
        dynamic = client.beta.dynamic.dynamic_id_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        )
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_dynamic_id_generate_content_with_all_params(self, client: RobertTest24) -> None:
        dynamic = client.beta.dynamic.dynamic_id_generate_content(
            dynamic_id="dynamicId",
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
            model="model",
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
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_dynamic_id_generate_content(self, client: RobertTest24) -> None:
        response = client.beta.dynamic.with_raw_response.dynamic_id_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dynamic = response.parse()
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_dynamic_id_generate_content(self, client: RobertTest24) -> None:
        with client.beta.dynamic.with_streaming_response.dynamic_id_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dynamic = response.parse()
            assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_dynamic_id_generate_content(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dynamic_id` but received ''"):
            client.beta.dynamic.with_raw_response.dynamic_id_generate_content(
                dynamic_id="",
                contents=[{}],
                model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_dynamic_id_stream_generate_content(self, client: RobertTest24) -> None:
        dynamic = client.beta.dynamic.dynamic_id_stream_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        )
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_dynamic_id_stream_generate_content_with_all_params(self, client: RobertTest24) -> None:
        dynamic = client.beta.dynamic.dynamic_id_stream_generate_content(
            dynamic_id="dynamicId",
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
            model="model",
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
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_dynamic_id_stream_generate_content(self, client: RobertTest24) -> None:
        response = client.beta.dynamic.with_raw_response.dynamic_id_stream_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dynamic = response.parse()
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_dynamic_id_stream_generate_content(self, client: RobertTest24) -> None:
        with client.beta.dynamic.with_streaming_response.dynamic_id_stream_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dynamic = response.parse()
            assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_dynamic_id_stream_generate_content(self, client: RobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dynamic_id` but received ''"):
            client.beta.dynamic.with_raw_response.dynamic_id_stream_generate_content(
                dynamic_id="",
                contents=[{}],
                model="model",
            )


class TestAsyncDynamic:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_dynamic_id_generate_content(self, async_client: AsyncRobertTest24) -> None:
        dynamic = await async_client.beta.dynamic.dynamic_id_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        )
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_dynamic_id_generate_content_with_all_params(self, async_client: AsyncRobertTest24) -> None:
        dynamic = await async_client.beta.dynamic.dynamic_id_generate_content(
            dynamic_id="dynamicId",
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
            model="model",
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
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_dynamic_id_generate_content(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.dynamic.with_raw_response.dynamic_id_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dynamic = await response.parse()
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_dynamic_id_generate_content(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.dynamic.with_streaming_response.dynamic_id_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dynamic = await response.parse()
            assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_dynamic_id_generate_content(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dynamic_id` but received ''"):
            await async_client.beta.dynamic.with_raw_response.dynamic_id_generate_content(
                dynamic_id="",
                contents=[{}],
                model="model",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_dynamic_id_stream_generate_content(self, async_client: AsyncRobertTest24) -> None:
        dynamic = await async_client.beta.dynamic.dynamic_id_stream_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        )
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_dynamic_id_stream_generate_content_with_all_params(
        self, async_client: AsyncRobertTest24
    ) -> None:
        dynamic = await async_client.beta.dynamic.dynamic_id_stream_generate_content(
            dynamic_id="dynamicId",
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
            model="model",
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
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_dynamic_id_stream_generate_content(self, async_client: AsyncRobertTest24) -> None:
        response = await async_client.beta.dynamic.with_raw_response.dynamic_id_stream_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dynamic = await response.parse()
        assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_dynamic_id_stream_generate_content(self, async_client: AsyncRobertTest24) -> None:
        async with async_client.beta.dynamic.with_streaming_response.dynamic_id_stream_generate_content(
            dynamic_id="dynamicId",
            contents=[{}],
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dynamic = await response.parse()
            assert_matches_type(GenerateContentResponse, dynamic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_dynamic_id_stream_generate_content(self, async_client: AsyncRobertTest24) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dynamic_id` but received ''"):
            await async_client.beta.dynamic.with_raw_response.dynamic_id_stream_generate_content(
                dynamic_id="",
                contents=[{}],
                model="model",
            )
