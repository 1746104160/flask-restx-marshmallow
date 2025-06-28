"""utils of flask_restx_marshmallow."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import field, make_dataclass
from http import HTTPStatus
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING, NoReturn, Self, Unpack, cast, overload

from apispec.ext.marshmallow.common import resolve_schema_cls
from flask.globals import current_app
from flask.templating import render_template
from flask.wrappers import Request as RequestBase
from flask.wrappers import Response as ResponseBase
from marshmallow.fields import Integer, List, Tuple
from marshmallow_dataclass import class_schema as marshmallow_dataclass_class_schema
from requests import ReadTimeout, get
from werkzeug.exceptions import UnprocessableEntity

from flask_restx_marshmallow._json import json
from flask_restx_marshmallow.schema import Schema
from flask_restx_marshmallow.type import (
    ApiKeySecurityScheme,
    Error,
    HttpSecurityScheme,
    Location,
    MutualTLSSecurityScheme,
    OAuth2SecurityScheme,
    OpenIdConnectSecurityScheme,
    ResponseCode,
    Security,
    Success,
    Tag,
    TupleResponse,
)

try:
    from loguru import logger
except ImportError:
    from logging import getLogger

    logger = getLogger(__name__)
if TYPE_CHECKING:
    from marshmallow import ValidationError
    from marshmallow.fields import Field
    from marshmallow.schema import Schema as Schema_
    from werkzeug.exceptions import BadRequest

    from .api import Api
    from .parameter import Parameters
    from .type import ClassSchemaKwargs, DataclassInstance, GenericParameters


class Response(ResponseBase):
    """The response object that is used by default in this project."""

    json_module = json


class Request(RequestBase):
    """The request object that is used by default in this project."""

    json_module = json


class classproperty[T]:  # noqa: N801
    """Class property."""

    def __init__(self: Self, func: Callable[..., T]) -> None:
        """Initialize class property.

        Args:
            func (Callable[P, T]): function get
        """
        self.fget = func
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__
        self.slot_name = f"_class_{self.__name__}"
        self.__module__ = func.__module__

    if TYPE_CHECKING:

        @overload
        def __get__(self: Self, instance: None, owner: type[object]) -> T: ...

        @overload
        def __get__(self: Self, instance: object, owner: type[object]) -> T: ...

    def __get__(self: Self, instance, owner) -> T:
        """Get the value.

        Args:
            instance (object): instance
            owner (type[object]): owner

        Returns:
            T: value
        """
        return classmethod(self.fget).__get__(None, owner)()


def schema_name_resolver[T: Schema_](schema: type[T]) -> str:
    """Resolve schema name.

    Args:
        schema (type[Schema]): schema class

    Returns:
        str: schema name
    """
    return cast("type[T]", resolve_schema_cls(schema)).__name__


def download_files(current_version: str, filename: str) -> None:
    """Retrieve swagger ui files."""
    with Path(Path(__file__).parent, "static", filename).open("wb") as f:
        try:
            res = get(
                f"https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/{current_version}/{filename}",
                timeout=5,
            ).content
            f.write(res)
        except (ConnectionError, ReadTimeout):
            copyfile(
                Path(Path(__file__).parent, "static", f"{filename}.bak"),
                Path(Path(__file__).parent, "static", filename),
            )


def raise_validation_error(
    error: "ValidationError",
    _req: "Request",
    _schema: "Parameters",
    error_status_code: int | HTTPStatus | None = None,  # noqa: ARG001
    error_headers: dict | None = None,  # noqa: ARG001
) -> NoReturn:
    """Validation error.

    Args:
        error (ValidationError): validation error
        _req (Request): request
        _schema (Parameters): schema
        error_status_code (int | HTTPStatus | None, optional): error status code. Defaults to None.
        error_headers (dict | None, optional): error headers. Defaults to None.

    Raises:
        UnprocessableEntity: validation error
    """  # noqa: E501
    raise UnprocessableEntity(
        description=cast("dict", error.messages).get("auto", error.messages),
    )


def handle_validation_error(
    error: "UnprocessableEntity | None" = None,
) -> TupleResponse:
    """Validation error.

    Returns:
        TupleResponse: response
    """
    return TupleResponse(
        response=Error(message=(error or UnprocessableEntity()).description),
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    )


def handle_invalid_json_error(err: "BadRequest | None" = None) -> TupleResponse:
    """Bad request.

    Args:
        err (BadRequest, optional): bad request. Defaults to None.

    Returns:
        TupleResponse: response
    """
    return TupleResponse(
        response=Error(message=getattr(err, "description", None)),
        status_code=HTTPStatus.BAD_REQUEST,
    )


def handle_parse_validation_error(
    err: "ValidationError",
    *_args,  # noqa: ANN002
    **_kwargs,  # noqa: ANN003
) -> "NoReturn":
    """Handles a Marshmallow ValidationError.

    By attaching a standardized error response and re-raising the exception.

    Args:
        err (ValidationError): The validation error instance to handle.
    """
    err.data = Error(
        code=ResponseCode.ERROR,
        message=next(iter(cast("dict", err.messages).values())),
    )
    raise err


def render_swagger_ui(api: "Api") -> str:
    """Render a SwaggerUI for a given API.

    Args:
        api (Api): api object

    Returns:
        str: render result
    """
    if base := current_app.config.get("SWAGGER_UI_BASE_URL"):
        return render_template(
            "index.html.j2",
            base_url=base,
            csrf_token_cookie_name=current_app.config.get(
                "CSRF_COOKIE_NAME",
                "csrf_token",
            ),
            specs_url=api.specs_url,
            title=api.title,
        )
    if (
        current_version := current_app.config.get("SWAGGER_UI_VERSION")
    ) is None and current_app.config.get("SWAGGER_UI_USE_CDN") is True:
        try:
            from bs4 import BeautifulSoup  # noqa: PLC0415
            from bs4 import Tag as Tag_  # noqa: PLC0415

            if (
                page := get("https://cdnjs.com/libraries/swagger-ui", timeout=5)
            ).status_code == HTTPStatus.OK.value:
                current_version = json.loads(
                    str(
                        cast(
                            "Tag_",
                            BeautifulSoup(page.content, "html.parser").find(
                                attrs={"type": "application/ld+json"},
                            ),
                        ).contents[0],
                    ),
                )["softwareVersion"]
        except ImportError:
            logger.warning(
                "Extra package 'beautifulsoup4' not found! Use local swagger.",
            )
        except (ConnectionError, ReadTimeout):
            logger.info("Failed to get swagger-ui version. Use local swagger.")
    if (
        current_version is not None
        and current_app.config.get("SWAGGER_UI_USE_CDN") is True
    ):
        if current_app.config.get("SWAGGER_UI_DOWNLOAD_UPDATES") is True:
            download_files(current_version, "swagger-ui-bundle.min.js")
            download_files(current_version, "swagger-ui-standalone-preset.min.js")
            download_files(current_version, "swagger-ui.min.css")
        return render_template(
            "index.html.j2",
            base_url=current_app.config.get(
                "SWAGGER_UI_CDN_URL",
                f"{current_app.config.get('SWAGGER_UI_CDN_BASE')}/{current_version}",
            ),
            csrf_token_cookie_name=current_app.config.get(
                "CSRF_COOKIE_NAME",
                "csrf_token",
            ),
            specs_url=api.specs_url,
            title=api.title,
        )
    return render_template(
        "local.html.j2",
        csrf_token_cookie_name=current_app.config.get("CSRF_COOKIE_NAME", "csrf_token"),
        specs_url=api.specs_url,
        title=api.title,
    )


def render_swagger_json(api: "Api") -> str | bytes:
    """Render a Swagger Json for a given API.

    Args:
        api (Api): api object

    Returns:
        str: render result
    """
    return json.dumps(api.__schema__)


def security_helper[A, S: str | Mapping[str, list[str] | str]](
    security: S | Sequence[S] | A,  # type: ignore[valid-type]
) -> "Security":
    """Security helper.

    Args:
        security (str | Mapping[str, list[str] | str]): security name or instance.

    Raises:
        TypeError: if security is not str or Mapping.

    Returns:
        Security: security form value.
    """
    if isinstance(security, str):
        return {security: []}
    if isinstance(security, Mapping):
        security_key = next(iter(security))
        if not isinstance(
            security_value := security[security_key],
            str | list,
        ) or not all(
            isinstance(security_value_inner, str)
            for security_value_inner in security_value
        ):
            msg = "security value must be str or list[str]."
            raise TypeError(msg)
        return {
            security_key: security_value
            if isinstance(security_value, list)
            else [security_value],
        }
    msg = f"security must be str or Mapping, got {type(security).__name__}"
    raise TypeError(msg)


def authorization_helper(  # noqa: C901, PLR0912
    authorization: Mapping[str, Mapping] | None,
) -> dict[
    str,
    ApiKeySecurityScheme
    | HttpSecurityScheme
    | OAuth2SecurityScheme
    | OpenIdConnectSecurityScheme
    | MutualTLSSecurityScheme,
]:
    """Authorization helper.

    Args:
        authorization (Mapping): authorization

    Raises:
        TypeError: if authorization is not Mapping
        ValueError: if required fields are missing

    Returns:
        dict[str, ApiKeySecurityScheme | HttpSecurityScheme | OAuth2SecurityScheme | OpenIdConnectSecurityScheme | MutualTLSSecurityScheme]: security scheme
    """  # noqa: E501
    if authorization is None:
        return {}
    if not isinstance(authorization, Mapping) or not all(
        isinstance(s, Mapping) for s in authorization.values()
    ):
        msg = "authorization must be Mapping[str, Mapping]"
        raise TypeError(msg)
    authorization_ = dict[
        str,
        ApiKeySecurityScheme
        | HttpSecurityScheme
        | OAuth2SecurityScheme
        | OpenIdConnectSecurityScheme
        | MutualTLSSecurityScheme,
    ]()
    for name, security_scheme in authorization.items():
        match security_scheme.get("type"):
            case "apiKey":
                authorization_[name] = {
                    "type": "apiKey",
                    "in": security_scheme.get("in", "header"),
                    "name": security_scheme.get("name", "Authorization"),
                }
                if (description := security_scheme.get("description")) and isinstance(
                    description,
                    str,
                ):
                    authorization_[name]["description"] = description
            case "http":
                http_ = HttpSecurityScheme(
                    type="http",
                    scheme=security_scheme.get("scheme", "bearer"),
                )
                if (description := security_scheme.get("description")) and isinstance(
                    description,
                    str,
                ):
                    http_["description"] = description
                if (
                    bearer_format := security_scheme.get("bearerFormat")
                ) and isinstance(bearer_format, str):
                    http_["bearerFormat"] = bearer_format
                authorization_[name] = http_
            case "oauth2":
                if (flows := security_scheme.get("flows")) is None:
                    msg = "flows is required."
                    raise ValueError(msg)
                authorization_[name] = OAuth2SecurityScheme(type="oauth2", flows=flows)
                if (description := security_scheme.get("description")) and isinstance(
                    description,
                    str,
                ):
                    authorization_[name]["description"] = description
            case "openIdConnect":
                if (url := security_scheme.get("openIdConnectUrl")) is None:
                    msg = "openIdConnectUrl is required."
                    raise ValueError(msg)
                authorization_[name] = OpenIdConnectSecurityScheme(
                    type="openIdConnect",
                    openIdConnectUrl=url,
                )
                if (description := security_scheme.get("description")) and isinstance(
                    description,
                    str,
                ):
                    authorization_[name]["description"] = description
            case "mutualTLS":
                authorization_[name] = MutualTLSSecurityScheme(type="mutualTLS")
                if (description := security_scheme.get("description")) and isinstance(
                    description,
                    str,
                ):
                    authorization_[name]["description"] = description
    return authorization_


def tag_helper(tag: Sequence[str] | str | dict | None) -> Tag:
    """Tag helper.

    Args:
        tag (Sequence[str] | str | dict | None): tag

    Raises:
        ValueError: Unsupported tag format.

    Returns:
        Tag: tag
    """
    if isinstance(tag, str):
        return Tag(name=tag)
    if isinstance(tag, dict) and "name" in tag:
        return Tag(**tag)
    if (
        isinstance(tag, Sequence)
        and isinstance(name_ := next(iter(tag)), str)
        and isinstance(description_ := next(iter(tag)), str)
    ):
        return Tag(name=name_, description=description_)
    msg = f"Unsupported tag format for {tag}"
    raise ValueError(msg)


def output_json(
    data: dict | str | bytes,
    code: int | HTTPStatus,
    headers: dict | None = None,
) -> Response:
    """Makes a Flask response with a JSON encoded body.

    Args:
        data (dict | str | bytes): data
        code (int | HTTPStatus): code
        headers (dict, optional): headers. Defaults to None.

    Returns:
        Response: response
    """
    dumped = (
        dumps
        if isinstance(
            (dumps := (json.dumps(data) if isinstance(data, dict) else data)),
            str,
        )
        else cast("bytes", dumps).decode()
    ) + "\n"
    return Response(
        response=dumped,
        status=code,
        headers=headers,
        mimetype="application/json",
    )


def get_location(field: "Field") -> Location | None:
    """Get location.

    Args:
        field (Field): field

    Returns:
        Location: location
    """
    if not isinstance(field, List | Tuple):
        if isinstance(location := field.metadata.get("location"), str):
            location = Location(location)
        return location
    if isinstance(field, List):
        return get_location(cast("Field", field.inner))
    return get_location(cast("Field", field.tuple_fields[0]))


def set_location(field: "Field", location: Location) -> None:
    """Set location.

    Args:
        field (Field): field
        location (Location): location
    """
    if not isinstance(field, List | Tuple):
        cast("dict", field.metadata).setdefault("location", location)
    elif isinstance(field, List):
        set_location(cast("Field", field.inner), location)
    else:
        for tuple_field in cast("list[Field]", field.tuple_fields):
            set_location(cast("Field", tuple_field), location)


@overload
def class_schema[C: "DataclassInstance", B: "Schema"](
    clazz: type[C],
    *,
    base: type[B],
    **kwargs: "Unpack[ClassSchemaKwargs]",
) -> type[B]: ...


@overload
def class_schema[C: "DataclassInstance", B: "Parameters"](
    clazz: type[C],
    *,
    base: type[B],
    **kwargs: "Unpack[ClassSchemaKwargs]",
) -> "type[GenericParameters[C]]": ...


def class_schema(clazz, base, *, use_origin_load=False, **kwargs):
    """Class schema.

    Args:
        clazz (type[dataclass]): dataclass type
        base (type[Schema | Parameters], optional): base schema class. Defaults to None.
        use_origin_load (bool, optional): use origin load. Defaults to False.
        **kwargs (Unpack[ClassSchemaKwargs]): kwargs

    Returns:
        Schema | Parameters: schema or parameters for annotations
    """
    schema = marshmallow_dataclass_class_schema(clazz, base, **kwargs)
    if not schema.__name__.endswith("Schema") and not schema.__name__.endswith(
        "Parameters",
    ):
        schema.__name__ = (
            f"{clazz.__name__}Schema"
            if issubclass(base, Schema)
            else f"{clazz.__name__}Parameters"
        )
    if use_origin_load:
        schema.load = base.load  # type: ignore[attr-defined]
    return schema


def unpack[T](
    response: TupleResponse
    | T
    | tuple[T]
    | tuple[T, int | HTTPStatus]
    | tuple[T, int | HTTPStatus, dict],
    default_code: HTTPStatus | int = HTTPStatus.OK,
) -> TupleResponse:
    """Unpack a Flask standard response.

    Args:
        response (T | tuple[T] | tuple[T, int | HTTPStatus] | tuple[T, int | HTTPStatus, dict]): response
        default_code (HTTPStatus | int, optional): default code. Defaults to HTTPStatus.OK.

    Raises:
        ValueError: if the response does not have one of the expected format

    Returns:
        TupleResponse: a 3-tuple ``(data, code, headers)
    """  # noqa: E501
    if isinstance(response, TupleResponse):
        return response
    if not isinstance(response, tuple):
        return TupleResponse(Success(result=response), default_code, {})
    if len(response) == 1:
        return TupleResponse(Success(result=response[0]), default_code, {})
    if len(response) == 2:  # noqa: PLR2004
        data, code = response
        return TupleResponse(Success(result=data), code, {})
    if len(response) == 3:  # noqa: PLR2004
        data, code, headers = response
        return TupleResponse(Success(result=data), code, headers)
    msg = "Too many response values"
    raise ValueError(msg)


def make_default_schema(
    name: str,
    *,
    success: bool = True,
    code: HTTPStatus | int = HTTPStatus.OK,
    message: str | None = None,
) -> type["Schema"]:
    """Make standard schema.

    Args:
        name (str): name
        success (bool, optional): success. Defaults to True.
        code (HTTPStatus | int, optional): code. Defaults to HTTPStatus.OK.
        message (str | None, optional): message. Defaults to None.

    Returns:
        type[Schema]: schema
    """
    return class_schema(
        make_dataclass(
            name,
            [
                (
                    "code",
                    ResponseCode,
                    field(
                        default=ResponseCode.SUCCESS
                        if success is True
                        else ResponseCode.ERROR
                        if success is False
                        else code,
                        metadata={
                            "by_value": Integer,
                            "metadata": {
                                "description": "response code",
                                "example": ResponseCode.SUCCESS
                                if success is True
                                else ResponseCode.ERROR
                                if success is False
                                else code,
                            },
                        },
                    ),
                ),
                (
                    "message",
                    str | None,
                    field(
                        default=message
                        or (
                            code.description
                            if isinstance(code, HTTPStatus)
                            and code is not HTTPStatus.OK
                            else None
                        )
                        or ("Request success" if success is True else "Request failed"),
                        metadata={
                            "metadata": {
                                "description": "response message",
                                "example": message
                                or (
                                    code.description
                                    if isinstance(code, HTTPStatus)
                                    and code is not HTTPStatus.OK
                                    else None
                                )
                                or (
                                    "Request success"
                                    if success is True
                                    else "Request failed"
                                ),
                            },
                        },
                    ),
                ),
            ],
        ),
        base=Schema,
    )
