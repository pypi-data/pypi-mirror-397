# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["PermissionCreatePermissionParams", "api_empty"]


class PermissionCreatePermissionParams(TypedDict, total=False):
    role: Required[Literal["ROLE_UNSPECIFIED", "OWNER", "WRITER", "READER"]]
    """Required. The role granted by this permission."""

    api_empty: Annotated[api_empty, PropertyInfo(alias="$")]

    alt: Annotated[Literal["json", "media", "proto"], PropertyInfo(alias="$alt")]
    """Data format for response."""

    callback: Annotated[str, PropertyInfo(alias="$callback")]
    """JSONP"""

    pretty_print: Annotated[bool, PropertyInfo(alias="$prettyPrint")]
    """Returns response with indentations and line breaks."""

    email_address: Annotated[str, PropertyInfo(alias="emailAddress")]
    """Optional.

    Immutable. The email address of the user of group which this permission refers.
    Field is not set when permission's grantee type is EVERYONE.
    """

    grantee_type: Annotated[
        Literal["GRANTEE_TYPE_UNSPECIFIED", "USER", "GROUP", "EVERYONE"], PropertyInfo(alias="granteeType")
    ]
    """Optional. Immutable. The type of the grantee."""


class api_empty(TypedDict, total=False):
    xgafv: Literal["1", "2"]
    """V1 error format."""
