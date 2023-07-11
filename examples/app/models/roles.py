"""
Description: role model
version: 0.1.1
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-14 15:43:35
FilePath: /flask_restx_marshmallow/examples/app/models/roles.py
"""
from datetime import datetime
from typing import Iterable
from uuid import UUID, uuid4

from app import models
from app.utils import cache, db
from flask import current_app
from flask_jwt_extended import get_current_user
from sqlalchemy import Boolean, Column, DateTime, Integer, String, exc, func
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy_utils import UUIDType, aggregated, generic_repr

from flask_restx_marshmallow import permission_required


@generic_repr
class Roles(db.Model):
    """
    Author: 1746104160
    msg: role info
    """

    __tablename__: str = "role"
    id: Mapped[UUID] = Column(
        UUIDType(binary=False),
        primary_key=True,
        nullable=False,
        comment="primary key for the table",
    )
    created_on: Mapped[datetime] = Column(
        DateTime, nullable=False, comment="created datetime"
    )
    description: Mapped[str] = Column(
        String(255), nullable=False, comment="role description"
    )
    last_update: Mapped[datetime] = Column(
        DateTime, nullable=False, comment="last update datetime"
    )
    name: Mapped[str] = Column(
        String(50), unique=True, nullable=False, comment="role name"
    )
    routes: Mapped[list["models.Routes"]] = relationship(
        "Routes", secondary="role2route", back_populates="roles"
    )
    users: Mapped[list["models.Users"]] = relationship(
        "Users", secondary="user2role", back_populates="roles"
    )
    valid: Mapped[bool] = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="whether the role is valid",
    )

    @aggregated(
        "users",
        Column(Integer, nullable=False, default=0, comment="valid user count"),
    )
    def user_count(self):
        """valid user count"""
        return func.count(  # pylint: disable=not-callable
            models.Users.valid is True
        )

    @classmethod
    def add(
        cls,
        *,
        description: str,
        name: str,
        routes: Iterable[str] = ("/personal"),
    ) -> dict:
        """create a new role

        Args:
            description (str): role description
            name (str): role name
            routes (Iterable[str], optional): authorized routes for the role.
            Defaults to ("/personal").
        """
        try:
            db.session.add(
                cls(
                    created_on=datetime.now(),
                    description=description,
                    id=uuid4(),
                    last_update=datetime.now(),
                    name=name,
                    routes=[
                        data
                        for route_name in routes
                        if (
                            data := models.Routes.get_route_by_route_name(
                                route_name
                            )
                        )
                    ],
                    valid=True,
                )
            )
            db.session.commit()
            return {"success": True, "message": "role created successfully"}
        except exc.IntegrityError:
            db.session.rollback()
            return {"success": False, "message": "role name already exists"}

    @classmethod
    @permission_required("/system/role")
    def delete(cls, role_id: UUID) -> dict:
        """delete a role

        Args:
            role_id (UUID): id of the role
        """
        query = cls.query.filter_by(id=role_id)
        current_user: models.Users = get_current_user()
        if query.one_or_none():
            query.delete()
            db.session.commit()
            return {"success": True, "message": "delete role successfully"}
        current_user.ban()
        current_app.logger.error(
            f"{current_user.name} is trying to delete role (id="
            f"{role_id}) that does not exist"
        )
        return {"success": False, "message": "role does not exist"}

    @classmethod
    @permission_required("/system/role")
    def update(cls, role_id: UUID, data: dict) -> dict:
        """update role info

        Args:
            role_id (UUID): id of the role
            data (dict): dict of the update info
        """
        query = cls.query.filter_by(id=role_id)
        current_user: models.Users = get_current_user()
        if role := query.one_or_none():
            role: Roles
            if routes := [
                data
                for route_name in data.pop("routes", [])
                if "/system" not in route_name
                and (data := models.Routes.get_route_by_route_name(route_name))
            ]:
                role.routes = routes
            data.update({"last_update": datetime.now()})
            query.update(data)
            db.session.commit()
            return {
                "success": True,
                "message": "update role info successfully",
            }
        current_user.ban()
        current_app.logger.error(
            f"{current_user.name} is trying to update role (id="
            f"{role_id}) that does not exist"
        )
        return {"success": False, "message": "role does not exist"}

    @classmethod
    def get_role_by_role_name(cls, role_name: str) -> "Roles":
        """get role by role name

        Args:
            role_name (str): role name

        Returns:
            Roles: role
        """
        return cls.query.filter_by(name=role_name).one_or_none()

    @classmethod
    @cache.cached(key_prefix="all_role_names")
    def get_all_names(cls) -> set[str]:
        """all role names

        Returns:
            set[str]: set of all role names
        """
        return set(
            map(
                lambda value: value[0],
                cls.query.with_entities(cls.name).distinct().all(),
            )
        )

    @classmethod
    @permission_required("/system/role")
    def get_all_roles(
        cls,
        *,
        keyword: str = "",
        order: str = "desc",
        order_prop: str = "created_on",
        page: int = 1,
        per_page: int = 10,
    ) -> dict:
        """get all roles

        Args:
            keyword (str, optional): query keyword. Defaults to "".
            order (str, optional): sort order. Defaults to "desc".
            order_prop (str, optional): order property. Defaults to "created_on".
            page (int, optional): current page. Defaults to 1.
            per_page (int, optional): page size. Defaults to 10.
        """
        query = cls.query.filter(
            cls.name != "admin", cls.name.contains(keyword)
        )
        return {
            "roles": query.order_by(
                getattr(cls, order_prop, cls.created_on).desc()
                if order == "desc"
                else getattr(cls, order_prop, cls.created_on).asc()
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all(),
            "total": query.count(),
        }
