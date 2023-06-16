"""
Description: interface parameters for user management
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 14:18:48
FilePath: /flask_restx_marshmallow/examples/app/managers/user_manager/parameters.py
"""
import uuid
from typing import NoReturn, Optional

from app.models import Roles, Users
from marshmallow import ValidationError, post_load, validate, validates_schema
from marshmallow.fields import UUID, Boolean, Integer, List, String

from flask_restx_marshmallow import JSONParameters, QueryParameters

from .schemas import UsersProfileSchema


class GetUsersInfoParameters(QueryParameters):
    """
    Author: 1746104160
    msg: interface parameters for getting users info
    """

    keyword: str = String(metadata={"description": "keyword"}, load_default="")
    order: str = String(
        validate=validate.OneOf(choices=["desc", "asc"]),
        metadata={"description": "sort order"},
        load_default="desc",
    )
    order_prop: str = String(
        validate=validate.OneOf(
            choices=set(UsersProfileSchema().fields.keys())
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
    def process_get_users_info(
        self, data: "GetUsersInfoParameters", **_kwargs
    ) -> dict:
        """query users info"""
        return {
            "data": Users.get_all_users(
                keyword=data.keyword,
                order=data.order,
                order_prop=data.order_prop,
                page=data.page,
                per_page=data.size,
            ),
        }


class UpdateUserParameters(JSONParameters):
    """
    Author: 1746104160
    msg: interface parameters for updating user info
    """

    user_id: uuid.UUID = UUID(
        required=True,
        metadata={"description": "id of the user to be updated"},
    )
    roles: list[str] = List(
        String(metadata={"description": "role name list"}),
        validate=validate.Length(min=1),
    )
    valid: bool = Boolean(metadata={"description": "whether the user is valid"})

    @validates_schema
    def validate(
        self, data: "UpdateUserParameters", **_kwargs
    ) -> Optional[NoReturn]:
        """validate schema"""
        if all(
            value is None for key, value in data.items() if key != "user_id"
        ):
            raise ValidationError("At least one field must be provided")
        if (
            data.roles is not None
            and not set(data.roles) < Roles.get_all_names()
        ):
            raise ValidationError("role names are not valid")

    @post_load
    def update_user_info(self, data: dict, **_kwargs) -> dict:
        """update user info"""
        return Users.update(data.pop("user_id"), data)


class DeleteUserParameters(JSONParameters):
    """
    Author: 1746104160
    msg: interface parameters for deleting user
    """

    user_id: dict = List(
        Integer(
            required=True,
            metadata={"description": "id of the user to be deleted"},
            validate=validate.Range(min=2),
        )
    )

    @post_load
    def delete_user(self, data: "DeleteUserParameters", **_kwargs) -> dict:
        """delete a user"""
        return Users.delete(data.user_id)
