"""
Description: flask-restx-marshmallow
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 16:32:05
FilePath: /flask_restx_marshmallow/flask-restx-marshmallow/__init__.py
"""
from flask_restx import Resource

from .api import Api
from .namespace import Namespace
from .parameter import (
    CookieParameters,
    HeaderParameters,
    JSONParameters,
    PostFormParameters,
    QueryParameters,
)
from .schema import (
    DefaultHTTPErrorSchema,
    Schema,
    SQLAlchemyAutoSchema,
    SQLAlchemySchema,
    StandardSchema,
)
from .sqlalchemy import SQLAlchemy
from .swagger import Swagger
from .util import File, permission_required
