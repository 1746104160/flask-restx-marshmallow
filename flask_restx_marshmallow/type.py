"""Type hints for flask_restx_marshmallow."""

from collections.abc import Callable, Mapping, Sequence
from collections.abc import Set as AbstractSet
from dataclasses import asdict, dataclass
from http import HTTPStatus
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    NamedTuple,
    NotRequired,
    Required,
    Self,
    TypedDict,
    TypeVar,
    cast,
    overload,
    override,
)

from apispec.core import APISpec as OriginalAPISpec
from apispec.core import Components as OriginalComponents
from apispec.ext.marshmallow import MarshmallowPlugin as OriginalMarshmallowPlugin
from apispec.ext.marshmallow.openapi import OpenAPIConverter as OriginalOpenAPIConverter
from apispec.plugin import BasePlugin
from flask_restx.resource import Resource

from flask_restx_marshmallow.enum import Location, ResponseCode

if TYPE_CHECKING:
    from _typeshed import DataclassInstance
    from apispec.ext.marshmallow.schema_resolver import SchemaResolver
    from marshmallow.fields import Field

    from .api import Api
    from .parameter import Parameters
    from .schema import Schema

    class GenericParameters[T: DataclassInstance](Parameters):
        """Generic parameters."""

        @overload
        def load(
            self: Self,
            data: Mapping,
            *,
            many: bool,
            partial: bool | Sequence[str] | AbstractSet[str] | None = None,
            unknown: str | None = None,
        ) -> list[T]: ...

        @overload
        def load(
            self: Self,
            data: Mapping,
            *,
            partial: bool | Sequence[str] | AbstractSet[str] | None = None,
            unknown: str | None = None,
        ) -> T: ...

        @override
        def load(
            self: Self,
            data: Mapping,
            *,
            many: bool | None = None,
            partial: bool | Sequence[str] | AbstractSet[str] | None = None,
            unknown: str | None = None,
        ) -> T | list[T]: ...

        @overload
        def loads(
            self: Self,
            json_data: str | bytes,
            *,
            many: bool,
            partial: bool | Sequence[str] | AbstractSet[str] | None = None,
            unknown: str | None = None,
            **kwargs,  # noqa: ANN003
        ) -> list[T]: ...

        @overload
        def loads(
            self: Self,
            json_data: str | bytes,
            *,
            partial: bool | Sequence[str] | AbstractSet[str] | None = None,
            unknown: str | None = None,
            **kwargs,  # noqa: ANN003
        ) -> T: ...

        @override
        def loads(
            self: Self,
            json_data: str | bytes,
            *,
            many: bool | None = None,
            partial: bool | Sequence[str] | AbstractSet[str] | None = None,
            unknown: str | None = None,
            **kwargs,
        ) -> T | list[T]: ...


class Result[T](TypedDict):
    """data."""

    items: list[T]
    total: int

    if TYPE_CHECKING:

        @override
        def __init__(self, items: list[T], total: int) -> "Result[T]": ...  # type: ignore[override]


def filter_none(data: Mapping) -> dict:
    """Filter None values.

    Args:
        data (Mapping): data

    Returns:
        dict: filtered data
    """
    return {k: v for k, v in data.items() if v is not None}


class _Success[T](TypedDict):
    """success response."""

    code: ResponseCode
    message: str | None
    result: NotRequired[Result[T] | T]


@dataclass
class Success[T]:
    """success response."""

    code: ResponseCode = ResponseCode.SUCCESS
    message: str | None = None
    result: Result[T] | T | None = None

    def __new__(
        cls,
        code: ResponseCode = ResponseCode.SUCCESS,
        message: str | None = None,
        result: Result[T] | T | None = None,
    ) -> "_Success[T]":
        """Success response."""
        instance = super().__new__(cls)
        instance.code = code
        instance.message = message
        instance.result = result
        return cast("_Success[T]", filter_none(asdict(instance)))

    if TYPE_CHECKING:

        @override
        def __init__(
            self,
            code: ResponseCode = ResponseCode.SUCCESS,
            message: str | None = None,
            result: Result[T] | T | None = None,
        ) -> "_Success[T]": ...  # type: ignore[override]


class _Error(TypedDict):
    """error response."""

    code: ResponseCode
    message: str | Mapping[str, list[str]] | None


@dataclass
class Error:
    """error response."""

    code: ResponseCode = ResponseCode.ERROR
    message: str | Mapping[str, list[str]] | None = None

    def __new__(
        cls,
        code: ResponseCode = ResponseCode.ERROR,
        message: str | Mapping[str, list[str]] | None = None,
    ) -> "_Error":
        """Error response."""
        instance = super().__new__(cls)
        instance.code = code
        instance.message = message
        return cast("_Error", filter_none(asdict(instance)))

    if TYPE_CHECKING:

        @override
        def __init__(
            self,
            code: ResponseCode = ResponseCode.ERROR,
            message: str | Mapping[str, list[str]] | None = None,
        ) -> "_Error": ...  # type: ignore[override]


class _Warn(TypedDict):
    """warning response."""

    code: ResponseCode
    message: str | None


@dataclass
class Warn:
    """warning response."""

    code: ResponseCode = ResponseCode.WARNING
    message: str | None = None

    def __new__(
        cls,
        code: ResponseCode = ResponseCode.WARNING,
        message: str | None = None,
    ) -> "_Warn":
        """Warning response."""
        instance = super().__new__(cls)
        instance.code = code
        instance.message = message
        return cast("_Warn", filter_none(asdict(instance)))

    if TYPE_CHECKING:

        @override
        def __init__(
            self,
            code: ResponseCode = ResponseCode.WARNING,
            message: str | None = None,
        ) -> "_Warn": ...  # type: ignore[override]


class TupleResponse[T](NamedTuple):
    """tuple response."""

    response: Mapping | _Success[T] | _Error | _Warn
    status_code: HTTPStatus | int | None = HTTPStatus.OK
    extra_headers: Mapping[str, str] | None = {}


class SchemaInitKwargs(TypedDict):
    """Schema init kwargs."""

    only: NotRequired[Sequence[str] | AbstractSet[str]]
    exclude: NotRequired[Sequence[str] | AbstractSet[str]]
    many: NotRequired[bool]
    load_only: NotRequired[Sequence[str] | AbstractSet[str]]
    dump_only: NotRequired[Sequence[str] | AbstractSet[str]]
    partial: NotRequired[bool | Sequence[str] | AbstractSet[str]]
    unknown: NotRequired[Literal["exclude", "include", "raise"]]


class FieldLocations(NamedTuple):
    """Non-body Field Locations."""

    name: str
    location: Location
    is_multiple: bool


class ApiInitKwargs[T: Exception](TypedDict):
    """Api init kwargs."""

    auth_decorator: NotRequired[
        Callable[[Callable[["Api"], str]], Callable[["Api"], str]]
    ]
    default_error_handler: Callable[[Exception], TupleResponse]
    error_handlers: Mapping[type[T] | T, Callable[[T], TupleResponse]]


class ApiInitAPPKwargs(TypedDict):
    """Api init_app kwargs."""

    add_specs: bool


class ClassSchemaKwargs(TypedDict):
    """Class schema kwargs."""

    use_origin_load: NotRequired[bool]
    globalns: NotRequired[dict]
    localns: NotRequired[dict]


type PathStr = Annotated[str, "/"]
type ExpressionStr = Annotated[str, "$"]


class Discriminator(TypedDict, total=False):
    """discriminator object."""

    propertyName: Required[str]
    mapping: Mapping[str, str]


class Xml(TypedDict, total=False):
    """xml object."""

    name: str
    namespace: str
    prefix: str
    attribute: bool
    wrapped: bool


class Contact(TypedDict, total=False):
    """contact object."""

    name: str
    url: str
    email: str


class License(TypedDict, total=False):
    """license object."""

    name: Required[str]
    identifier: str
    url: str


class Info(TypedDict, total=False):
    """info object."""

    title: Required[str]
    summary: str
    description: str
    termsOfService: str
    contact: Contact
    license: License
    version: Required[str]


class Variable(TypedDict, total=False):
    """server variable object."""

    enum: list[str]
    default: Required[str]
    description: str


class Server(TypedDict, total=False):
    """server object."""

    url: Required[str]
    description: str
    variables: Mapping[str, Variable]


class ExternalDocs(TypedDict, total=False):
    """External Documentation Object."""

    description: str
    url: Required[str]


class Example[T](TypedDict, total=False):
    """example object."""

    summary: str
    description: str
    value: T
    externalValue: str


A = TypeVar("A")

Reference = TypedDict(
    "Reference",
    {"$ref": str, "summary": NotRequired[str], "description": NotRequired[str]},
)


class OneOf(TypedDict, total=False):
    """oneOf object."""

    const: str
    title: str
    description: str


SwaggerSchema = TypedDict(
    "SwaggerSchema",
    {
        "$ref": str,
        "discriminator": Discriminator,
        "xml": Xml,
        "externalDocs": "ExternalDocs",
        "example": A,
        "examples": Mapping[str, Example[A] | Reference],
        "type": Literal["object", "array", "string", "number", "integer", "boolean"],
        "format": str,
        "required": list[str],
        "properties": Mapping[str, "SwaggerSchema"],
        "oneOf": list[OneOf],
    },
    total=False,
)
Parameter = TypedDict(
    "Parameter",
    {
        "name": Required[str],
        "in": Required[Literal["query", "header", "path", "cookie"]],
        "description": str,
        "required": Required[bool],
        "deprecated": bool,
        "allowEmptyValue": bool,
        "style": str,
        "explode": bool,
        "allowReserved": bool,
        "schema": SwaggerSchema,
        "example": A,
        "examples": Mapping[str, Example[A] | Reference],
    },
    total=False,
)


class Header[T](TypedDict, total=False):
    """header object."""

    description: str
    required: bool
    deprecated: bool
    style: str
    explode: bool
    schema: SwaggerSchema
    example: T
    examples: Mapping[str, Example[T] | Reference]
    content: Mapping[str, "MediaType[T]"]


class Encoding(TypedDict, total=False):
    """encoding object."""

    contentType: str
    headers: Mapping[str, Header | Reference]
    style: str
    explode: bool
    allowReserved: bool


class MediaType[T](TypedDict, total=False):
    """mediaType object."""

    schema: SwaggerSchema
    example: T
    examples: Mapping[str, Example[T] | Reference]
    encoding: Mapping[str, Encoding]


class RequestBody(TypedDict, total=False):
    """requestBody object."""

    description: str
    content: Required[Mapping[str, MediaType]]
    required: bool


class Link[T](TypedDict, total=False):
    """link object."""

    operationRef: str
    operationId: str
    parameters: Mapping[str, ExpressionStr | T]
    requestBody: T | ExpressionStr
    description: str
    server: Server


class SwaggerResponse(TypedDict, total=False):
    """response object."""

    description: Required[str]
    headers: Mapping[str, Header | Reference]
    content: Mapping[str, MediaType]
    links: Mapping[str, Link | Reference]


DefaultResponse = TypedDict(
    "DefaultResponse",
    {
        "default": Required[SwaggerResponse | Reference],
        "100": SwaggerResponse | Reference,
        "101": SwaggerResponse | Reference,
        "102": SwaggerResponse | Reference,
        "103": SwaggerResponse | Reference,
        "200": SwaggerResponse | Reference,
        "201": SwaggerResponse | Reference,
        "202": SwaggerResponse | Reference,
        "203": SwaggerResponse | Reference,
        "204": SwaggerResponse | Reference,
        "205": SwaggerResponse | Reference,
        "206": SwaggerResponse | Reference,
        "207": SwaggerResponse | Reference,
        "208": SwaggerResponse | Reference,
        "226": SwaggerResponse | Reference,
        "300": SwaggerResponse | Reference,
        "301": SwaggerResponse | Reference,
        "302": SwaggerResponse | Reference,
        "303": SwaggerResponse | Reference,
        "304": SwaggerResponse | Reference,
        "305": SwaggerResponse | Reference,
        "307": SwaggerResponse | Reference,
        "308": SwaggerResponse | Reference,
        "400": SwaggerResponse | Reference,
        "401": SwaggerResponse | Reference,
        "402": SwaggerResponse | Reference,
        "403": SwaggerResponse | Reference,
        "404": SwaggerResponse | Reference,
        "405": SwaggerResponse | Reference,
        "406": SwaggerResponse | Reference,
        "407": SwaggerResponse | Reference,
        "408": SwaggerResponse | Reference,
        "409": SwaggerResponse | Reference,
        "410": SwaggerResponse | Reference,
        "411": SwaggerResponse | Reference,
        "412": SwaggerResponse | Reference,
        "413": SwaggerResponse | Reference,
        "414": SwaggerResponse | Reference,
        "415": SwaggerResponse | Reference,
        "416": SwaggerResponse | Reference,
        "417": SwaggerResponse | Reference,
        "418": SwaggerResponse | Reference,
        "421": SwaggerResponse | Reference,
        "422": SwaggerResponse | Reference,
        "423": SwaggerResponse | Reference,
        "424": SwaggerResponse | Reference,
        "425": SwaggerResponse | Reference,
        "426": SwaggerResponse | Reference,
        "428": SwaggerResponse | Reference,
        "429": SwaggerResponse | Reference,
        "431": SwaggerResponse | Reference,
        "451": SwaggerResponse | Reference,
        "500": SwaggerResponse | Reference,
        "501": SwaggerResponse | Reference,
        "502": SwaggerResponse | Reference,
        "503": SwaggerResponse | Reference,
        "504": SwaggerResponse | Reference,
        "505": SwaggerResponse | Reference,
        "506": SwaggerResponse | Reference,
        "507": SwaggerResponse | Reference,
        "508": SwaggerResponse | Reference,
        "510": SwaggerResponse | Reference,
        "511": SwaggerResponse | Reference,
    },
    total=False,
)
type CODES = Literal[
    "default",
    "100",
    "101",
    "102",
    "103",
    "200",
    "201",
    "202",
    "203",
    "204",
    "205",
    "206",
    "207",
    "208",
    "226",
    "300",
    "301",
    "302",
    "303",
    "304",
    "305",
    "307",
    "308",
    "400",
    "401",
    "402",
    "403",
    "404",
    "405",
    "406",
    "407",
    "408",
    "409",
    "410",
    "411",
    "412",
    "413",
    "414",
    "415",
    "416",
    "417",
    "418",
    "421",
    "422",
    "423",
    "424",
    "425",
    "426",
    "428",
    "429",
    "431",
    "451",
    "500",
    "501",
    "502",
    "503",
    "504",
    "505",
    "506",
    "507",
    "508",
    "510",
    "511",
]

type Callback = Mapping[ExpressionStr, PathItem]
type Security = Mapping[str, list[str]]


class Operation(TypedDict, total=False):
    """operation object."""

    tags: list[str]
    summary: str
    description: str
    externalDocs: ExternalDocs
    operationId: str
    parameters: list[Parameter | Reference]
    requestBody: RequestBody | Reference
    responses: DefaultResponse
    callbacks: Mapping[str, Callback | Reference]
    deprecated: bool
    security: list[Security]
    servers: list[Server]


type Method = Literal[
    "get",
    "put",
    "post",
    "delete",
    "options",
    "head",
    "patch",
    "trace",
]

PathItem = TypedDict(
    "PathItem",
    {
        "$ref": str,
        "summary": str,
        "description": str,
        "get": Operation,
        "put": Operation,
        "post": Operation,
        "delete": Operation,
        "options": Operation,
        "head": Operation,
        "patch": Operation,
        "trace": Operation,
        "servers": list[Server],
        "parameters": list[Parameter | Reference],
    },
    total=False,
)


class OAuthFlow(TypedDict, total=False):
    """oauth flow object."""

    authorizationUrl: Required[str]
    tokenUrl: Required[str]
    refreshUrl: str
    scopes: Required[Mapping[str, str]]


class OAuthFlows(TypedDict, total=False):
    """oauth flows object."""

    implicit: OAuthFlow
    password: OAuthFlow
    clientCredentials: OAuthFlow
    authorizationCode: OAuthFlow


ApiKeySecurityScheme = TypedDict(
    "ApiKeySecurityScheme",
    {
        "type": Literal["apiKey"],
        "description": NotRequired[str],
        "name": str,
        "in": Literal["query", "header", "cookie"],
    },
)


class HttpSecurityScheme(TypedDict, total=False):
    """http security scheme object."""

    type: Required[Literal["http"]]
    description: str
    scheme: Required[str]
    bearerFormat: str


class OAuth2SecurityScheme(TypedDict, total=False):
    """oauth2 security scheme object."""

    type: Literal["oauth2"]
    description: str
    flows: Required[OAuthFlows]


class OpenIdConnectSecurityScheme(TypedDict, total=False):
    """openIdConnect security scheme object."""

    type: Literal["openIdConnect"]
    description: str
    openIdConnectUrl: Required[str]


class MutualTLSSecurityScheme(TypedDict, total=False):
    """mutualTLS security scheme object."""

    type: Literal["mutualTLS"]
    description: str


class Components(TypedDict, total=False):
    """components object."""

    schemas: Mapping[str, SwaggerSchema]
    responses: Mapping[str, SwaggerResponse | Reference]
    parameters: Mapping[str, Parameter | Reference]
    examples: Mapping[str, Example | Reference]
    requestBodies: Mapping[str, RequestBody | Reference]
    headers: Mapping[str, Header | Reference]
    securitySchemes: Mapping[
        str,
        ApiKeySecurityScheme
        | HttpSecurityScheme
        | OAuth2SecurityScheme
        | OpenIdConnectSecurityScheme
        | MutualTLSSecurityScheme
        | Reference,
    ]
    links: Mapping[str, Link | Reference]
    callbacks: Mapping[str, Callback | Reference]
    pathItems: Mapping[str, PathItem | Reference]


class Tag(TypedDict, total=False):
    """tag object."""

    name: Required[str]
    description: str
    externalDocs: ExternalDocs


class OpenAPI(TypedDict, total=False):
    """openapi object."""

    openapi: Required[str]
    info: Required[Info]
    jsonSchemaDialect: str
    servers: list[Server]
    paths: Mapping[PathStr, PathItem]
    webhooks: Mapping[str, PathItem]
    components: Components
    security: list[Security]
    tags: list[Tag]
    externalDocs: ExternalDocs


class Apidoc(TypedDict, total=False):
    """__apidoc__ values."""

    params: "Parameters | None"
    responses: Mapping[CODES, "Schema"] | None
    security: list[Security] | None
    deprecated: bool | None


class ResourceRoute(NamedTuple):
    """Resource route."""

    resource: type[Resource]
    urls: list[str]
    route_doc: Apidoc | None
    kwargs: dict


class APISpecComponents(OriginalComponents):
    """Stores components that describe objects used in the API."""

    if TYPE_CHECKING:

        @override
        def security_scheme(
            self,
            component_id: str,
            component: ApiKeySecurityScheme
            | HttpSecurityScheme
            | OAuth2SecurityScheme
            | OpenIdConnectSecurityScheme
            | MutualTLSSecurityScheme,
        ) -> Self: ...


class OpenAPIConverter(OriginalOpenAPIConverter):
    """Patched OpenAPIConverter.

    Adds methods for generating OpenAPI specification from marshmallow schemas and
    fields.
    """

    if TYPE_CHECKING:

        @override
        def _field2parameter(
            self,
            field: Field,
            *,
            name: str,
            location: str,
        ) -> Parameter: ...

        @override
        def resolve_nested_schema[T: Schema](
            self,
            schema: type[T] | T | str,
        ) -> SwaggerSchema: ...

        @override
        def field2property(self, field: Field) -> SwaggerSchema: ...


class MarshmallowPlugin(OriginalMarshmallowPlugin):
    """APISpec plugin for translating marshmallow schemas to OpenAPI format."""

    if TYPE_CHECKING:
        resolver: SchemaResolver
        converter: OpenAPIConverter


class APISpec(OriginalAPISpec):
    """Stores metadata that describes a RESTful API using the OpenAPI specification.

    Args:
        title (str): API title
        version (str): API version
        plugins (Iterable[Plugin]): Plugin instances. See https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#infoObject
        openapi_version (str): OpenAPI Specification version. Should be in the form '2.x' or '3.x.x' to comply with the OpenAPI standard.
        options: Optional top-level keys See https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#openapi-object

    """  # noqa: E501

    @override
    def __init__(
        self,
        title: str,
        version: str,
        openapi_version: str,
        plugins: Sequence[BasePlugin] = (),
        **options: Any,
    ) -> None:
        """Stores metadata that describes a RESTful API using the OpenAPI specification.

        Args:
            title (str): API title
            version (str): API version
            plugins (Iterable[Plugin]): Plugin instances. See https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#infoObject.
            openapi_version (str): OpenAPI Specification version. Should be in the form\
                '2.x' or '3.x.x' to comply with the OpenAPI standard.
            options: Optional top-level keys See https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#openapi-object

        """
        super().__init__(title, version, openapi_version, plugins, **options)
        self.components = APISpecComponents(
            plugins=self.plugins,
            openapi_version=self.openapi_version,
        )

    if TYPE_CHECKING:
        _tags: list[Tag]
        _paths: Mapping[str, PathItem]

        @override
        def tag(self, tag: "Tag") -> Self: ...

        @override
        def path(
            self,
            path: str | None = None,
            *,
            operations: Mapping[Method, Operation] | None = None,
            summary: str | None = None,
            description: str | None = None,
            parameters: list[Parameter | Reference] | None = None,
            **kwargs,  # noqa: ANN003
        ) -> Self: ...

    @property
    def tags(self) -> list[Tag]:
        """Get tags."""
        return self._tags

    @property
    def paths(self) -> Mapping[str, PathItem]:
        """Get paths."""
        return self._paths
