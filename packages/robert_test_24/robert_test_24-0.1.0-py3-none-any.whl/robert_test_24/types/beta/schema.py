# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Schema"]


class Schema(BaseModel):
    """
    The `Schema` object allows the definition of input and output data types.
    These types can be objects, but also primitives and arrays.
    Represents a select subset of an [OpenAPI 3.0 schema
    object](https://spec.openapis.org/oas/v3.0.3#schema).
    """

    type: Literal["TYPE_UNSPECIFIED", "STRING", "NUMBER", "INTEGER", "BOOLEAN", "ARRAY", "OBJECT", "NULL"]
    """Required. Data type."""

    any_of: Optional[List["Schema"]] = FieldInfo(alias="anyOf", default=None)
    """Optional.

    The value should be validated against any (one or more) of the subschemas in the
    list.
    """

    default: Optional[object] = None
    """Optional.

    Default value of the field. Per JSON Schema, this field is intended for
    documentation generators and doesn't affect validation. Thus it's included here
    and ignored so that developers who send schemas with a `default` field don't get
    unknown-field errors.
    """

    description: Optional[str] = None
    """Optional.

    A brief description of the parameter. This could contain examples of use.
    Parameter description may be formatted as Markdown.
    """

    enum: Optional[List[str]] = None
    """Optional.

    Possible values of the element of Type.STRING with enum format. For example we
    can define an Enum Direction as : {type:STRING, format:enum, enum:["EAST",
    NORTH", "SOUTH", "WEST"]}
    """

    example: Optional[object] = None
    """Optional.

    Example of the object. Will only populated when the object is the root.
    """

    format: Optional[str] = None
    """Optional.

    The format of the data. Any value is allowed, but most do not trigger any
    special functionality.
    """

    items: Optional["Schema"] = None
    """
    The `Schema` object allows the definition of input and output data types. These
    types can be objects, but also primitives and arrays. Represents a select subset
    of an [OpenAPI 3.0 schema object](https://spec.openapis.org/oas/v3.0.3#schema).
    """

    maximum: Optional[float] = None
    """Optional. Maximum value of the Type.INTEGER and Type.NUMBER"""

    max_items: Optional[str] = FieldInfo(alias="maxItems", default=None)
    """Optional. Maximum number of the elements for Type.ARRAY."""

    max_length: Optional[str] = FieldInfo(alias="maxLength", default=None)
    """Optional. Maximum length of the Type.STRING"""

    max_properties: Optional[str] = FieldInfo(alias="maxProperties", default=None)
    """Optional. Maximum number of the properties for Type.OBJECT."""

    minimum: Optional[float] = None
    """Optional.

    SCHEMA FIELDS FOR TYPE INTEGER and NUMBER Minimum value of the Type.INTEGER and
    Type.NUMBER
    """

    min_items: Optional[str] = FieldInfo(alias="minItems", default=None)
    """Optional. Minimum number of the elements for Type.ARRAY."""

    min_length: Optional[str] = FieldInfo(alias="minLength", default=None)
    """Optional. SCHEMA FIELDS FOR TYPE STRING Minimum length of the Type.STRING"""

    min_properties: Optional[str] = FieldInfo(alias="minProperties", default=None)
    """Optional. Minimum number of the properties for Type.OBJECT."""

    nullable: Optional[bool] = None
    """Optional. Indicates if the value may be null."""

    pattern: Optional[str] = None
    """Optional.

    Pattern of the Type.STRING to restrict a string to a regular expression.
    """

    properties: Optional[Dict[str, "Schema"]] = None
    """Optional. Properties of Type.OBJECT."""

    property_ordering: Optional[List[str]] = FieldInfo(alias="propertyOrdering", default=None)
    """Optional.

    The order of the properties. Not a standard field in open api spec. Used to
    determine the order of the properties in the response.
    """

    required: Optional[List[str]] = None
    """Optional. Required properties of Type.OBJECT."""

    title: Optional[str] = None
    """Optional. The title of the schema."""
