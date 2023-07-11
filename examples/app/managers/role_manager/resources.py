"""
Description: RESTful APIs for role management
version: 0.1.1
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-14 20:40:46
FilePath: /flask_restx_marshmallow/examples/app/managers/role_manager/resources.py
"""
from http import HTTPStatus

from app.config import Config
from flask import Response

from flask_restx_marshmallow import Namespace, Resource, permission_required

from .parameters import (
    CreateRoleParameters,
    DeleteRoleParameters,
    GetRolesInfoParameters,
    UpdateRoleParameters,
)
from .schemas import RolesInfoSchema

role_ns: Namespace = Namespace(
    "role", description="interface for role management"
)


@role_ns.route("/info", endpoint="role info")
class RoleInfo(Resource):
    """
    Author: 1746104160
    msg: query role info
    """

    @permission_required("/system/role")
    @role_ns.parameters(
        params=GetRolesInfoParameters(add_jwt=Config.DEVELOPING),
        location="query",
    )
    @role_ns.response(
        code=HTTPStatus.OK,
        description="query role info",
        model=RolesInfoSchema(message="query role info successfully"),
    )
    def get(self, res: dict) -> Response:
        """query role info"""
        return res


@role_ns.route("/manage", endpoint="role manage")
class RoleManage(Resource):
    """
    Author: 1746104160
    msg: role management
    """

    @permission_required("/system/role")
    @role_ns.parameters(
        params=CreateRoleParameters(add_jwt=Config.DEVELOPING),
        locations=["query", "body"],
    )
    @role_ns.response(
        code=HTTPStatus.OK,
        description="create a new role",
        model=None,
        name="CreateRoleSchema",
        message="create a new role successfully",
    )
    def put(self, res: dict) -> Response:
        """create a new role"""
        return res

    @permission_required("/system/role")
    @role_ns.parameters(
        params=UpdateRoleParameters(add_jwt=Config.DEVELOPING),
        locations=["query", "body"],
    )
    @role_ns.response(
        code=HTTPStatus.OK,
        description="update role info",
        model=None,
        name="UpdateRoleInfoSchema",
        message="update role info successfully",
    )
    def patch(self, res: dict) -> Response:
        """update role info"""
        return res

    @permission_required("/system/role")
    @role_ns.parameters(
        params=DeleteRoleParameters(add_jwt=Config.DEVELOPING),
        locations=["query", "body"],
    )
    @role_ns.response(
        code=HTTPStatus.OK,
        description="delete role",
        model=None,
        name="DeleteRoleSchema",
        message="delete role successfully",
    )
    def delete(self, res: dict) -> Response:
        """delete role"""
        return res
