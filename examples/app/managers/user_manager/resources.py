"""
Description: RESTful APIs for user management
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 14:27:35
FilePath: /flask_restx_marshmallow/examples/app/managers/user_manager/resources.py
"""
from http import HTTPStatus

from app.config import Config
from flask import Response

from flask_restx_marshmallow import Namespace, Resource, permission_required

from .parameters import (
    DeleteUserParameters,
    GetUsersInfoParameters,
    UpdateUserParameters,
)
from .schemas import UsersInfoSchema

user_ns: Namespace = Namespace(
    "user", description="interface for user management"
)


@user_ns.route("/info", endpoint="user info")
class UserInfo(Resource):
    """
    Author: 1746104160
    msg: query user info
    """

    @permission_required("/system/user")
    @user_ns.parameters(
        params=GetUsersInfoParameters(add_jwt=Config.DEVELOPING),
        location="query",
    )
    @user_ns.response(
        code=HTTPStatus.OK,
        description="query user info",
        model=UsersInfoSchema(message="query user info successfully"),
    )
    def get(self, res: dict) -> Response:
        """query user info"""
        return res


@user_ns.route("/manage", endpoint="用户信息管理")
class UserManage(Resource):
    """
    Author: 1746104160
    msg: user management
    """

    @user_ns.parameters(
        params=UpdateUserParameters(add_jwt=Config.DEVELOPING),
        locations=["query", "body"],
    )
    @user_ns.response(
        code=HTTPStatus.OK,
        description="update user info",
        model=None,
        name="UpdateUserInfoSchema",
        message="update user info successfully",
    )
    def patch(self, res: dict) -> Response:
        """update user info"""
        return res

    @user_ns.parameters(
        params=DeleteUserParameters(add_jwt=Config.DEVELOPING),
        locations=["query", "body"],
    )
    @user_ns.response(
        code=HTTPStatus.OK,
        description="delete a user",
        model=None,
        name="DeleteUserSchema",
        message="delete user successfully",
    )
    def delete(self, res: dict) -> Response:
        """delete a user"""
        return res
