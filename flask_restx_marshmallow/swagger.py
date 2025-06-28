"""patched swagger of flask_restx_marshmallow."""

import re
from collections.abc import Callable, Mapping, Sequence
from http import HTTPStatus
from http.client import HTTPException
from itertools import chain
from typing import TYPE_CHECKING, Literal, Self, cast, overload

from apispec.ext.marshmallow.common import get_fields
from docstring_parser import parse_from_object
from flask import current_app
from flask.globals import request
from marshmallow.constants import missing
from werkzeug.exceptions import InternalServerError

from .enum import Location
from .schema import InternalServerErrorSchema, UnprocessableEntitySchema
from .type import (
    CODES,
    Apidoc,
    APISpec,
    Components,
    Contact,
    DefaultResponse,
    Example,
    Header,
    Info,
    License,
    MarshmallowPlugin,
    MediaType,
    Method,
    OpenAPI,
    Operation,
    Parameter,
    Reference,
    RequestBody,
    Server,
    SwaggerResponse,
    Tag,
    Variable,
)
from .util import (
    authorization_helper,
    get_location,
    make_default_schema,
    schema_name_resolver,
    security_helper,
    tag_helper,
)

if TYPE_CHECKING:
    from flask_restx.resource import Resource

    from .api import Api
    from .namespace import Namespace
    from .parameter import Parameters
    from .schema import Schema


class Swagger:
    """swagger documentation."""

    def __init__(self, api: "Api") -> None:
        """Swagger documentation."""
        self.api = api
        self.ma_plugin = MarshmallowPlugin(schema_name_resolver)
        self.spec = APISpec(
            title=_v(self.api.title),
            version=_v(self.api.version),
            openapi_version="3.1.1",
            plugins=[self.ma_plugin],
        )
        self.ma_plugin.init_spec(self.spec)
        self.add_headers = False
        self.tag_names = set[str]()
        self.errors = dict["CODES", list["Schema"]]()

    def as_dict(self: Self) -> "OpenAPI":
        """Serialize the swagger object.

        Returns:
            OpenAPI: serialized swagger object
        """
        self.as_dict_()
        basepath = self.api.base_path
        host = self.get_host()
        if len(basepath) > 1 and basepath.endswith("/"):
            basepath = basepath[:-1]
        info = Info(title=_v(self.api.title), version=_v(self.api.version))
        if description := _v(self.api.description):
            info["description"] = description
        if terms := _v(self.api.terms_url):
            info["termsOfService"] = terms
        contact = Contact()
        if name := _v(self.api.contact):
            contact["name"] = name
        if email := _v(self.api.contact_email):
            contact["email"] = email
        if url := _v(self.api.contact_url):
            contact["url"] = url
        info["contact"] = contact
        if license_ := _v(self.api.license):
            info["license"] = License(
                name=license_,
                identifier=license_.replace(" ", "-"),
            )
            if license_url := _v(self.api.license_url):
                info["license"]["url"] = license_url
        openapi = OpenAPI(
            openapi="3.1.1",
            info=info,
            servers=[
                Server(
                    url="{scheme}://{host}{basepath}",
                    description="default server",
                    variables={
                        "scheme": Variable(
                            enum=["http", "https"],
                            default=request.scheme,
                            description="http or https",
                        ),
                        "host": Variable(
                            enum=[request.host, host] if host else [request.host],
                            default=request.host,
                            description="host",
                        ),
                        "basepath": Variable(default=basepath, description="basepath"),
                    },
                ),
            ],
            paths=self.spec.paths,
            components=Components(**self.spec.components.to_dict()),
            tags=self.spec.tags,
        )
        if self.api.security:
            openapi["security"] = (
                [security_helper(self.api.security)]
                if not isinstance(self.api.security, Sequence)
                else [security_helper(s) for s in self.api.security]
            )

        return openapi

    def as_dict_(self: Self) -> None:  # noqa: C901, PLR0912
        """Serialize the swagger object."""
        for security_key, security in authorization_helper(
            self.api.authorizations,
        ).items():
            self.spec.components.security_scheme(security_key, security)
        for tag_ in self.api.tags:
            tag = tag_helper(tag_)
            self.spec.tag(tag)
            self.tag_names.add(tag["name"])
        for exception, handler in self.api.error_handlers.items():
            if exception is InternalServerError:
                doc = parse_from_object(handler)
                schema = InternalServerErrorSchema()
                schema.description = (
                    doc.long_description or doc.short_description or schema.description
                )
                self.errors.setdefault("500", []).append(schema)
                self.spec.components.schema("HTTPError500Schema", schema=schema)
                continue
            response = handler()
            name = (
                f"HTTPError{HTTPStatus(response.status_code).value}Schema"
                if issubclass(exception, HTTPException)
                else f"{exception.__name__}Schema"
            )
            if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
                schema = UnprocessableEntitySchema()
                doc = parse_from_object(UnprocessableEntitySchema)
                schema.description = (
                    doc.long_description or doc.short_description or schema.description
                )
            elif response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                schema = InternalServerErrorSchema()
                doc = parse_from_object(InternalServerErrorSchema)
                schema.description = (
                    doc.long_description or doc.short_description or schema.description
                )
            else:
                schema = make_default_schema(
                    name=name,
                    success=False,
                    code=HTTPStatus(response.status_code),
                    message=cast("str | None", response.response.get("message")),
                )()
                doc = parse_from_object(handler)
                schema.description = (
                    doc.long_description or doc.short_description or schema.description
                )
            self.errors.setdefault(cast("CODES", str(response.status_code)), []).append(
                schema,
            )
            self.spec.components.schema(name, schema=schema)

        for ns in self.api.namespaces:
            for security_key, security in authorization_helper(
                ns.authorizations,
            ).items():
                self.spec.components.security_scheme(security_key, security)
            if ns.name not in self.tag_names and ns != self.api.default_namespace:
                self.spec.tag(
                    Tag(name=ns.name, description=ns.description)
                    if ns.description
                    else Tag(name=ns.name),
                )
            if not ns.resources:
                continue
            for resource, urls, route_doc, kwargs in ns.resources:
                for url in self.api.ns_urls(ns, urls):
                    path = re.compile(r"<(?:[^:<>]+:)?([^<>]+)>").sub(r"{\1}", url)
                    doc = parse_from_object(resource)
                    self.spec.path(
                        path,
                        operations=self.serialize_resource_operations(
                            ns,
                            resource,
                            url,
                            route_doc=route_doc,
                            **kwargs,
                        ),
                        summary=doc.short_description,
                        description=doc.long_description,
                        parameters=self.paramters_for(
                            getattr(resource, "__apidoc__", {}).get("params"),
                        ),
                    )

    def get_host(self: Self) -> str | None:
        """Get host.

        Returns:
            str: host name
        """
        hostname = current_app.config.get("SERVER_NAME", None) or None
        if (
            hostname is not None
            and self.api.blueprint is not None
            and self.api.blueprint.subdomain
        ):
            hostname = f"{self.api.blueprint.subdomain}.{hostname}"
        return hostname

    def serialize_resource_operations(
        self: Self,
        ns: "Namespace",
        resource: type["Resource"],
        url: str,
        *,
        route_doc: Apidoc | Literal[False] | None = None,
        **kwargs,  # noqa: ANN003
    ) -> "dict[Method, Operation] | None":
        """Serialize resource operations.

        Args:
            ns (Namespace): namespace
            resource (Resource): resource
            url (str): url
            route_doc (dict | bool | None): route doc
            kwargs (dict): other key word arguments

        Returns:
            dict | None: resource operations
        """
        route_doc = Apidoc() if route_doc is None else route_doc
        if route_doc is False:
            return None
        if (
            resource_doc := merge_api_doc(
                route_doc,
                getattr(resource, "__apidoc__", Apidoc()),
            )
        ) is False:
            return None
        operations = dict[Method, Operation]()
        for method in [m.lower() for m in resource.methods or []]:
            if (
                methods := [cast("str", m).lower() for m in kwargs.get("methods", [])]
            ) and method not in methods:
                continue
            method_doc = merge_api_doc(
                resource_doc,
                getattr(getattr(resource, method), "__apidoc__", Apidoc()),
            )
            tags = [ns.name]
            params = method_doc.get("params")
            parameters = self.paramters_for(params)
            request_body = self.request_body_for(params)
            resp = method_doc.get("responses")
            responses = self.responses_for(resp or {})
            operation_id = (
                f"{ns.name}.{resource.__name__}.{method}."
                f"{url.strip('/').replace('/', '_')}"
            )
            security = method_doc.get("security")
            doc = parse_from_object(getattr(resource, method))

            operation = Operation(
                tags=tags,
                operationId=operation_id,
                responses=responses,
                deprecated=method_doc.get("deprecated") or False,
            )
            if doc.short_description:
                operation["summary"] = doc.short_description
            if doc.long_description:
                operation["description"] = doc.long_description
            if parameters:
                operation["parameters"] = parameters
            if request_body:
                operation["requestBody"] = request_body
            if security:
                operation["security"] = (
                    security if isinstance(security, list) else [security]
                )
            operations[cast("Method", method)] = Operation(**operation)
        return operations

    def paramters_for(
        self: Self,
        params: "Parameters | None",
    ) -> list["Parameter | Reference"] | None:
        """Get parameters for the swagger document.

        Args:
            params (Parameters): parameters

        Returns:
            list[Parameter]: list parameter
        """
        return (
            [
                self.ma_plugin.converter._field2parameter(  # noqa: SLF001
                    field,
                    name=field.data_key or name,
                    location=location.value,
                )
                for name, field in get_fields(params, exclude_dump_only=True).items()
                if (location := get_location(field))
                and location is not Location.BODY
                and location is not Location.FORM_DATA
                and field.metadata.get("show", True)
            ]
            if params is not None
            else None
        )

    def _responses_for(  # noqa: C901, PLR0912
        self: Self,
        code: "CODES",
        schemas: list["Schema"],
    ) -> SwaggerResponse:
        """Get responses for the swagger document.

        Args:
            code (str): code
            schemas (list[schemas]): schemas

        Returns:
            SwaggerResponse: swagger response
        """
        doc = parse_from_object(schemas[0])
        code_responses = SwaggerResponse(
            description=doc.long_description
            or doc.short_description
            or HTTPStatus(int(code)).phrase,
        )
        content: dict[str, MediaType] = {}
        for schema in schemas:
            schema_doc = parse_from_object(schema)
            if len((body := schema.copy_body_fields()).fields.keys()) > 0:
                if type(body).__name__ not in self.spec.components.schemas:
                    self.spec.components.schema(type(body).__name__, schema=body)
                schema_ref = self.ma_plugin.converter.resolve_nested_schema(
                    type(body).__name__,
                )
                if len(schemas) == 1:
                    content.update({
                        "application/json": {
                            "schema": schema_ref,
                            "example": {
                                name: value.metadata.get(
                                    "example",
                                    value.dump_default
                                    if value.dump_default is not missing
                                    else None,
                                )
                                for name, value in zip(
                                    body.fields.keys(),
                                    body.fields.values(),
                                    strict=False,
                                )
                            },
                        },
                    })
                elif (json_ := content.get("application/json")) is None:
                    content.update({
                        "application/json": {
                            "schema": schema_ref,
                            "examples": {
                                type(schema).__name__: {
                                    "summary": schema_doc.long_description
                                    or schema.description,
                                    "description": schema_doc.short_description
                                    or schema.description,
                                    "value": {
                                        name: value.metadata.get(
                                            "example",
                                            value.dump_default
                                            if value.dump_default is not missing
                                            else None,
                                        )
                                        for name, value in zip(
                                            body.fields.keys(),
                                            body.fields.values(),
                                            strict=False,
                                        )
                                    },
                                },
                            },
                        },
                    })
                else:
                    cast(
                        "dict[str, Example | Reference]",
                        json_.setdefault("examples", {}),
                    ).update({
                        type(schema).__name__: Example(
                            summary=schema_doc.long_description or schema.description,
                            description=schema_doc.short_description
                            or schema.description,
                            value={
                                name: value.metadata.get(
                                    "example",
                                    value.dump_default
                                    if value.dump_default is not missing
                                    else None,
                                )
                                for name, value in zip(
                                    body.fields.keys(),
                                    body.fields.values(),
                                    strict=False,
                                )
                            },
                        ),
                    })

            if simple := schema.copy_simple_string_field():
                if len(schemas) == 1:
                    content.update({
                        "text/plain": {
                            "schema": {"type": "string"},
                            "example": simple.metadata.get(
                                "example",
                                simple.dump_default
                                if simple.dump_default is not missing
                                else None,
                            ),
                        },
                    })
                elif (plain := content.get("text/plain")) is None:
                    content.update({
                        "text/plain": {
                            "schema": {"type": "string"},
                            "examples": {
                                type(schema).__name__: Example(
                                    summary=schema_doc.long_description
                                    or schema.description,
                                    description=schema_doc.short_description
                                    or schema.description,
                                    value=simple.metadata.get(
                                        "example",
                                        simple.dump_default
                                        if simple.dump_default is not missing
                                        else None,
                                    ),
                                ),
                            },
                        },
                    })
                else:
                    cast(
                        "dict[str, Example | Reference]",
                        plain.setdefault("examples", {}),
                    ).update({
                        type(schema).__name__: Example(
                            summary=schema_doc.long_description or schema.description,
                            description=schema_doc.short_description
                            or schema.description,
                            value=simple.metadata.get(
                                "example",
                                simple.dump_default
                                if simple.dump_default is not missing
                                else None,
                            ),
                        ),
                    })
            code_responses["content"] = content
            if len((header := schema.copy_header_fields()).fields.keys()) > 0:
                if (headers := code_responses.get("headers")) is None:
                    code_responses["headers"] = {
                        field.data_key or name: {
                            "description": field.metadata.get(
                                "description",
                                field.data_key or name,
                            ),
                            "schema": self.ma_plugin.converter.field2property(field),
                            "example": field.metadata.get(
                                "example",
                                field.dump_default
                                if field.dump_default is not missing
                                else None,
                            ),
                        }
                        for name, field in header.fields.items()
                    }
                elif (headers := code_responses.get("headers")) is None:
                    cast("dict[str, Header | Reference]", headers).update({
                        field.data_key or name: Header(
                            description=field.metadata.get(
                                "description",
                                field.data_key or name,
                            ),
                            schema=self.ma_plugin.converter.field2property(field),
                            example=field.metadata.get(
                                "example",
                                field.dump_default
                                if field.dump_default is not missing
                                else None,
                            ),
                        )
                        for name, field in header.fields.items()
                    })
        return code_responses

    def responses_for(
        self: Self,
        api_responses: Mapping["CODES", "Schema"],
    ) -> DefaultResponse:
        """Get responses for the swagger document.

        Args:
            api_responses (Mapping[str, Schema]): responses

        Returns:
            dict[str, DefaultResponse]: swagger response
        """
        responses = DefaultResponse(default=SwaggerResponse(description="Success"))
        code2schemas = dict["CODES", list["Schema"]]()
        [
            code2schemas.setdefault(code, []).append(schema)
            if not isinstance(schema, list)
            else code2schemas.setdefault(code, []).extend(schema)
            for code, schema in chain(api_responses.items(), self.errors.items())
        ]
        for code, schemas in code2schemas.items():
            responses_ = self._responses_for(code, schemas)
            if HTTPStatus(int(code)) is HTTPStatus.OK:
                responses["default"] = responses_
            responses[code] = responses_
        return responses

    def request_body_for(self: Self, params: "Parameters | None") -> RequestBody | None:
        """Get request body for the swagger document.

        Args:
            params (Parameters): parameters

        Returns:
            RequestBody: request body
        """
        if params is None:
            return None
        doc = parse_from_object(params)
        content: Mapping[str, MediaType] = {}
        required = False
        if has_body := len((body := params.copy_body_fields()).fields.keys()) > 0:
            self.spec.components.schema(type(body).__name__, schema=body)
            content.update({
                "application/json": {
                    "schema": self.ma_plugin.converter.resolve_nested_schema(
                        type(body).__name__,
                    ),
                    "example": {
                        name: value.metadata.get(
                            "example",
                            value.load_default
                            if value.load_default is not missing
                            else None,
                        )
                        for name, value in zip(
                            body.fields.keys(),
                            body.fields.values(),
                            strict=False,
                        )
                    },
                },
            })
            required = any(field.required for field in body.fields.values())
        if has_form := len((form := params.copy_form_fields()).fields.keys()) > 0:
            self.spec.components.schema(type(form).__name__, schema=form)
            content.update({
                "multipart/form-data": {
                    "schema": self.ma_plugin.converter.resolve_nested_schema(
                        type(form).__name__,
                    ),
                    "example": {
                        name: value.metadata.get(
                            "example",
                            value.load_default
                            if value.load_default is not missing
                            else None,
                        )
                        for name, value in zip(
                            form.fields.keys(),
                            form.fields.values(),
                            strict=False,
                        )
                    },
                },
            })
            if not required:
                required = any(field.required for field in form.fields.values())
        if not has_body and not has_form:
            return None
        return RequestBody(
            description=doc.long_description
            or doc.short_description
            or params.description,
            content=content,
            required=required,
        )


@overload
def _v(value: Callable[[], str]) -> str: ...


@overload
def _v(value: str) -> str: ...


@overload
def _v(value: None) -> None: ...


def _v(value):
    """Dereference values (callable).

    Args:
        value (Callable[[], str] | str | None): value

    Returns:
        str | None: value
    """
    return value() if callable(value) else value


def merge_api_doc(root: "Apidoc", child: "Apidoc") -> "Apidoc":
    """Merge api doc.

    Args:
        root (Apidoc): root
        child (Apidoc): child

    Returns:
        Apidoc: api doc
    """
    if (root_params := root.get("params")) is None or (
        child_params := child.get("params")
    ) is None:
        params = root_params or child.get("params")
    else:
        params = root_params.combine(child_params)
    if (root_resp := root.get("responses")) is None or (
        child_resp := child.get("responses")
    ) is None:
        responses = root_resp or child.get("responses")
    else:
        responses = dict["CODES", "Schema"](**root_resp, **child_resp)
    if (root_security := root.get("security")) is None or (
        child_security := child.get("security")
    ) is None:
        security = root_security or child.get("security")
    else:
        security = root_security + child_security

    return Apidoc(
        params=params,
        responses=responses,
        security=security,
        deprecated=root.get("deprecated", False) or child.get("deprecated", False),
    )
