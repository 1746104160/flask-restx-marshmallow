"""
Description: SQLAlchemy models for the example app. 
version: 0.1.1
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-05 14:58:06
FilePath: /examples/app/models/__init__.py
"""
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy_utils import UUIDType, generic_repr

from app.models.roles import Roles
from app.models.routes import Routes
from app.models.users import Users
from app.utils import db


@generic_repr
@dataclass
class User2Role(db.Model):
    """
    Author: 1746104160
    msg: User and Role relationship table
    """

    __tablename__ = "user2role"
    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="primary key for the table",
    )
    user_id: Mapped[UUID] = Column(
        UUIDType(binary=False),
        ForeignKey(
            "user.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="foreign key for user table",
    )
    role_id: Mapped[UUID] = Column(
        UUIDType(binary=False),
        ForeignKey(
            "role.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="foreign key for role table",
    )


@generic_repr
@dataclass
class Role2Route(db.Model):
    """
    Author: 1746104160
    msg: Role and Route relationship table
    """

    __tablename__: str = "role2route"
    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
        comment="primary key for the table",
    )
    role_id: Mapped[UUID] = Column(
        UUIDType(binary=False),
        ForeignKey(
            "role.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="foreign key for role table",
    )
    route_id: Mapped[UUID] = Column(
        UUIDType(binary=False),
        ForeignKey(
            "route.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        comment="foreign key for route table",
    )
