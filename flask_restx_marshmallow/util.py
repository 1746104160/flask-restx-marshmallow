"""
Description: utils of flask_restx_marshmallow
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-02 13:25:40
FilePath: /flask_restx_marshmallow/flask_restx_marshmallow/util.py
"""
import importlib
import re
from datetime import timedelta
from functools import wraps
from http import HTTPStatus
from io import BytesIO
from types import ModuleType
from typing import Iterable, Literal, Optional

import filetype
import marshmallow
import redis
import requests
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from bs4 import BeautifulSoup, Tag
from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    render_template,
    url_for,
)
from flask_jwt_extended import get_current_user, verify_jwt_in_request
from marshmallow import Schema, missing
from marshmallow.fields import (
    IP,
    URL,
    UUID,
    AwareDateTime,
    Bool,
    Boolean,
    Constant,
    Date,
    DateTime,
    Decimal,
    Dict,
    Email,
    Field,
    Float,
    Int,
    Integer,
    IPv4,
    IPv4Interface,
    IPv6,
    IPv6Interface,
    List,
    NaiveDateTime,
    Number,
    Str,
    String,
    Time,
    TimeDelta,
    Url,
)
from sortedcontainers import SortedDict
from werkzeug.datastructures import FileStorage

import flask_restx_marshmallow

try:
    json: ModuleType = importlib.import_module("orjson")
except ModuleNotFoundError:
    json = importlib.import_module("json")


class File(Field):
    """
    Author: 1746104160
    msg: check file upload type
    """

    default_error_messages: dict[str, str] = {
        "invalid": "Not a valid file.",
        "invalid_mimetype": "{mimetype} is not a valid mimetype.",
        "invalid_size": "File size is too large for {text}.",
    }

    size_name: tuple[
        Literal["B"],
        Literal["KB"],
        Literal["MB"],
        Literal["GB"],
    ] = ("B", "KB", "MB", "GB")

    mimes: set[str] = {
        "application",
        "audio",
        "font",
        "image",
        "model",
        "text",
        "video",
    }

    def __init__(
        self,
        *,
        mimetypes: Optional[str | Iterable[str]] = None,
        size: Optional[int | float] = None,
        size_unit: str = "MB",
        **kwargs,
    ) -> None:
        """initialize file type

        Args:
            mimetypes (Iterable[str], optional): accept mimetype or iterable mimetypes
            like `image/png|image|image/*`. Defaults to None.
            size (Union[int, float], optional): maximum size to upload. Defaults to None.
            size_unit (str, optional): size unit like m|mb|M|MB|. Defaults to "MB".
        """
        super().__init__(**kwargs)
        if mimetypes is not None:
            if isinstance(mimetypes, str):
                self.mimetypes = {mimetypes}
                mimetype_begin: str = mimetypes.split("/")[0].lower()
                assert mimetype_begin in self.mimes
                self.mimetypes: set[str] = {mimetypes}
            else:
                assert isinstance(mimetypes, (list, tuple, set))
                assert all(isinstance(mimetype, str) for mimetype in mimetypes)
                assert {
                    mimetype.split("/")[0].lower() for mimetype in mimetypes
                } < self.mimes
                self.mimetypes = mimetypes
        if size is not None:
            assert size > 0 and isinstance(size, (int, float))
            size_unit: str = (
                upper if "B" in (upper := size_unit.upper()) else upper + "B"
            )
            assert size_unit in self.size_name
            self.size: int | float = size * 1024 ** self.size_name.index(
                size_unit
            )
            self.size_text: str = f"{size:.2f}{size_unit}"

    def _deserialize(
        self, value: FileStorage, *_args, **_kwargs
    ) -> FileStorage:
        """protected method for deserializing the value

        Args:
            value (FileStorage): file

        Raises:
            ValidationError: invalid file

        Returns:
            FileStorage: file
        """
        if not isinstance(value, FileStorage):
            raise self.make_error("invalid file")
        byte_value: bytes = value.stream.read()
        file_mime = (
            res.mime
            if (res := filetype.guess(byte_value)) is not None
            else value.mimetype
        )
        if getattr(self, "mimetypes") is not None and not any(
            re.match(
                re.compile(mimetype, re.IGNORECASE),
                file_mime,
            )
            for mimetype in self.mimetypes
        ):
            raise self.make_error("invalid_mimetype", mimetype=value.mimetype)

        if (
            getattr(self, "size") is not None
            and len(value.stream.read()) > self.size
        ):
            raise self.make_error("invalid_size", text=self.size_text)
        value.stream = BytesIO(byte_value)
        return value


class ObjectDict(SortedDict):
    """
    Author: 1746104160
    msg: sortable object-like dict
    """

    def __str__(self) -> str:
        return json.dumps(self)

    def __getattr__(self, key):
        return self.get(key)


class Apidoc(Blueprint):
    """
    Author: 1746104160
    msg: blueprint for swagger ui
    """

    def __init__(self, *args, **kwargs) -> None:
        self.registered: bool = False
        super().__init__(*args, **kwargs)

    def register(self, *args, **kwargs) -> None:
        super().register(*args, **kwargs)
        self.registered = True


API_DEFAULT_HTTP_CODE_MESSAGES: dict[int, str] = {
    HTTPStatus.UNAUTHORIZED.value: "unauthorized",
    HTTPStatus.FORBIDDEN.value: "forbidden",
    HTTPStatus.UNPROCESSABLE_ENTITY.value: "unprocessable parameters",
    HTTPStatus.NOT_FOUND.value: "not found",
    HTTPStatus.METHOD_NOT_ALLOWED.value: "method not allowed",
    HTTPStatus.INTERNAL_SERVER_ERROR.value: "internal server error",
    HTTPStatus.SERVICE_UNAVAILABLE.value: "service is unavailable now",
    HTTPStatus.TOO_MANY_REQUESTS.value: "too many requests",
    HTTPStatus.BAD_REQUEST.value: "bad request",
}
DEFAULT_FIELD_MAPPING: dict[type, str] = {
    Int: "integer",
    Integer: "integer",
    Constant: "integer",
    Number: "number",
    Float: "number",
    Decimal: "number",
    String: "string",
    Str: "string",
    Boolean: "boolean",
    Bool: "boolean",
    UUID: "uuid",
    DateTime: "date-time",
    AwareDateTime: "date-time",
    NaiveDateTime: "date-time",
    Date: "string",
    Time: "string",
    TimeDelta: "integer",
    Email: "string",
    URL: "string",
    Url: "string",
    Dict: "object",
    List: "array",
    Field: "string",
    File: "file",
    IP: "string",
    IPv4: "string",
    IPv6: "string",
    IPv4Interface: "string",
    IPv6Interface: "string",
}


def resolver(_: type[Schema]) -> str:
    """return none to avoid bug"""
    return ""


def get_default(field: Field) -> str | list[str] | None:
    """get default value

    Args:
        field (Field): field object

    Returns:
        str | list[str] | None: default value
    """
    if (
        marshmallow.__version__ < "3.19.0"
        and (default := getattr(field, "default", None)) is not None
        and not isinstance(default, type(missing))
    ):
        return default
    if (
        marshmallow.__version__ < "3.19.0"
        and (default := getattr(field, "load_default", None)) is not None
        and not isinstance(default, type(missing))
    ):
        return default
    if (
        default := getattr(field.metadata, "default", None)
    ) is not None and not isinstance(default, type(missing)):
        return default
    if (
        default := getattr(field.metadata, "load_default", None)
    ) is not None and not isinstance(default, type(missing)):
        return default
    return None


def get_description(field: Field) -> str | None:
    """get description value

    Args:
        field (Field): field object

    Returns:
        str | None: description value
    """
    if (
        marshmallow.__version__ < "3.19.0"
        and (description := getattr(field, "description", None)) is not None
        and not isinstance(description, type(missing))
    ):
        return description
    if (
        description := getattr(field.metadata, "description", None)
    ) is not None and not isinstance(description, type(missing)):
        return description
    return None


def permission_required(
    route: str,
    *,
    user_authed_routes_attr_name: Optional[str] = "routes",
    optional: bool = False,
) -> None:
    """verify interface permission

    Args:
        route (str): authorized route
        user_routes_attr_name (str, optional): user model attribute name
        for authorized routes. Defaults to "routes".
    """

    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs) -> Response:
            verify_jwt_in_request(optional=optional)
            try:
                current_user = get_current_user()
                if any(
                    re.match(route, route_name) or route.startswith(route_name)
                    for route_name in getattr(
                        current_user, user_authed_routes_attr_name
                    )
                ):
                    return current_app.ensure_sync(func)(*args, **kwargs)
                res: Response = jsonify(
                    {
                        "code": HTTPStatus.FORBIDDEN.value,
                        "message": f"no permission to access {route}",
                        "success": False,
                    }
                )
                res.status_code = HTTPStatus.FORBIDDEN.value
                return res
            except RuntimeError:
                if optional:
                    return current_app.ensure_sync(func)(*args, **kwargs)

        return decorator

    return wrapper


def ui_for(api: "flask_restx_marshmallow.Api") -> str | None:
    """Render a SwaggerUI for a given API

    Args:
        api (flask_restx_marshmallow.Api): api object

    Returns:
        str: render result
    """
    if base := current_app.config.get("SWAGGER_UI_BASE_URL"):
        return render_template(
            "index.html",
            title=api.title,
            specs_url=api.specs_url,
            base_url=base,
        )
    rdb: redis.Redis | dict = (
        redis.StrictRedis.from_url(
            current_app.config["CACHE_REDIS_URL"], decode_responses=True
        )
        if current_app.config.get("CACHE_REDIS_URL") is not None
        else {}
    )
    match current_app.config.get("SWAGGER_UI_CDN"):
        case "cdn.baomitu.com":
            if (
                current_version := current_app.config.get("SWAGGER_UI_VERSION")
                or rdb.get("swagger-ui-version")
            ) is not None:
                return render_template(
                    "index.html",
                    title=api.title,
                    specs_url=api.specs_url,
                    base_url="//lib.baomitu.com/swagger-ui/"
                    + current_app.config["SWAGGER_UI_VERSION"],
                )
            try:
                if (
                    req := requests.get(
                        "https://cdn.baomitu.com/swagger-ui", timeout=5
                    )
                ) and req.status_code == 200:
                    html: BeautifulSoup = BeautifulSoup(req.text, "html.parser")
                    versions: list[tuple[int]] = sorted(
                        tuple(map(int, version_string.split(".")))
                        for version in html.find_all(
                            "h3", class_="version-name version-close"
                        )
                        if (version_string := version.attrs["data-id"])
                        and re.match(r"^\d+\.\d+\.\d+$", version_string)
                    )
                    while current_version := ".".join(map(str, versions.pop())):
                        if (
                            (
                                res := requests.get(
                                    "https://lib.baomitu.com/swagger-ui/"
                                    + current_version
                                    + "/swagger-ui-bundle.min.js",
                                    timeout=1,
                                )
                            )
                            and res.status_code == 200
                            and res.text[:3] != "404"
                            # 360 CDN return status code 200 but return 404 page
                        ):
                            if (
                                current_app.config.get("CACHE_REDIS_URL")
                                is not None
                            ):
                                rdb.set(
                                    "swagger-ui-version",
                                    current_version,
                                    ex=timedelta(hours=24),
                                )
                            return render_template(
                                "index.html",
                                title=api.title,
                                specs_url=api.specs_url,
                                base_url="//lib.baomitu.com/swagger-ui/"
                                + current_version,
                            )
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
            ):
                current_app.logger.error("use local swagger")
        case "cdn.bootcdn.net":
            if (
                current_version := current_app.config.get("SWAGGER_UI_VERSION")
                or rdb.get("swagger-ui-version")
            ) is not None:
                return render_template(
                    "index.html",
                    title=api.title,
                    specs_url=api.specs_url,
                    base_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/"
                    + current_app.config["SWAGGER_UI_VERSION"],
                )
            try:
                if (
                    req := requests.get(
                        "https://www.bootcdn.cn/swagger-ui", timeout=5
                    )
                ) and req.status_code == 200:
                    html: BeautifulSoup = BeautifulSoup(req.text, "html.parser")
                    ul_tag: Tag = html.find(
                        "ul", class_="dropdown-menu dmenuver"
                    )
                    versions: list[tuple[int]] = sorted(
                        tuple(map(int, version_string.split(".")))
                        for version in ul_tag.find_all("a")
                        if (version_string := version.attrs["data-version"])
                        and re.match(r"^\d+\.\d+\.\d+$", version_string)
                    )
                    while current_version := ".".join(map(str, versions.pop())):
                        if (
                            res := requests.get(
                                "https://cdn.bootcdn.net/ajax/libs/swagger-ui/"
                                + current_version
                                + "/swagger-ui-bundle.min.js",
                                timeout=1,
                            )
                        ) and res.status_code == 200:
                            if (
                                current_app.config.get("CACHE_REDIS_URL")
                                is not None
                            ):
                                rdb.set(
                                    "swagger-ui-version",
                                    current_version,
                                    ex=timedelta(hours=24),
                                )
                            return render_template(
                                "index.html",
                                title=api.title,
                                specs_url=api.specs_url,
                                base_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/"
                                + current_version,
                            )
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
            ):
                current_app.logger.error("use local swagger")
        case "cdnjs.com":
            if (
                current_version := current_app.config.get("SWAGGER_UI_VERSION")
                or rdb.get("swagger-ui-version")
            ) is not None:
                return render_template(
                    "index.html",
                    title=api.title,
                    specs_url=api.specs_url,
                    base_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/"
                    + current_app.config["SWAGGER_UI_VERSION"],
                )
            try:
                if (
                    req := requests.get(
                        "https://cdn.baomitu.com/swagger-ui", timeout=5
                    )
                ) and req.status_code == 200:
                    current_version = re.findall(
                        r'\("swagger-ui","(.*)",true,false', req.text
                    )[0]
                    if current_app.config.get("CACHE_REDIS_URL") is not None:
                        rdb.set(
                            "swagger-ui-version",
                            current_version,
                            ex=timedelta(hours=24),
                        )
                        return render_template(
                            "index.html",
                            title=api.title,
                            specs_url=api.specs_url,
                            base_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/"
                            + current_version,
                        )
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
            ):
                current_app.logger.error("use local swagger")
        case _:
            current_app.logger.error("unavailable cdn. use local swagger")
    return render_template(
        "local.html",
        title=api.title,
        specs_url=api.specs_url,
    )


spec: APISpec = APISpec(
    title="flask_restx_marshmallow",
    version="0.1.0",
    openapi_version="3.0.2",
    plugins=[MarshmallowPlugin(schema_name_resolver=resolver)],
    info={"description": "flask_restx_marshmallow backend api"},
)
converter: MarshmallowPlugin.Converter = spec.plugins[0].converter
apidoc: Apidoc = Apidoc(
    "swagger_doc",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/swaggerui",
)


@apidoc.add_app_template_global
def swagger_static(filename: str) -> str:
    """swagger static file

    Args:
        filename (str): filename

    Returns:
        str: url path
    """
    return url_for("swagger_doc.static", filename=filename)
