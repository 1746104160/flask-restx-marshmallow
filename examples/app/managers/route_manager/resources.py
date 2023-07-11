"""
Description: RESTful APIs for route management
version: 0.1.1
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 14:07:42
FilePath: /flask_restx_marshmallow/examples/app/managers/route_manager/resources.py
"""
from http import HTTPStatus

from app.config import Config
from requests import Response

from flask_restx_marshmallow import Namespace, Resource, permission_required

from .parameters import GetRoutesInfoParameters
from .schemas import RoutesInfoSchema

route_ns: Namespace = Namespace(
    "route", description="interface for route management"
)


@route_ns.route("/info", endpoint="route info")
class RouteInfo(Resource):
    """
    Author: 1746104160
    msg: query route info
    """

    @permission_required("/system/route")
    @route_ns.parameters(
        GetRoutesInfoParameters(add_jwt=Config.DEVELOPING), location="query"
    )
    @route_ns.response(
        code=HTTPStatus.OK,
        description="query route info",
        model=RoutesInfoSchema(message="query route info successfully"),
    )
    def get(self, res: dict) -> Response:
        """query route info"""
        return res
