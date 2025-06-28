"""Test swagger doc."""

from collections.abc import Callable
from functools import wraps
from http import HTTPStatus
from typing import TYPE_CHECKING

from flask import request, url_for

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient

    from flask_restx_marshmallow.api import Api


def swagger_auth_decorator_test[**P](
    func: Callable[P, str | bytes],
) -> Callable[P, str | bytes | tuple[str | bytes, HTTPStatus]]:
    """Decorator function.

    Returns:
        Callable: A wrapper function that takes the same arguments as the
            original function.
    """

    @wraps(func)
    def wrapper(
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> str | bytes | tuple[str | bytes, HTTPStatus]:
        """Wrapper function.

        Returns:
            str | bytes: The result of the function call.
        """
        if request.headers.get("Authorization") != "Bearer test_token":
            return "Unauthorized", HTTPStatus.UNAUTHORIZED
        return func(*args, **kwargs)

    return wrapper


def test_swagger_with_debug(app: "Flask", api: "Api", client: "FlaskClient") -> None:
    """Test swagger doc."""
    api.auth_render_swagger(swagger_auth_decorator_test)
    app.config["DEBUG"] = True
    response = client.get(url_for("specs"))
    assert response.status_code == HTTPStatus.OK


def test_swagger_without_debug(
    api: "Api",
    client: "FlaskClient",
) -> None:
    """Test swagger doc without debug mode."""
    api.auth_render_swagger(swagger_auth_decorator_test)
    response = client.get(url_for("specs"))
    assert response.status_code == HTTPStatus.UNAUTHORIZED
