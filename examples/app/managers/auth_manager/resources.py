"""
Description: RESTful APIs for system login and register
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-14 20:23:13
FilePath: /flask_restx_marshmallow/examples/app/managers/auth_manager/resources.py
"""
from http import HTTPStatus

from flask import Response

from flask_restx_marshmallow import Namespace, Resource

from .parameters import LoginParameters, RegisterParameters
from .schemas import LoginSchema

auth_ns: Namespace = Namespace(
    "auth", description="interface for user authorization"
)


@auth_ns.route("/login", endpoint="login")
class LoginSystem(Resource):
    """
    Author: 1746104160
    msg: login system account
    """

    @auth_ns.parameters(params=LoginParameters(), location="body")
    @auth_ns.response(
        code=HTTPStatus.OK,
        description="login system account",
        model=LoginSchema(message="login successfully"),
    )
    def post(self, res: dict) -> Response:
        """login system account"""
        return res


@auth_ns.route("/register", endpoint="注册")
class RegisterSystem(Resource):
    """
    Author: 1746104160
    msg: register system account
    """

    @auth_ns.parameters(params=RegisterParameters(), location="body")
    @auth_ns.response(
        code=HTTPStatus.OK,
        description="register system account",
        model=None,
        name="RegisterSchema",
        message="register successfully",
    )
    def put(self, res: dict) -> Response:
        """register system account"""
        return res
