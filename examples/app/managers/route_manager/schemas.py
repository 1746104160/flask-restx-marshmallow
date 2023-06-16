"""
Description: response schema for route management
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 14:09:09
FilePath: /flask_restx_marshmallow/examples/app/managers/route_manager/schemas.py
"""
import uuid
from dataclasses import dataclass
from datetime import datetime

from app.models import Routes
from marshmallow.fields import UUID, DateTime, Integer, List, Nested, String

from flask_restx_marshmallow import SQLAlchemySchema, StandardSchema


class RoutesProfileSchema(SQLAlchemySchema):
    """
    Author: 1746104160
    msg: route profile schema
    """

    @dataclass
    class Meta:
        """
        Author: 1746104160
        msg: set route info SQLAlchemy schema model
        """

        model = Routes

    created_on: datetime = DateTime(
        metadata={"description": "created datetime"}
    )
    description: str = String(metadata={"description": "route description"})
    last_update: datetime = DateTime(
        metadata={"description": "last update datetime"}
    )
    name: str = String(metadata={"description": "route name"})
    route_id: uuid.UUID = UUID(
        attribute="id", metadata={"description": "primary key"}
    )


class RoutesInfoSchema(StandardSchema):
    """
    Author: 1746104160
    msg: route info schema
    """

    data: dict = Nested(
        {
            "routes": List(
                Nested(RoutesProfileSchema),
                metadata={"description": "route info"},
            ),
            "total": Integer(metadata={"description": "route total count"}),
        },
        metadata={"description": "data"},
    )
