"""
Description: response schema for user management
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 14:30:53
FilePath: /flask_restx_marshmallow/examples/app/managers/user_manager/schemas.py
"""
import uuid
from dataclasses import dataclass
from datetime import datetime

from app.models import Roles, Users
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

from ..role_manager.schemas import RolesProfileSchema


class UsersProfileSchema(SQLAlchemySchema):
    """
    Author: 1746104160
    msg: user profile schema
    """

    @dataclass
    class Meta:
        """
        Author: 1746104160
        msg: set user info SQLAlchemy schema model
        """

        model = Users

    created_on: datetime = DateTime(
        metadata={"description": "created datetime"}
    )
    description: str = String(metadata={"description": "user description"})
    last_login: datetime = DateTime(
        metadata={"description": "last login datetime"}
    )
    name: str = String(metadata={"description": "user name"})
    roles: list[Roles] = List(
        Nested(RolesProfileSchema), metadata={"description": "user roles"}
    )
    routes: list[str] = List(
        String(metadata={"description": "authorized routes"})
    )
    user_id: uuid.UUID = UUID(
        attribute="id", metadata={"description": "primary key"}
    )
    valid: bool = Boolean(metadata={"description": "whether the user is valid"})


class UsersInfoSchema(StandardSchema):
    """
    Author: 1746104160
    msg: user info schema
    """

    data: dict = Nested(
        {
            "users": List(
                Nested(UsersProfileSchema),
                metadata={"description": "user info"},
            ),
            "total": Integer(metadata={"description": "user total count"}),
        },
        metadata={"description": "data"},
    )
