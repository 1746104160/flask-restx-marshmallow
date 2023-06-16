"""
Description: configs base for example app.
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-05 21:45:39
FilePath: /flask_restx_marshmallow/examples/app/configs.py
"""
# pylint: disable=invalid-name
import os
from dataclasses import dataclass
from datetime import timedelta
from secrets import token_urlsafe
from typing import Iterable


@dataclass
class BaseConfig:
    """
    Author: 1746104160
    msg: base config
    """

    BASE_ROOT: str = "/api/v1"
    CACHE_REDIS_URL: str = "redis://:@localhost:6379/0"
    DEVELOPING: bool = False
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(days=1)
    JWT_SECRET_KEY: str = "extremely secret key"
    SECRET_KEY: str = "very secret key"
    SQLALCHEMY_DATABASE_URI: str = f"sqlite://{os.getcwd()}/db.db"


@dataclass
class DevelopingConfig(BaseConfig):
    """
    Author: 1746104160
    msg: developing config
    """

    DEVELOPING: bool = True
    JWT_SECRET_KEY: str = token_urlsafe(128)
    JWT_TOKEN_LOCATION: Iterable[str] = ("headers", "query_string")
    SECRET_KEY: str = token_urlsafe()


@dataclass
class ProductionConfig(BaseConfig):
    """
    Author: 1746104160
    msg: production config
    """

    CACHE_REDIS_URL: str = os.environ["CACHE_REDIS_URL"]
    DEVELOPING: bool = False
    JWT_SECRET_KEY: str = (
        "LZKrguH6YM191DCC0R10fkjZRrKaeOo9taFMvsr2pOURJVT5Ul1EIYjw4CwUIoibjtAKPcgV5nKdOudJVL8_sL1mo3"
        + "lDk8meHOUEi2aZV9vO_dr7A2CRQe8Kp0OVF5ccAuGA9vxuMtPxchSIlt_XRrbjMLsvxqUcz4WIxtxWk1g"
    )
    JWT_BLACKLIST_ENABLED: bool = True
    JWT_BLACKLIST_TOKEN_CHECKS: Iterable[str] = ("access", "refresh")
    SECRET_KEY: str = "wRgTS1DZsBwYZJCRS3P0lpl9QI8zvjzzdpX2P0rutzo"
    SQLALCHEMY_DATABASE_URI: str = os.path.join(
        os.environ["SQLALCHEMY_DATABASE_URI"], "example"
    )
