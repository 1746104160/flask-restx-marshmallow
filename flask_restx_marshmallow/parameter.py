"""
Description: parameters of flask_restx_marshmallow
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 14:15:27
FilePath: /flask_restx_marshmallow/flask_restx_marshmallow/parameter.py
"""
import importlib
from dataclasses import dataclass
from types import ModuleType
from typing import Generator

from marshmallow import EXCLUDE, Schema, fields

from .util import ObjectDict


class Parameters(Schema):
    """
    Author: 1746104160
    msg: Base Parameters
    """

    @dataclass
    class Meta:
        """
        Author: 1746104160
        msg: Meta for Parameters
        """

        unknown: str = EXCLUDE

    def __init__(
        self, *, add_jwt: bool = False, location: str, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        for field in self.fields.values():
            field.load_only = True
            if not field.metadata.get("location"):
                field.metadata["location"] = location
        if add_jwt:
            self.fields["jwt"] = fields.String(
                metadata={"description": "JWT", "location": "query"}
            )
        try:
            json: ModuleType = importlib.import_module("orjson")
        except ModuleNotFoundError:
            json = importlib.import_module("json")
        self.opts.render_module = json

    @property
    def dict_class(self) -> type:
        return ObjectDict

    def __contains__(self, field: str) -> bool:
        return field in self.fields

    def items(self) -> Generator[tuple[str, dict], None, None]:
        """
        Author: 1746104160
        msg: make dict
        param {*} self
        """
        for key, value in self.fields.items():
            yield key, value.__dict__

    def __setitem__(self, key: str, value: fields.Field) -> None:
        self.fields[key] = value


class QueryParameters(Parameters):
    """
    Author: 1746104160
    msg: query parameters
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(location="query", **kwargs)


class PostFormParameters(Parameters):
    """
    Author: 1746104160
    msg: form parameters
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(location="formData", **kwargs)


class JSONParameters(Parameters):
    """
    Author: 1746104160
    msg: json parameters
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(location="body", **kwargs)


class CookieParameters(Parameters):
    """
    Author: 1746104160
    msg: cookie parameters
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(location="cookie", **kwargs)


class HeaderParameters(Parameters):
    """
    Author: 1746104160
    msg: header parameters
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(location="header", **kwargs)
