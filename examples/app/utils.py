"""
Description: utils for the example app.
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-14 16:31:24
FilePath: /flask_restx_marshmallow/examples/app/utils.py
"""
from app.config import Config
from flask import Blueprint
from flask_caching import Cache

from flask_restx_marshmallow import Api, SQLAlchemy

db: SQLAlchemy = SQLAlchemy()
api_blueprint: Blueprint = Blueprint(
    "example api", __name__, url_prefix=Config.BASE_ROOT
)
cache: Cache = Cache()
api: Api = Api(
    version="0.1.0",
    title="example app",
    description="api interface for example app",
    contact="1746104160",
    contact_email="shaojiahong2001@outlook.com",
    contact_url="https://github.com/1746104160",
    license="MIT",
    license_url="https://mit-license.org/",
)
api.init_app(api_blueprint)
