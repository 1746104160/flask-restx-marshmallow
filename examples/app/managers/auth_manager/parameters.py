"""
Description: interface parameters for system login and register
version: 0.1.1
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-14 20:23:56
FilePath: /flask_restx_marshmallow/examples/app/managers/auth_manager/parameters.py
"""
from datetime import datetime, timedelta

from app.models import Users
from app.utils import db
from flask import current_app
from flask_jwt_extended import create_access_token
from marshmallow import post_load, validate
from marshmallow.fields import String

from flask_restx_marshmallow import JSONParameters


class LoginParameters(JSONParameters):
    """
    Author: 1746104160
    msg: interface parameters for system login
    """

    username: str = String(
        required=True,
        validate=validate.And(
            validate.Length(min=6, max=16),
            validate.Regexp(
                r"^[a-zA-Z][a-zA-Z0-9_]{5,15}$", error="account is invalid"
            ),
        ),
        metadata={"description": "user name"},
    )
    password: str = String(
        required=True,
        validate=validate.And(
            validate.Length(min=6, max=16),
            validate.Regexp(
                r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,16}$",
                error="password is invalid",
            ),
        ),
        metadata={"description": "password"},
    )

    @post_load
    def process_login(self, data: "LoginParameters", **_kwargs) -> dict:
        """process login request"""
        if (
            user := Users.get_user_by_username(data.username)
        ) is None or user.password != data.password:
            return {
                "code": 1,
                "message": "user name and password not match",
                "success": False,
            }
        user.last_login = datetime.now()
        db.session.commit()
        current_app.logger.info(f"{user.name} login success")
        return {
            "data": {
                "accessToken": create_access_token(
                    identity=user, expires_delta=timedelta(days=1)
                ),
            }
        }


class RegisterParameters(JSONParameters):
    """
    Author: 1746104160
    msg: interface parameters for system register
    """

    username: str = String(
        required=True,
        validate=validate.And(
            validate.Length(min=6, max=16),
            validate.Regexp(
                r"^[a-zA-Z][a-zA-Z0-9_]{5,15}$", error="account is invalid"
            ),
        ),
        metadata={"description": "user name"},
    )
    password: str = String(
        required=True,
        validate=validate.And(
            validate.Length(min=6, max=16),
            validate.Regexp(
                r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,16}$",
                error="password is invalid",
            ),
        ),
        metadata={"description": "password"},
    )

    @post_load
    def process_register(self, data: "RegisterParameters", **_kwargs) -> dict:
        """process register request"""
        Users.add(name=data.username, password=data.password)
        current_app.logger.info(f"{data.username} register success")
        return {"message": "register success"}
