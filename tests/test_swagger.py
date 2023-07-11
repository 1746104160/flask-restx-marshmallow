'''
Description: 艺术集散地
version: 1.0.0
Author: 邵佳泓
Date: 2023-06-23 10:39:57
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-07-11 12:50:16
FilePath: /flask_restx_marshmallow/tests/test_swagger.py
'''
from typing import NoReturn

from flask import Flask, url_for
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.test import TestResponse

from examples.app.models.users import Users
from examples.app.utils import db


def test_swagger_json(
    app: Flask,
    client: FlaskClient,
) -> NoReturn:
    """test swagger doc"""
    if app.config["DEVELOPING"]:
        resp: TestResponse = client.get(url_for("api.specs"))
        assert resp.status_code == 200
    else:
        resp = client.get(
            url_for("api.specs"),
        )
        assert resp.status_code == 401
        admin = Users.get_user_by_username("administrator")
        accessToken = create_access_token(admin)
        resp = client.get(
            url_for("api.specs"),
            headers=Headers({"Authorization": f"Bearer {accessToken}"}),
        )
        assert resp.status_code == 200
        normal = Users.get_user_by_username("normal")
        accessToken = create_access_token(normal)
        if normal.valid is True:
            resp = client.get(
                url_for("api.specs"),
                headers=Headers({"Authorization": f"Bearer {accessToken}"}),
            )
            assert resp.status_code == 403
            normal.valid = True
            db.session.commit()
        else:
            resp = client.get(
                url_for("api.specs"),
                headers=Headers({"Authorization": f"Bearer {accessToken}"}),
            )
            assert resp.status_code == 401


def test_swagger_html(
    app: Flask,
    client: FlaskClient,
) -> NoReturn:
    """test swagger doc"""
    if app.config["DEVELOPING"]:
        resp: TestResponse = client.get(url_for("api.doc"))
        assert resp.status_code == 200
    else:
        resp = client.get(
            url_for("api.doc"),
        )
        assert resp.status_code == 401
        admin = Users.get_user_by_username("administrator")
        accessToken = create_access_token(admin)
        resp = client.get(
            url_for("api.doc"),
            headers=Headers({"Authorization": f"Bearer {accessToken}"}),
        )
        assert resp.status_code == 200
        normal = Users.get_user_by_username("normal")
        accessToken = create_access_token(normal)
        if normal.valid is True:
            resp = client.get(
                url_for("api.doc"),
                headers=Headers({"Authorization": f"Bearer {accessToken}"}),
            )
            assert resp.status_code == 403
            normal.valid = True
            db.session.commit()
        else:
            resp = client.get(
                url_for("api.doc"),
                headers=Headers({"Authorization": f"Bearer {accessToken}"}),
            )
            assert resp.status_code == 401
