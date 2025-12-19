# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .message import Message
from ..._models import BaseModel
from .content_filter import ContentFilter

__all__ = ["ModelGenerateMessageResponse"]


class ModelGenerateMessageResponse(BaseModel):
    """The response from the model.

    This includes candidate messages and
    conversation history in the form of chronologically-ordered messages.
    """

    candidates: Optional[List[Message]] = None
    """Candidate response messages from the model."""

    filters: Optional[List[ContentFilter]] = None
    """A set of content filtering metadata for the prompt and response text.

    This indicates which `SafetyCategory`(s) blocked a candidate from this response,
    the lowest `HarmProbability` that triggered a block, and the HarmThreshold
    setting for that category.
    """

    messages: Optional[List[Message]] = None
    """The conversation history used by the model."""
