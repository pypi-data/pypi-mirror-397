# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["VoiceConfig", "PrebuiltVoiceConfig"]


class PrebuiltVoiceConfig(BaseModel):
    """The configuration for the prebuilt speaker to use."""

    voice_name: Optional[str] = FieldInfo(alias="voiceName", default=None)
    """The name of the preset voice to use."""


class VoiceConfig(BaseModel):
    """The configuration for the voice to use."""

    prebuilt_voice_config: Optional[PrebuiltVoiceConfig] = FieldInfo(alias="prebuiltVoiceConfig", default=None)
    """The configuration for the prebuilt speaker to use."""
