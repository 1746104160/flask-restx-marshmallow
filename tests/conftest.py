"""
Description: flask_restx_marshmallow
version: 0.1.1
Author: 1746104160
Date: 2023-07-11 12:39:16
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-07-11 12:48:43
FilePath: /flask_restx_marshmallow/tests/conftest.py
"""
import pytest
from flask import Flask

from examples.app import create_app

flask_app: Flask = create_app()


@pytest.fixture()
def app() -> Flask:
    """test flask app"""
    flask_app.config["TESTING"] = True
    yield flask_app
