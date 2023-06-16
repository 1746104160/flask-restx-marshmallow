"""
Description: response schema for system login
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-14 20:22:14
FilePath: /flask_restx_marshmallow/examples/app/managers/auth_manager/schemas.py
"""
from marshmallow.fields import Nested, String

from flask_restx_marshmallow import StandardSchema


class LoginSchema(StandardSchema):
    """
    Author: 1746104160
    msg: response schema for system login
    """

    data: dict = Nested(
        {"accessToken": String(metadata={"description": "JWT token"})},
        metadata={"description": "data"},
    )
