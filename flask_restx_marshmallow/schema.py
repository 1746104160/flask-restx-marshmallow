"""
Description: schemas of flask_restx_marshmallow
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 14:16:11
FilePath: /flask_restx_marshmallow/flask_restx_marshmallow/schema.py
"""
import importlib
from types import ModuleType
from typing import Optional

from flask_restx.model import Model as OriginalModel
from marshmallow import Schema as OriginalSchema
from marshmallow import fields
from marshmallow_sqlalchemy import (
    SQLAlchemyAutoSchema as OriginalSQLAlchemyAutoSchema,
)
from marshmallow_sqlalchemy import SQLAlchemySchema as OriginalSQLAlchemySchema
from marshmallow_sqlalchemy.convert import (
    ModelConverter as OriginalModelConverter,
)
from marshmallow_sqlalchemy.convert import (
    _base_column,
    _has_default,
    _set_meta_kwarg,
)
from sqlalchemy import Column, Table
from sqlalchemy_utils.types import ScalarListType
from typing_extensions import Self
from werkzeug.utils import cached_property

from .util import (
    API_DEFAULT_HTTP_CODE_MESSAGES,
    ObjectDict,
    converter,
    get_default,
)


class SchemaMixin:
    """
    Author: 1746104160
    msg: Support deepcopy
    """

    def __deepcopy__(self, _) -> Self:
        """support deepcopy"""
        return self


class Schema(SchemaMixin, OriginalSchema):
    """
    Author: 1746104160
    msg: Support deepcopy and change default dict class
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        for field in self.fields.values():
            field.dump_only = True
        try:
            json: ModuleType = importlib.import_module("orjson")
        except ModuleNotFoundError:
            json = importlib.import_module("json")

        self.opts.render_module = json

    @property
    def dict_class(self) -> type:
        return ObjectDict


class StandardSchema(Schema):
    """
    Author: 1746104160
    msg: Standard schema
    """

    code: int = fields.Integer(
        required=True, dump_default=0, metadata={"description": "status code"}
    )
    message: str = fields.String(
        required=True, dump_default="ok", metadata={"description": "message"}
    )
    success: bool = fields.Boolean(
        required=True,
        dump_default=True,
        metadata={"description": "whether success"},
    )

    def __init__(self, message: str, **kwargs) -> None:
        """set default message

        Args:
            message (str): return message
        """
        super().__init__(**kwargs)
        self.dump_fields["message"].dump_default = message


class ModelConverter(OriginalModelConverter):
    """
    Author: 1746104160
    msg: SqlAlchemy model converter
    """

    SQLA_TYPE_MAPPING = {
        **OriginalModelConverter.SQLA_TYPE_MAPPING,
        **{ScalarListType: fields.List},
    }

    def __init__(self, schema_cls: Optional["SQLAlchemySchema"] = None) -> None:
        super().__init__(schema_cls=schema_cls)

    def _add_column_kwargs(self, kwargs: dict, column: Column) -> None:
        """Add keyword arguments to kwargs (in-place) based on the column.

        Args:
            kwargs (dict): keyword arguments
            column (Column): sqlalchemy column
        """
        if hasattr(column, "nullable"):
            if column.nullable:
                kwargs["allow_none"] = True
            kwargs["required"] = not column.nullable and not _has_default(
                column
            )
        if (getattr(column, "default", None)) is not None:
            _set_meta_kwarg(kwargs, "default", column.default.arg)

    def _get_field_kwargs_for_property(self, prop: Table) -> dict[str, list]:
        """get field keyword arguments for a property

        Args:
            prop (Table): property

        Returns:
            dict: keyword arguments
        """
        kwargs: dict[str, list] = self.get_base_kwargs()
        if hasattr(prop, "columns"):
            column: Column = _base_column(prop.columns[0])
            self._add_column_kwargs(kwargs, column)
            prop: Column = column
        if hasattr(prop, "direction"):
            self._add_relationship_kwargs(kwargs, prop)
        if (doc := getattr(prop, "doc", None)) is not None:
            _set_meta_kwarg(kwargs, "description", doc)
        if (column_type := getattr(prop, "type", None)) and isinstance(
            column_type, ScalarListType
        ):
            kwargs["cls_or_instance"] = (
                fields.String()
                if column_type.coerce_func == str
                else fields.Integer()
                if column_type.coerce_func == int
                else fields.Float()
                if column_type.coerce_func == float
                else fields.Field()
            )
        return kwargs


class SQLAlchemySchema(SchemaMixin, OriginalSQLAlchemySchema):
    """
    Author: 1746104160
    msg: Support deepcopy and change default dict class
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        for field in self.fields.values():
            field.dump_only = True
        try:
            json: ModuleType = importlib.import_module("orjson")
        except ModuleNotFoundError:
            json = importlib.import_module("json")

        self.opts.render_module = json
        self.opts.model_converter: type[ModelConverter] = ModelConverter

    @property
    def dict_class(self) -> type:
        return ObjectDict


class SQLAlchemyAutoSchema(SchemaMixin, OriginalSQLAlchemyAutoSchema):
    """
    Author: 1746104160
    msg: Support deepcopy and change default dict class
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        for field in self.fields.values():
            field.dump_only = True
        try:
            json: ModuleType = importlib.import_module("orjson")
        except ModuleNotFoundError:
            json = importlib.import_module("json")

        self.opts.render_module = json
        self.opts.model_converter: type[ModelConverter] = ModelConverter

    @property
    def dict_class(self) -> type:
        return ObjectDict


class DefaultHTTPErrorSchema(Schema):
    """
    Author: 1746104160
    msg: Default HTTP Error Schema
    """

    code: int = fields.Integer(
        required=True, dump_default=500, metadata={"description": "status code"}
    )
    message: str = fields.String(
        required=True,
        dump_default=API_DEFAULT_HTTP_CODE_MESSAGES[500],
        metadata={"description": "message"},
    )
    success: bool = fields.Boolean(
        required=True,
        dump_default=False,
        metadata={"description": "whether success"},
    )

    def __init__(self, http_code: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.dump_fields["code"].dump_default = http_code
        self.dump_fields[
            "message"
        ].dump_default = API_DEFAULT_HTTP_CODE_MESSAGES[http_code]


class Model(OriginalModel):
    """
    Author: 1746104160
    msg: Patched Model
    """

    def __init__(self, name: str, model, **kwargs) -> None:
        super().__init__(name, {"__schema__": model}, **kwargs)

    @cached_property
    def __schema__(self) -> dict:
        """schema json

        Raises:
            NotImplementedError: not implemented

        Returns:
            dict: schema json
        """
        schema: Schema | fields.Field = self["__schema__"]
        if isinstance(schema, Schema):
            json_schema: dict = {"type": "object", "properties": {}}
            for field_name, field_obj in schema.dump_fields.items():
                observed_field_name: str = field_obj.data_key or field_name
                field_schema: dict = converter.field2property(field_obj)
                if (default := get_default(field_obj)) is not None:
                    field_schema["default"] = default
                json_schema["properties"][observed_field_name] = field_schema
            return json_schema
        if isinstance(schema, fields.Field):
            field_schema = converter.field2property(schema)
            if (default := get_default(schema)) is not None:
                field_schema["default"] = default
            return field_schema
        raise NotImplementedError()
