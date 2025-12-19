# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["SchemaParam"]


class SchemaParam(TypedDict, total=False):
    """
    The `Schema` object allows the definition of input and output data types.
    These types can be objects, but also primitives and arrays.
    Represents a select subset of an [OpenAPI 3.0 schema
    object](https://spec.openapis.org/oas/v3.0.3#schema).
    """

    type: Required[Literal["TYPE_UNSPECIFIED", "STRING", "NUMBER", "INTEGER", "BOOLEAN", "ARRAY", "OBJECT", "NULL"]]
    """Required. Data type."""

    any_of: Annotated[Iterable["SchemaParam"], PropertyInfo(alias="anyOf")]
    """Optional.

    The value should be validated against any (one or more) of the subschemas in the
    list.
    """

    default: object
    """Optional.

    Default value of the field. Per JSON Schema, this field is intended for
    documentation generators and doesn't affect validation. Thus it's included here
    and ignored so that developers who send schemas with a `default` field don't get
    unknown-field errors.
    """

    description: str
    """Optional.

    A brief description of the parameter. This could contain examples of use.
    Parameter description may be formatted as Markdown.
    """

    enum: SequenceNotStr[str]
    """Optional.

    Possible values of the element of Type.STRING with enum format. For example we
    can define an Enum Direction as : {type:STRING, format:enum, enum:["EAST",
    NORTH", "SOUTH", "WEST"]}
    """

    example: object
    """Optional.

    Example of the object. Will only populated when the object is the root.
    """

    format: str
    """Optional.

    The format of the data. Any value is allowed, but most do not trigger any
    special functionality.
    """

    items: "SchemaParam"
    """
    The `Schema` object allows the definition of input and output data types. These
    types can be objects, but also primitives and arrays. Represents a select subset
    of an [OpenAPI 3.0 schema object](https://spec.openapis.org/oas/v3.0.3#schema).
    """

    maximum: float
    """Optional. Maximum value of the Type.INTEGER and Type.NUMBER"""

    max_items: Annotated[str, PropertyInfo(alias="maxItems")]
    """Optional. Maximum number of the elements for Type.ARRAY."""

    max_length: Annotated[str, PropertyInfo(alias="maxLength")]
    """Optional. Maximum length of the Type.STRING"""

    max_properties: Annotated[str, PropertyInfo(alias="maxProperties")]
    """Optional. Maximum number of the properties for Type.OBJECT."""

    minimum: float
    """Optional.

    SCHEMA FIELDS FOR TYPE INTEGER and NUMBER Minimum value of the Type.INTEGER and
    Type.NUMBER
    """

    min_items: Annotated[str, PropertyInfo(alias="minItems")]
    """Optional. Minimum number of the elements for Type.ARRAY."""

    min_length: Annotated[str, PropertyInfo(alias="minLength")]
    """Optional. SCHEMA FIELDS FOR TYPE STRING Minimum length of the Type.STRING"""

    min_properties: Annotated[str, PropertyInfo(alias="minProperties")]
    """Optional. Minimum number of the properties for Type.OBJECT."""

    nullable: bool
    """Optional. Indicates if the value may be null."""

    pattern: str
    """Optional.

    Pattern of the Type.STRING to restrict a string to a regular expression.
    """

    properties: Dict[str, "SchemaParam"]
    """Optional. Properties of Type.OBJECT."""

    property_ordering: Annotated[SequenceNotStr[str], PropertyInfo(alias="propertyOrdering")]
    """Optional.

    The order of the properties. Not a standard field in open api spec. Used to
    determine the order of the properties in the response.
    """

    required: SequenceNotStr[str]
    """Optional. Required properties of Type.OBJECT."""

    title: str
    """Optional. The title of the schema."""
