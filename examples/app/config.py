"""
Description: config for example app.
version: 0.1.1
Author: 1746104160
Date: 2023-06-05 14:57:33
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-14 17:01:00
FilePath: /flask_restx_marshmallow/examples/app/config.py
"""
from dataclasses import dataclass

from app.configs import ProductionConfig


@dataclass
class Config(ProductionConfig):
    """
    Author: 1746104160
    msg: user custom config
    """

    # to enable swagger ui without authentication
    SWAGGER_UI_CDN = "cdnjs.com"
    SWAGGER_UI_VERSION = "5.0.0"
    DEVELOPING = True
