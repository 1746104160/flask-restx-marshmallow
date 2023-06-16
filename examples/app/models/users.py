"""
Description: user model
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 13:16:55
FilePath: /flask_restx_marshmallow/examples/app/models/users.py
"""
from datetime import datetime
from typing import Iterable, Optional
from uuid import UUID, uuid4

from app import models
from app.utils import db
from flask import current_app
from flask_jwt_extended import get_current_user
from sqlalchemy import Boolean, Column, DateTime, String, Text, exc
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy_utils import (
    PasswordType,
    ScalarListType,
    UUIDType,
    generic_repr,
    observes,
)

from flask_restx_marshmallow import permission_required


@generic_repr
class Users(db.Model):
    """
    Author: 1746104160
    msg: user info
    """

    __tablename__: str = "user"
    id: Mapped[UUID] = Column(
        UUIDType(binary=False),
        primary_key=True,
        nullable=True,
        comment="primary key for the table",
    )
    created_on: Mapped[datetime] = Column(
        DateTime, nullable=False, comment="created datetime"
    )
    description: Mapped[str] = Column(Text, comment="user description")
    last_login: Mapped[datetime] = Column(
        DateTime, nullable=False, comment="last login datetime"
    )
    name: Mapped[str] = Column(
        String(20), unique=True, nullable=False, comment="user name"
    )
    password: Mapped[str] = Column(
        PasswordType(
            schemes=["pbkdf2_sha512", "md5_crypt"], deprecated=["md5_crypt"]
        ),
        nullable=False,
        comment="user password",
    )
    roles: Mapped[list[models.Roles]] = relationship(
        "Roles", secondary="user2role", back_populates="users"
    )
    routes: Mapped[list[str]] = Column(
        ARRAY(String(50)).with_variant(ScalarListType(str), "sqlite", "mysql"),
        nullable=False,
        default=["/personal"],
        comment="user authorized routes",
    )
    valid: Mapped[bool] = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="whether the user is valid",
    )

    @observes("roles")
    def auto_set_routes(self, roles: set[models.Roles]) -> None:
        """auto set authorized routes

        Args:
            roles (set[Roles]): set of role objects
        """
        self.routes = list(
            {
                route.name
                for role in roles
                for route in role.routes
                if role.valid
            }
        )

    @classmethod
    @permission_required("/system/route", optional=True)
    def add(
        cls,
        *,
        description: Optional[str] = None,
        name: str,
        password: str,
        roles: Iterable[str] = ("standard",),
    ) -> dict:
        """create system user

        Args:
            description (str, optional): personal description. Defaults to None.
            name (str): user name
            password (str): user password
            roles (Iterable[str], optional): roles for the user. Defaults to None.
        """
        try:
            db.session.add(
                cls(
                    created_on=datetime.now(),
                    description=description,
                    id=uuid4(),
                    last_login=datetime.now(),
                    name=name,
                    password=password,
                    roles=[
                        data
                        for role_name in roles
                        if (
                            data := models.Roles.get_role_by_role_name(
                                role_name
                            )
                        )
                    ],
                    valid=True,
                )
            )
            db.session.commit()
            return {"success": True, "message": "create user success"}
        except exc.IntegrityError:
            db.session.rollback()
            return {"success": False, "message": "user name already exists"}

    @classmethod
    @permission_required("/system/user")
    def delete(cls, user_id: UUID) -> dict:
        """delete a user

        Args:
            user_id (UUID): id of the user
        """
        query = cls.query.filter_by(id=user_id)
        current_user: Users = get_current_user()
        if query.one_or_none():
            query.delete()
            db.session.commit()
            return {"success": True, "message": "delete user success"}
        current_user.ban()
        current_app.logger.error(
            f"{current_user.name} is trying to delete user (id="
            f"{user_id}) that does not exist"
        )
        return {"success": False, "message": "user does not exist"}

    @classmethod
    @permission_required("/system/user")
    def update(cls, user_id: UUID, data: dict) -> dict:
        """update user info

        Args:
            user_id (UUID): id of the user
            data (dict): dict of the update info
        """
        query = cls.query.filter_by(id=user_id)
        current_user: Users = get_current_user()
        if user := query.one_or_none():
            user: Users
            if roles := [
                data
                for role_name in data.pop("roles", [])
                if role_name != "admin"
                and (data := models.Roles.get_role_by_role_name(role_name))
            ]:
                user.roles = roles
            data.update({"last_login": datetime.now()})
            query.update(data)
            db.session.commit()
            return {
                "success": True,
                "message": "update user success",
            }
        current_user.ban()
        current_app.logger.error(
            f"{current_user.name} is trying to update user (id="
            f"{user_id}) that does not exist"
        )
        return {"success": False, "message": "user does not exist"}

    @classmethod
    def get_user_by_id(cls, user_id: int) -> "Users":
        """get user by id

        Args:
            user_id (int): id of the user

        Returns:
            Users: user object
        """
        return cls.query.filter_by(id=user_id).one_or_none()

    @classmethod
    def get_user_by_username(cls, username: str) -> "Users":
        """get user by username

        Args:
            username (str): user name

        Returns:
            Users: user object
        """
        return cls.query.filter_by(name=username).one_or_none()

    @classmethod
    def get_all_users(
        cls,
        *,
        keyword: str = "",
        order: str = "desc",
        order_prop: str = "created_on",
        page: int = 1,
        per_page: int = 10,
    ) -> dict:
        """get all users

        Args:
            keyword (str, optional): query keyword. Defaults to "".
            order (str, optional): sort order. Defaults to "desc".
            order_prop (str, optional): order property. Defaults to "created_on".
            page (int, optional): current page. Defaults to 1.
            per_page (int, optional): page size. Defaults to 10.
        """
        query = cls.query.filter(
            cls.name != "administrator", cls.name.contains(keyword)
        )
        return {
            "users": query.order_by(
                getattr(cls, order_prop, cls.created_on).desc()
                if order == "desc"
                else getattr(cls, order_prop, cls.created_on).asc()
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all(),
            "total": query.count(),
        }

    @classmethod
    def judge_user_valid_by_id(cls, user_id: int) -> bool:
        """judge whether the user is valid

        Args:
            user_id (int): id of the user

        Returns:
            bool: whether the user is valid
        """
        try:
            return cls.get_user_by_id(user_id).valid
        except AttributeError:
            return False

    def ban(self) -> None:
        """ban the user"""
        self.valid = False
        db.session.commit()
