# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from ..custom_metadata_param import CustomMetadataParam

__all__ = ["DocumentUpdateParams", "api_empty"]


class DocumentUpdateParams(TypedDict, total=False):
    corpus: Required[str]

    update_mask: Required[Annotated[str, PropertyInfo(alias="updateMask")]]
    """Required.

    The list of fields to update. Currently, this only supports updating
    `display_name` and `custom_metadata`.
    """

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    custom_metadata: Annotated[Iterable[CustomMetadataParam], PropertyInfo(alias="customMetadata")]
    """Optional.

    User provided custom metadata stored as key-value pairs used for querying. A
    `Document` can have a maximum of 20 `CustomMetadata`.
    """

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Optional.

    The human-readable display name for the `Document`. The display name must be no
    more than 512 characters in length, including spaces. Example: "Semantic
    Retriever Documentation"
    """

    name: str
    """Immutable.

    Identifier. The `Document` resource name. The ID (name excluding the
    "ragStores/\\**/documents/" prefix) can contain up to 40 characters that are
    lowercase alphanumeric or dashes (-). The ID cannot start or end with a dash. If
    the name is empty on create, a unique name will be derived from `display_name`
    along with a 12 character random suffix. Example:
    `ragStores/{corpus_id}/documents/my-awesome-doc-123a456b789c`
    """


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
