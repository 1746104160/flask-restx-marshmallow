"""parameters of flask_restx_marshmallow."""

from collections.abc import Iterable
from typing import TYPE_CHECKING, Literal, Self, Unpack, override

from marshmallow.fields import Field, List, Tuple
from marshmallow.schema import Schema
from werkzeug.utils import cached_property

from ._json import json
from .enum import Location
from .type import FieldLocations, SchemaInitKwargs
from .util import get_location, set_location

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from collections.abc import Set as AbstractSet

    from marshmallow.fields import Field


class Parameters(Schema):
    """Base Parameters.

    Args:
        location (Location, optional): location of the parameters. Defaults to None.
        kwargs (dict): other key word arguments.
    """

    description: str = "Request parameters"

    class Meta:
        """Meta for Parameters."""

        unknown: str = "exclude"
        render_module = json

    def __init__(
        self: Self,
        *,
        location: Location
        | Literal["query", "header", "formData", "body", "cookie", "path"]
        | None = None,
        **kwargs: Unpack["SchemaInitKwargs"],
    ) -> None:
        """Base Parameters.

        Args:
            location (Location, optional): location of the parameters. Defaults to None.
            kwargs (dict): other key word arguments.
        """
        super().__init__(**kwargs)
        self.location: (
            Location
            | Literal["query", "header", "formData", "body", "cookie", "path"]
            | None
        ) = location
        if location is not None:
            self.default_location = Location(location)
        for field in self.fields.values():
            field.load_only = True
            if location is not None:
                if isinstance(location, str):
                    location = self.default_location
                set_location(field, location)

    @cached_property
    def locations(self: Self) -> set[str]:
        """Get locations.

        Returns:
            set[str]: locations
        """
        return {
            get_location(field) or self.default_location
            for field in self.fields.values()
        }

    @cached_property
    def field_locations(self: Self) -> list[FieldLocations]:
        """Get (field_name, location, is_multiple) for each non-body field.

        Returns:
            list[FieldLocations]: field name, location, is multiple
        """
        return [
            FieldLocations(
                name,
                location or self.default_location,
                isinstance(field, List | Tuple),
            )
            for name, field in self.fields.items()
            if (location := get_location(field)) is not Location.BODY
        ]

    def __contains__(self: Self, field: str) -> bool:
        """Whether field in self.fields.

        Args:
            field (str): field name

        Returns:
            bool: whether field in self.fields
        """
        return field in self.fields

    def items(self: Self) -> "Iterable[tuple[str, dict]]":
        """Make dict.

        Yields:
            tuple[str, dict]: field name and field dict
        """
        for key, value in self.fields.items():
            yield key, value.__dict__

    def __setitem__(self: Self, key: str, value: "Field") -> None:
        """Set item."""
        self.fields[key] = value

    def copy_body_fields(self: Self) -> "Parameters":
        """Return a copy of this schema with only fields that location is body."""
        return Parameters.from_dict(
            dict(
                filter(
                    lambda field: get_location(field[1]) is Location.BODY,
                    self.fields.items(),
                ),
            ),
            name=f"{type(self).__name__}Body",
        )(location=Location.BODY)

    def copy_form_fields(self: Self) -> "Parameters":
        """Return a copy of this schema with only fields that location is formdata."""
        return Parameters.from_dict(
            dict(
                filter(
                    lambda field: get_location(field[1]) is Location.FORM_DATA,
                    self.fields.items(),
                ),
            ),
            name=f"{type(self).__name__}Form",
        )(location=Location.FORM_DATA)

    def combine(self: Self, other: "Parameters") -> "Parameters":
        """Combine two schemas.

        Args:
            other (Self): other schema

        Returns:
            Self: combined schema
        """
        return self.from_dict(other.fields, name=other.__class__.__name__)(
            location=other.location,
        )

    def __or__(self, other: "Parameters") -> "Parameters":
        """Combine two schemas.

        Args:
            other (Self): other schema

        Returns:
            Self: combined schema
        """
        return self.from_dict(other.fields, name=other.__class__.__name__)(
            location=other.location,
        )

    if TYPE_CHECKING:

        @override
        def load[T](
            self: Self,
            data: Mapping[str, T] | Iterable[Mapping[str, T]],
            *,
            many: bool | None = None,
            partial: bool | Sequence[str] | AbstractSet[str] | None = None,
            unknown: str | None = None,
        ) -> dict: ...
        @override
        def loads(
            self: Self,
            json_data: str,
            *,
            many: bool | None = None,
            partial: bool | Sequence[str] | AbstractSet[str] | None = None,
            unknown: str | None = None,
            **kwargs,  # noqa: ANN003
        ) -> dict: ...

        @override
        @classmethod
        def from_dict[T: Field](
            cls,
            fields: dict[str, T],
            *,
            name: str = "GeneratedSchema",
        ) -> type["Parameters"]: ...
