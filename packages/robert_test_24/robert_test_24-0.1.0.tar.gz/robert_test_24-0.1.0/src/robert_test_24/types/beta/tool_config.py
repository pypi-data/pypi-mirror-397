# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ToolConfig", "FunctionCallingConfig", "RetrievalConfig", "RetrievalConfigLatLng"]


class FunctionCallingConfig(BaseModel):
    """Configuration for specifying function calling behavior."""

    allowed_function_names: Optional[List[str]] = FieldInfo(alias="allowedFunctionNames", default=None)
    """Optional.

    A set of function names that, when provided, limits the functions the model will
    call.

    This should only be set when the Mode is ANY or VALIDATED. Function names should
    match [FunctionDeclaration.name]. When set, model will predict a function call
    from only allowed function names.
    """

    mode: Optional[Literal["MODE_UNSPECIFIED", "AUTO", "ANY", "NONE", "VALIDATED"]] = None
    """Optional.

    Specifies the mode in which function calling should execute. If unspecified, the
    default value will be set to AUTO.
    """


class RetrievalConfigLatLng(BaseModel):
    """An object that represents a latitude/longitude pair.

    This is expressed as a
    pair of doubles to represent degrees latitude and degrees longitude. Unless
    specified otherwise, this object must conform to the
    WGS84 standard. Values must be within normalized ranges.
    """

    latitude: Optional[float] = None
    """The latitude in degrees. It must be in the range [-90.0, +90.0]."""

    longitude: Optional[float] = None
    """The longitude in degrees. It must be in the range [-180.0, +180.0]."""


class RetrievalConfig(BaseModel):
    """Retrieval config."""

    language_code: Optional[str] = FieldInfo(alias="languageCode", default=None)
    """Optional.

    The language code of the user. Language code for content. Use language tags
    defined by [BCP47](https://www.rfc-editor.org/rfc/bcp/bcp47.txt).
    """

    lat_lng: Optional[RetrievalConfigLatLng] = FieldInfo(alias="latLng", default=None)
    """An object that represents a latitude/longitude pair.

    This is expressed as a pair of doubles to represent degrees latitude and degrees
    longitude. Unless specified otherwise, this object must conform to the WGS84
    standard. Values must be within normalized ranges.
    """


class ToolConfig(BaseModel):
    """
    The Tool configuration containing parameters for specifying `Tool` use
    in the request.
    """

    function_calling_config: Optional[FunctionCallingConfig] = FieldInfo(alias="functionCallingConfig", default=None)
    """Configuration for specifying function calling behavior."""

    retrieval_config: Optional[RetrievalConfig] = FieldInfo(alias="retrievalConfig", default=None)
    """Retrieval config."""
