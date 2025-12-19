# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["ToolConfigParam", "FunctionCallingConfig", "RetrievalConfig", "RetrievalConfigLatLng"]


class FunctionCallingConfig(TypedDict, total=False):
    """Configuration for specifying function calling behavior."""

    allowed_function_names: Annotated[SequenceNotStr[str], PropertyInfo(alias="allowedFunctionNames")]
    """Optional.

    A set of function names that, when provided, limits the functions the model will
    call.

    This should only be set when the Mode is ANY or VALIDATED. Function names should
    match [FunctionDeclaration.name]. When set, model will predict a function call
    from only allowed function names.
    """

    mode: Literal["MODE_UNSPECIFIED", "AUTO", "ANY", "NONE", "VALIDATED"]
    """Optional.

    Specifies the mode in which function calling should execute. If unspecified, the
    default value will be set to AUTO.
    """


class RetrievalConfigLatLng(TypedDict, total=False):
    """An object that represents a latitude/longitude pair.

    This is expressed as a
    pair of doubles to represent degrees latitude and degrees longitude. Unless
    specified otherwise, this object must conform to the
    WGS84 standard. Values must be within normalized ranges.
    """

    latitude: float
    """The latitude in degrees. It must be in the range [-90.0, +90.0]."""

    longitude: float
    """The longitude in degrees. It must be in the range [-180.0, +180.0]."""


class RetrievalConfig(TypedDict, total=False):
    """Retrieval config."""

    language_code: Annotated[str, PropertyInfo(alias="languageCode")]
    """Optional.

    The language code of the user. Language code for content. Use language tags
    defined by [BCP47](https://www.rfc-editor.org/rfc/bcp/bcp47.txt).
    """

    lat_lng: Annotated[RetrievalConfigLatLng, PropertyInfo(alias="latLng")]
    """An object that represents a latitude/longitude pair.

    This is expressed as a pair of doubles to represent degrees latitude and degrees
    longitude. Unless specified otherwise, this object must conform to the WGS84
    standard. Values must be within normalized ranges.
    """


class ToolConfigParam(TypedDict, total=False):
    """
    The Tool configuration containing parameters for specifying `Tool` use
    in the request.
    """

    function_calling_config: Annotated[FunctionCallingConfig, PropertyInfo(alias="functionCallingConfig")]
    """Configuration for specifying function calling behavior."""

    retrieval_config: Annotated[RetrievalConfig, PropertyInfo(alias="retrievalConfig")]
    """Retrieval config."""
