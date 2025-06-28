"""schemas of flask_restx_marshmallow."""

from collections.abc import Iterable
from copy import deepcopy
from typing import TYPE_CHECKING, Self, Unpack, cast, overload, override

from marshmallow.constants import missing
from marshmallow.fields import Dict, Enum, Field, Integer, List, String
from marshmallow.schema import Schema as OriginalSchema

from ._json import json
from .enum import ResponseCode

if TYPE_CHECKING:
    from collections import OrderedDict

    from .type import SchemaInitKwargs


class Schema(OriginalSchema):
    """Response schema."""

    description: str = "Response schema"

    class Meta:
        """Meta for response schema."""

        unknown = "exclude"
        render_module = json

    def __init__(
        self: Self,
        header_fields: Iterable[str] | None = None,
        **kwargs: Unpack["SchemaInitKwargs"],
    ) -> None:
        """Response schema.

        Args:
            header_fields (Iterable[str] | None): fields in response header
            kwargs (Unpack["SchemaInitKwargs"]): keyword arguments
        """
        super().__init__(**kwargs)
        self.header_fields = header_fields
        for name, field_obj in self.fields.items():
            if header_fields and name in header_fields:
                cast("dict", field_obj.metadata)["header"] = True
            else:
                field_obj.dump_only = True

    def copy_body_fields(self: Self) -> "Schema":
        """Return a copy of this schema with response body fields."""
        return Schema.from_dict(
            dict(
                filter(
                    lambda field: field[1].metadata.get("header") is not True
                    and field[1].metadata.get("simple") is not True,
                    self.fields.items(),
                ),
            ),
            name=f"{type(self).__name__}Body",
        )()

    def copy_header_fields(self: Self) -> "Schema":
        """Return a copy of this schema with response header fields."""
        return Schema.from_dict(
            dict(
                filter(
                    lambda field: field[1].metadata.get("header") is True,
                    self.fields.items(),
                ),
            ),
            name=f"{type(self).__name__}Header",
        )()

    def copy_simple_string_field(self: Self) -> "String | None":
        """Return a copy of this schema with simple string fields."""
        return cast(
            "String | None",
            deepcopy(
                next(
                    filter(
                        lambda field: isinstance(field, String)
                        and field.metadata.get("simple") is True,
                        self.fields.values(),
                    ),
                    None,
                ),
            ),
        )

    @property
    def example(self: Self) -> dict:
        """Example of response schema."""
        return {
            field_name: example
            for field_name, field in self.fields.items()
            if (
                example := field.metadata.get("example")
                or (default if (default := field.dump_default) is not missing else None)
            )
        }

    if TYPE_CHECKING:

        @overload
        def dump(self: Self, obj: object | dict) -> dict | OrderedDict: ...

        @overload
        def dump(
            self: Self,
            obj: object | dict,
            *,
            many: bool,
        ) -> list[dict | OrderedDict]: ...

        @override
        def dump(
            self: Self,
            obj: object | dict,
            *,
            many: bool | None = None,
        ) -> dict | OrderedDict | list[dict | OrderedDict]: ...

        @overload
        def dumps(self: Self, obj: object | dict) -> str | bytes: ...

        @overload
        def dumps(self: Self, obj: object | dict, *, many: bool) -> str | bytes: ...

        @override
        def dumps(
            self: Self,
            obj: object | dict,
            *args,
            many: bool | None = None,
            **kwargs,
        ) -> str | bytes: ...

        @override
        @classmethod
        def from_dict[T: Field](
            cls,
            fields: dict[str, T],
            *,
            name: str = "GeneratedSchema",
        ) -> type["Schema"]: ...


class UnprocessableEntitySchema(Schema):
    """Unprocessable Entity Schema."""

    code = Enum(
        ResponseCode,
        by_value=Integer,
        required=True,
        dump_default=ResponseCode.ERROR,
        metadata={"description": "response code", "default": ResponseCode.ERROR},
    )
    message = Dict(
        keys=String,
        values=List(String()),
        required=True,
        dump_default={"field": ["Unprocessable Entity"]},
        metadata={
            "description": "message",
            "default": {"field": ["Unprocessable Entity"]},
        },
    )


class InternalServerErrorSchema(Schema):
    """Internal Server Error Schema."""

    message = String(
        dump_default="Internal Server Error",
        metadata={
            "description": "message",
            "example": "Internal Server Error",
            "simple": True,
        },
    )
