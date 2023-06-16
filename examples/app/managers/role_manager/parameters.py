"""
Description: interface parameters for role management
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-14 20:35:53
FilePath: /flask_restx_marshmallow/examples/app/managers/role_manager/parameters.py
"""
import uuid
from typing import NoReturn, Optional

from app.models import Roles, Routes
from marshmallow import ValidationError, post_load, validate, validates_schema
from marshmallow.fields import UUID, Boolean, Integer, List, String

from flask_restx_marshmallow import JSONParameters, QueryParameters

from .schemas import RolesProfileSchema


class GetRolesInfoParameters(QueryParameters):
    """
    Author: 1746104160
    msg: interface parameters for getting roles info
    """

    keyword: str = String(metadata={"description": "keyword"}, load_default="")
    order: str = String(
        validate=validate.OneOf(choices=["desc", "asc"]),
        metadata={"description": "sort order"},
        load_default="desc",
    )
    order_prop: str = String(
        validate=validate.OneOf(
            choices=set(RolesProfileSchema().fields.keys())
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
    def process_get_roles_info(
        self, data: "GetRolesInfoParameters", **_kwargs
    ) -> dict:
        """query roles info"""
        return {
            "data": Roles.get_all_roles(
                keyword=data.keyword,
                order=data.order,
                order_prop=data.order_prop,
                page=data.page,
                per_page=data.size,
            ),
        }


class CreateRoleParameters(JSONParameters):
    """
    Author: 1746104160
    msg: interface parameters for creating a new role
    """

    name: str = String(
        required=True,
        validate=validate.Length(min=2, max=20),
        metadata={"description": "role name"},
    )
    description: str = String(
        required=True,
        validate=validate.Length(min=1),
        metadata={"description": "role description"},
    )

    @post_load
    def process_create_role(
        self, data: "CreateRoleParameters", **_kwargs
    ) -> dict:
        """create a new role"""
        return Roles.add(description=data.description, name=data.name)


class UpdateRoleParameters(JSONParameters):
    """
    Author: 1746104160
    msg: interface parameters for updating role info
    """

    role_id: uuid.UUID = UUID(
        required=True,
        metadata={"description": "id of the role to be updated"},
    )
    routes: list[str] = List(
        String(metadata={"description": "route names"}),
        validate=validate.Length(min=1),
    )
    valid: bool = Boolean(metadata={"description": "whether the role is valid"})

    @validates_schema
    def validate(
        self, data: "UpdateRoleParameters", **_kwargs
    ) -> Optional[NoReturn]:
        """validate schema"""
        if all(
            value is None for key, value in data.items() if key != "role_id"
        ):
            raise ValidationError("At least one field should be provided")
        if (
            data["routes"] is not None
            and not set(data["routes"]) < Routes.get_all_names()
        ):
            raise ValidationError("route names are invalid")

    @post_load
    def update_role_info(self, data: dict, **_kwargs) -> dict:
        """update role info"""
        return Roles.update(data.pop("role_id"), data)


class DeleteRoleParameters(JSONParameters):
    """
    Author: 1746104160
    msg: interface parameters for deleting a role
    """

    role_id: uuid.UUID = UUID(
        required=True, metadata={"description": "id of the role to be deleted"}
    )

    @post_load
    def delete_role(self, data: "DeleteRoleParameters", **_kwargs) -> dict:
        """delete a role"""
        return Roles.delete(data.role_id)
