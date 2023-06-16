"""
Description: response schema for role management
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 13:52:14
FilePath: /flask_restx_marshmallow/examples/app/managers/role_manager/schemas.py
"""
import uuid
from dataclasses import dataclass
from datetime import datetime

from app.models import Roles, Routes
from marshmallow.fields import (
    UUID,
    Boolean,
    DateTime,
    Integer,
    List,
    Nested,
    String,
)

from flask_restx_marshmallow import SQLAlchemySchema, StandardSchema

from ..route_manager.schemas import RoutesProfileSchema


class RolesProfileSchema(SQLAlchemySchema):
    """
    Author: 1746104160
    msg: role profile schema
    """

    @dataclass
    class Meta:
        """
        Author: 1746104160
        msg: set role info SQLAlchemy schema model
        """

        model = Roles

    created_on: datetime = DateTime(
        metadata={"description": "created datetime"}
    )
    description: str = String(metadata={"description": "role description"})
    last_update: datetime = DateTime(
        metadata={"description": "last update datetime"}
    )
    name: str = String(metadata={"description": "role name"})
    role_id: uuid.UUID = UUID(
        attribute="id", metadata={"description": "primary key"}
    )
    routes: list[Routes] = List(
        Nested(RoutesProfileSchema),
        metadata={"description": "authorized routes"},
    )
    valid: bool = Boolean(metadata={"description": "whether the role is valid"})


class RolesInfoSchema(StandardSchema):
    """
    Author: 1746104160
    msg: role info schema
    """

    data: dict = Nested(
        {
            "roles": List(
                Nested(RolesProfileSchema),
                metadata={"description": "role info"},
            ),
            "total": Integer(metadata={"description": "role total count"}),
        },
        metadata={"description": "data"},
    )
