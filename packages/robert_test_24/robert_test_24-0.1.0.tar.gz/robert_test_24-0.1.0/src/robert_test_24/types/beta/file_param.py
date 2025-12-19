# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo
from ..._models import set_pydantic_config

__all__ = ["FileParam"]


class FileParam(TypedDict, total=False):
    """
    A file uploaded to the API.
    Next ID: 15
    """

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Optional.

    The human-readable display name for the `File`. The display name must be no more
    than 512 characters in length, including spaces. Example: "Welcome Image"
    """

    name: str
    """Immutable.

    Identifier. The `File` resource name. The ID (name excluding the "files/"
    prefix) can contain up to 40 characters that are lowercase alphanumeric or
    dashes (-). The ID cannot start or end with a dash. If the name is empty on
    create, a unique name will be generated. Example: `files/123-456`
    """

    source: Literal["SOURCE_UNSPECIFIED", "UPLOADED", "GENERATED", "REGISTERED"]
    """Source of the File."""


set_pydantic_config(FileParam, {"arbitrary_types_allowed": True})
