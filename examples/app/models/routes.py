"""
Description: route model
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-14 19:23:03
FilePath: /flask_restx_marshmallow/examples/app/models/routes.py
"""
from datetime import datetime
from uuid import UUID, uuid4

from app import models
from app.utils import cache, db
from flask import current_app
from sqlalchemy import Column, DateTime, Integer, String, exc, func
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy_utils import UUIDType, aggregated, generic_repr

from flask_restx_marshmallow import permission_required


@generic_repr
class Routes(db.Model):
    """
    Author: 1746104160
    msg: route info
    """

    __tablename__ = "route"
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
        String(255), nullable=False, comment="route description"
    )
    last_update: Mapped[datetime] = Column(
        DateTime, nullable=False, comment="last update datetime"
    )
    name: Mapped[str] = Column(
        String(50), unique=True, nullable=False, comment="route name"
    )
    roles: Mapped[list[models.Roles]] = relationship(
        "Roles", secondary="role2route", back_populates="routes"
    )

    @aggregated(
        "roles.users",
        Column(Integer, nullable=False, default=0, comment="valid user count"),
    )
    def user_count(self):
        """valid user count"""
        return func.count(  # pylint: disable=not-callable
            models.Users.valid is True
        )

    @classmethod
    @permission_required("/system/route", optional=True)
    def add(
        cls,
        name: str,
        description: str,
    ) -> dict:
        """add route

        Args:
            description (str): route description
            name (str): route name
        """
        try:
            db.session.add(
                cls(
                    created_on=datetime.now(),
                    description=description,
                    id=uuid4(),
                    last_update=datetime.now(),
                    name=name,
                )
            )
            db.session.commit()
            return {"success": True, "message": "add route success"}
        except exc.IntegrityError:
            db.session.rollback()
            current_app.logger.warning(msg=f"route {name} already exists")
            return {"success": False, "message": "route already exists"}

    @classmethod
    @permission_required("/system/role")
    def get_route_by_route_name(cls, route_name: str) -> "Routes":
        """get route by route name

        Args:
            route_name (str): route name

        Returns:
            Routes: route object
        """
        return cls.query.filter_by(name=route_name).one_or_none()

    @classmethod
    @cache.cached(key_prefix="all_route_names")
    def get_all_names(cls) -> set[str]:
        """get all route names

        Returns:
            set[str]: set of route names
        """
        set(
            map(
                lambda value: value[0],
                cls.query.with_entities(cls.name).distinct().all(),
            )
        )

    @classmethod
    def get_all_routes(
        cls,
        *,
        keyword: str = "",
        order: str = "desc",
        order_prop: str = "created_on",
        page: int = 1,
        per_page: int = 10,
    ) -> dict:
        """get all routes

        Args:
            keyword (str, optional): query keyword. Defaults to "".
            order (str, optional): sort order. Defaults to "desc".
            order_prop (str, optional): order property. Defaults to "created_on".
            page (int, optional): current page. Defaults to 1.
            per_page (int, optional): page size. Defaults to 10.
        """
        query = cls.query.filter(
            cls.name.notlike("/system%"), cls.name.contains(keyword)
        )
        return {
            "routes": query.order_by(
                getattr(cls, order_prop, cls.created_on).desc()
                if order == "desc"
                else getattr(cls, order_prop, cls.created_on).asc()
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all(),
            "total": query.count(),
        }
