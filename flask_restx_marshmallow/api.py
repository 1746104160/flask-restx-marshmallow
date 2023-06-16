"""
Description: patched api of flask_restx_marshmallow
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-04 21:38:24
FilePath: /flask_restx_marshmallow/flask_restx_marshmallow/api.py
"""
import importlib
from dataclasses import dataclass
from http import HTTPStatus
from types import ModuleType
from typing import Optional

from flask import Blueprint, Flask, Response, abort, current_app, jsonify
from flask_restx import Api as OriginalApi
from marshmallow.exceptions import ValidationError
from typing_extensions import override
from werkzeug.exceptions import (
    UnprocessableEntity as originalUnprocessableEntity,
)
from werkzeug.utils import cached_property

from .namespace import Namespace
from .swagger import Swagger
from .util import apidoc, permission_required, ui_for

try:
    json: ModuleType = importlib.import_module("orjson")
except ModuleNotFoundError:
    json = importlib.import_module("json")


class Api(OriginalApi):
    """
    Author: 1746104160
    msg: Patched API
    """

    @cached_property
    def __schema__(self) -> dict:
        """The Swagger specifications/schema for this API"""
        if not self._schema:
            self._schema: dict = Swagger(self).as_dict()
        return self._schema

    def init_app(self, app: Flask | Blueprint, **kwargs) -> None:
        """Add handle error

        Args:
            app (Union[Flask, Blueprint]): app instance
        """
        super().init_app(app, **kwargs)
        app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY.value)(
            handle_validation_error
        )

    @override
    def _register_apidoc(self, app: Flask) -> None:
        """disable original function for registering apidoc"""

    @override
    def render_doc(self) -> str | None:
        """render doc"""
        if self._doc_view:
            return self._doc_view()
        if not self._doc:
            abort(HTTPStatus.NOT_FOUND)
        return ui_for(self)

    @override
    def handle_error(self, e: Exception) -> Response:
        """handle error

        Args:
            e (Exception): exception

        Raises:
            e: exception

        Returns:
            Response: flask response
        """
        for val in current_app.error_handler_spec.values():
            for handler in val.values():
                registered_error_handlers: list[type[Exception]] = list(
                    filter(lambda x: isinstance(e, x), handler.keys())
                )
                if len(registered_error_handlers) > 0:
                    raise e
        return super().handle_error(e)

    @override
    def namespace(self, *args, **kwargs) -> Namespace:
        """The only purpose of this method is to pass a custom Namespace class

        Returns:
            Namespace: namespace
        """
        _namespace: Namespace = Namespace(*args, **kwargs)
        self.add_namespace(_namespace)
        return _namespace

    @override
    def _register_doc(self, _app_or_blueprint: Flask | Blueprint) -> None:
        """disable original function for registering doc"""

    @override
    def _register_specs(self, app_or_blueprint: Flask | Blueprint) -> None:
        """disable original function for registering spec"""

    def register_doc_production(
        self,
        app: Flask,
        blueprint: Optional[Blueprint] = None,
        authed_route: Optional[str] = "/system",
    ) -> None:
        """register swagger documentation

        Args:
            app (Flask): app instance
            blueprint (Blueprint, optional): blueprint instance. Defaults to None.
            authed_route (str, optional): authed route. Defaults to "/system".
        """
        assert isinstance(authed_route, str)
        app.register_blueprint(apidoc)
        app_or_blueprint: Blueprint | Flask = blueprint if blueprint else app
        app_or_blueprint.add_url_rule(
            self._doc,
            "doc",
            permission_required(authed_route)(self.render_doc),
        )
        app_or_blueprint.add_url_rule(
            self.prefix or "/",
            "root",
            permission_required(authed_route)(self.render_root),
        )
        app_or_blueprint.add_url_rule(
            "/" + self.default_swagger_filename,
            "specs",
            permission_required(authed_route)(
                lambda: json.dumps(self.__schema__)
            ),
        )

    def register_doc(
        self, app: Flask, blueprint: Optional[Blueprint] = None
    ) -> None:
        """register swagger documentation

        Args:
            app (Flask): app instance
            blueprint (Blueprint, optional): blueprint instance. Defaults to None.
        """
        app.register_blueprint(apidoc)
        app_or_blueprint: Blueprint | Flask = blueprint if blueprint else app
        app_or_blueprint.add_url_rule(
            self._doc,
            "doc",
            self.render_doc,
        )
        app_or_blueprint.add_url_rule(
            self.prefix or "/", "root", self.render_root
        )
        app_or_blueprint.add_url_rule(
            "/" + self.default_swagger_filename,
            "specs",
            lambda: json.dumps(self.__schema__),
        )


@dataclass
class UnprocessableEntity(originalUnprocessableEntity):
    """
    Author: 1746104160
    msg: util class for typing unprocessable entities
    """

    exc: ValidationError


def handle_validation_error(err: UnprocessableEntity) -> Response:
    """Return validation errors as JSON

    Args:
        err (UnprocessableEntity): exception

    Returns:
        Response: response for unprocessable entity
    """
    res: Response = jsonify(
        {
            "code": HTTPStatus.UNPROCESSABLE_ENTITY.value,
            "message": err.exc.messages,
            "success": False,
        }
    )
    res.status_code = HTTPStatus.UNPROCESSABLE_ENTITY.value
    return res
