"""
Description: create backend service
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 13:08:18
FilePath: /flask_restx_marshmallow/examples/app/__init__.py
"""
import datetime
from http import HTTPStatus

from app.config import Config
from app.managers import auth_ns, role_ns, route_ns, user_ns
from app.models import Users
from app.utils import api, api_blueprint, cache, db
from flask import Flask, Response, jsonify
from flask_jwt_extended import JWTManager


def create_app(config=Config) -> Flask:
    """
    Author: 1746104160
    msg: create backend service
    """
    app: Flask = Flask(__name__)
    app.config.from_object(config)
    jwt: JWTManager = JWTManager(app)

    db.init_app(app)
    api.add_namespace(auth_ns, path="/auth/user")
    api.add_namespace(role_ns, path="/admin/role")
    api.add_namespace(route_ns, path="/admin/route")
    api.add_namespace(user_ns, path="/admin/user")
    if app.config["DEVELOPING"] is True:
        api.register_doc(app, api_blueprint)
    else:
        api.register_doc_production(app, api_blueprint)

    app.register_blueprint(api_blueprint)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(
        _jwt_header: dict[str, str], jwt_payload: dict
    ) -> bool:
        jti: str = jwt_payload["jti"]
        exp: int = jwt_payload["exp"]
        user_id: int = jwt_payload["sub"]
        return (
            exp < datetime.datetime.now().timestamp()
            or cache.get(jti)
            or not Users.judge_user_valid_by_id(user_id)
        )

    @jwt.user_identity_loader
    def user_identity_lookup(user: Users) -> str:
        return user.id.hex

    @jwt.user_lookup_loader
    def user_lookup_callback(
        _jwt_header: dict[str, str], jwt_payload: dict[str, str]
    ) -> Users:
        return Users.get_user_by_id(jwt_payload["sub"])

    @jwt.unauthorized_loader
    def unauthorized_callback(*_args, **_kwargs) -> Response:
        res: Response = jsonify(
            {
                "code": HTTPStatus.UNAUTHORIZED.value,
                "message": "user unauthorized",
                "success": False,
            }
        )
        res.status_code = HTTPStatus.UNAUTHORIZED.value
        return res

    @jwt.token_verification_failed_loader
    def token_verification_failed_callback(*_args, **_kwargs) -> Response:
        res: Response = jsonify(
            {
                "code": HTTPStatus.UNAUTHORIZED.value,
                "message": "user token verification failed",
                "success": False,
            }
        )
        res.status_code = HTTPStatus.UNAUTHORIZED.value
        return res

    @jwt.expired_token_loader
    def expired_token_callback(*_args, **_kwargs) -> Response:
        res: Response = jsonify(
            {
                "code": HTTPStatus.UNAUTHORIZED.value,
                "message": "user token expired",
                "success": False,
            }
        )
        res.status_code = HTTPStatus.UNAUTHORIZED.value
        return res

    @jwt.invalid_token_loader
    def invalid_token_callback(*_args, **_kwargs) -> Response:
        res: Response = jsonify(
            {
                "code": HTTPStatus.UNAUTHORIZED.value,
                "message": "user token invalid",
                "success": False,
            }
        )
        res.status_code = HTTPStatus.UNAUTHORIZED.value
        return res

    @jwt.revoked_token_loader
    def revoked_token_callback(*_args, **_kwargs) -> Response:
        res: Response = jsonify(
            {
                "code": HTTPStatus.UNAUTHORIZED.value,
                "message": "user is banned",
                "success": False,
            }
        )
        res.status_code = HTTPStatus.UNAUTHORIZED.value
        return res

    return app
