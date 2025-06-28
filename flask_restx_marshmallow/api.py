"""patched api of flask_restx_marshmallow."""

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Self, cast, override

from flask import abort, current_app
from flask.blueprints import Blueprint
from flask.helpers import url_for
from flask_restx.api import Api as OriginalApi
from werkzeug.exceptions import BadRequest, InternalServerError, UnprocessableEntity
from werkzeug.utils import cached_property

from flask_restx_marshmallow.swagger import Swagger
from flask_restx_marshmallow.util import (
    Request,
    Response,
    handle_invalid_json_error,
    handle_validation_error,
    output_json,
    render_swagger_json,
    render_swagger_ui,
)

try:
    from loguru import logger
except ImportError:
    from logging import getLogger

    logger = getLogger(__name__)

if TYPE_CHECKING:
    from flask.app import Flask

    from .namespace import Namespace
    from .type import OpenAPI, TupleResponse


class Api(OriginalApi):
    """Patched API."""

    _swagger_auth_decorator = None
    if TYPE_CHECKING:
        namespaces: list[Namespace]
        blueprint: Blueprint

    @cached_property
    def __schema__(self: Self) -> "OpenAPI":
        """The Swagger specifications/schema for this API.

        Raises:
            ValueError: Unable to render schema

        Returns:
            OpenAPI: swagger
        """
        if not self._schema:
            try:
                self._schema = Swagger(self).as_dict()
            except Exception as exc:
                msg = "Unable to render schema"
                logger.exception(msg)
                raise ValueError(msg) from exc
        return self._schema

    @override
    def render_doc(self: Self) -> str:
        """Render doc.

        Returns:
            str: rendered doc
        """
        if (
            self._swagger_auth_decorator is None
            or current_app.config.get("DEBUG") is True
        ):
            return render_swagger_ui(self)
        return cast(
            "str",
            self._swagger_auth_decorator(render_swagger_ui)(self),
        )

    def render_json(self: Self) -> str | bytes:
        """Render swagger json doc.

        Returns:
            str: rendered json
        """
        if (
            self._swagger_auth_decorator is None
            or current_app.config.get("DEBUG") is True
        ):
            return render_swagger_json(self)
        return cast(
            "str | bytes",
            self._swagger_auth_decorator(render_swagger_json)(self),
        )

    @override
    def _register_apidoc(self: Self, app: "Flask") -> None:
        conf: dict = app.extensions.setdefault("restx", {})
        if not conf.get("apidoc_registered"):
            app.register_blueprint(apidoc, url_prefix="/swagger")
        conf["apidoc_registered"] = True

    @override
    def _register_specs(self: Self, app_or_blueprint: "Flask | Blueprint") -> None:
        if self._add_specs:
            app_or_blueprint.add_url_rule(
                f"/{self.default_swagger_filename}",
                "specs",
                self.render_json,
            )

    @override
    def _register_doc(self: Self, app_or_blueprint: "Flask | Blueprint") -> None:
        if self._add_specs and self._doc:
            app_or_blueprint.add_url_rule(self._doc, "doc", self.render_doc)
        app_or_blueprint.add_url_rule(self._doc, "root", abort)

    @override
    def init_app(self: Self, app: "Flask", **kwargs) -> None:  # noqa: ANN003
        super().init_app(app, **kwargs)
        self.error_handlers: dict[type[Exception], Callable[[], TupleResponse]] = {}
        self.error_handlers[BadRequest] = handle_invalid_json_error
        self.error_handlers[UnprocessableEntity] = handle_validation_error
        self.error_handlers[InternalServerError] = lambda: None  # type: ignore[assignment]

    @override
    def _init_app(self: Self, app: "Flask") -> None:
        super()._init_app(app)
        self.representations["application/json"] = output_json
        app.response_class = Response
        app.request_class = Request

    def auth_render_swagger[T](
        self,
        func: Callable[[Callable[["Api"], str | bytes]], Callable[["Api"], T]],
    ) -> None:
        """Add decorator to render swagger ui."""
        self._swagger_auth_decorator = func


apidoc = Blueprint(
    "swagger_doc",
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)


@apidoc.add_app_template_global
def swagger_static(filename: str) -> str:
    """Swagger static file.

    Args:
        filename (str): filename

    Returns:
        str: url path
    """
    return url_for("swagger_doc.static", filename=filename)
