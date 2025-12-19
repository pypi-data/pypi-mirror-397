# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["VoiceConfigParam", "PrebuiltVoiceConfig"]


class PrebuiltVoiceConfig(TypedDict, total=False):
    """The configuration for the prebuilt speaker to use."""

    voice_name: Annotated[str, PropertyInfo(alias="voiceName")]
    """The name of the preset voice to use."""


class VoiceConfigParam(TypedDict, total=False):
    """The configuration for the voice to use."""

    prebuilt_voice_config: Annotated[PrebuiltVoiceConfig, PropertyInfo(alias="prebuiltVoiceConfig")]
    """The configuration for the prebuilt speaker to use."""
