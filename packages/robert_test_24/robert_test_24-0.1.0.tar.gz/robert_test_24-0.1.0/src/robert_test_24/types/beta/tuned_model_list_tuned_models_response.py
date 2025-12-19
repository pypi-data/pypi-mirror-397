# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .tuned_model import TunedModel

__all__ = ["TunedModelListTunedModelsResponse"]


class TunedModelListTunedModelsResponse(BaseModel):
    """Response from `ListTunedModels` containing a paginated list of Models."""

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """A token, which can be sent as `page_token` to retrieve the next page.

    If this field is omitted, there are no more pages.
    """

    tuned_models: Optional[List[TunedModel]] = FieldInfo(alias="tunedModels", default=None)
    """The returned Models."""
