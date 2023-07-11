"""
Description: interface parameters for route management
version: 0.1.1
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 14:04:28
FilePath: /flask_restx_marshmallow/examples/app/managers/route_manager/parameters.py
"""
from app.managers.route_manager.schemas import RoutesProfileSchema
from app.models import Routes
from marshmallow import post_load, validate
from marshmallow.fields import Integer, String

from flask_restx_marshmallow import QueryParameters


class GetRoutesInfoParameters(QueryParameters):
    """
    Author: 1746104160
    msg: interface parameters for getting routes info
    """

    keyword: str = String(metadata={"description": "keyword"}, load_default="")
    order: str = String(
        validate=validate.OneOf(choices=["desc", "asc"]),
        metadata={"description": "sort order"},
        load_default="desc",
    )
    order_prop: str = String(
        validate=validate.OneOf(
            choices=set(RoutesProfileSchema().fields.keys())
        ),
        load_default="created_on",
        metadata={"description": "order property"},
    )
    page: int = Integer(
        validate=validate.Range(min=1),
        metadata={"description": "page number"},
        load_default=1,
    )
    size: int = Integer(
        validate=validate.OneOf(choices=[5, 10, 20, 50]),
        metadata={"description": "page size"},
        load_default=10,
    )

    @post_load
    def process_get_routes_info(
        self, data: "GetRoutesInfoParameters", **_kwargs
    ) -> dict:
        """query routes info"""
        return {
            "data": Routes.get_all_routes(
                keyword=data.keyword,
                order=data.order,
                order_prop=data.order_prop,
                page=data.page,
                per_page=data.size,
            ),
        }
