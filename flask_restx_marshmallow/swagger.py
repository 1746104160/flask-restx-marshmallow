"""
Description: patched swagger of flask_restx_marshmallow
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-04 21:45:14
FilePath: /flask_restx_marshmallow/flask_restx_marshmallow/swagger.py
"""
from apispec.ext.marshmallow.common import get_fields
from flask import current_app, request
from flask_restx.swagger import Swagger as OriginalSwagger
from flask_restx.utils import not_none
from marshmallow.fields import Field, List
from typing_extensions import override

import flask_restx_marshmallow

from .schema import Schema
from .util import DEFAULT_FIELD_MAPPING, converter, get_default, get_description


class Swagger(OriginalSwagger):
    """
    Author: 1746104160
    msg: swagger documentation patched
    """

    @override
    def as_dict(self) -> dict:
        """serialize the swagger object

        Returns:
            dict: serialized swagger object
        """
        api_spec: dict = super().as_dict()
        api_spec["schemes"] = ["http", "https"]
        return api_spec

    def get_host(self) -> str:
        """get host

        Returns:
            str: host name
        """
        hostname: str | None = current_app.config.get("SERVER_NAME", None)
        self.api: flask_restx_marshmallow.Api
        if hostname and self.api.blueprint and self.api.blueprint.subdomain:
            hostname = ".".join((self.api.blueprint.subdomain, hostname))
        if hostname is None:
            hostname = request.host
        return hostname

    def parameters_for(self, doc: dict[str, Schema]) -> list[dict]:
        """get parameters for the swagger document

        Args:
            doc (dict[str, Schema]): swagger document

        Returns:
            list[dict]: json parameters
        """
        schema: Schema = doc["params"]
        if not schema:
            return []
        if isinstance(schema, list):
            return schema
        parameters: list = []
        json_fields: dict[str, Field] = {}
        fields: dict[str, Field] = get_fields(schema, exclude_dump_only=True)
        for field_name, field_obj in fields.items():
            location: str | None = field_obj.metadata.get("location")
            if location == "body":
                json_fields.update({field_name: field_obj})
            else:
                data: dict = {
                    "in": location,
                    "required": getattr(field_obj, "required", False),
                    "name": field_obj.data_key or field_name,
                    "type": DEFAULT_FIELD_MAPPING[field_obj.__class__],
                }
                if (default := get_default(field_obj)) is not None:
                    data["default"] = default
                if data["type"] == "array":
                    list_field: List = field_obj
                    data["items"] = {
                        "type": DEFAULT_FIELD_MAPPING[
                            list_field.inner.__class__
                        ]
                    }
                    if (description := get_description(field_obj)) is not None:
                        data["items"]["description"] = description
                    if getattr(list_field.inner, "required", False):
                        data["required"] = True
                elif (description := get_description(field_obj)) is not None:
                    data["description"] = description
                parameters.append(data)
        if json_fields:
            json_schema: dict[str, Field] = converter.fields2jsonschema(
                json_fields
            )
            for field_name, field_obj in json_fields.items():
                if (default := get_default(field_obj)) is not None:
                    json_schema["properties"][field_name]["default"] = default
            parameters.append(
                {
                    "in": "body",
                    "required": True,
                    "name": "payload",
                    "schema": json_schema,
                }
            )
        return parameters

    def serialize_operation(self, doc: dict[str, dict], method: str) -> dict:
        """add swagger-ui consumes operation

        Args:
            doc (dict[str, dict]): swagger doc
            method (str): operation method

        Returns:
            dict: serialized swagger doc
        """
        operation: dict = {
            "responses": self.responses_for(doc, method) or None,
            "summary": doc[method]["docstring"]["summary"],
            "description": self.description_for(doc, method) or None,
            "operationId": self.operation_id_for(doc, method),
            "parameters": self.parameters_for(doc[method]) or None,
            "security": self.security_for(doc, method),
        }
        # Handle 'produces' mimetypes documentation
        if "produces" in doc[method]:
            operation["produces"] = doc[method]["produces"]
        # Handle deprecated annotation
        if doc.get("deprecated") or doc[method].get("deprecated"):
            operation["deprecated"] = True
        # Handle form exceptions:
        doc_params: list = list(doc.get("params", {}).values())
        all_params: list = doc_params + (operation["parameters"] or [])
        if all_params and any(p["in"] == "formData" for p in all_params):
            if any(p["type"] == "file" for p in all_params):
                operation["consumes"] = [
                    "application/json",
                    "multipart/form-data",
                ]
            else:
                operation["consumes"] = [
                    "application/json",
                    "application/x-www-form-urlencoded",
                    "multipart/form-data",
                ]
        operation.update(self.vendor_fields(doc, method))
        return not_none(operation)
