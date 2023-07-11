"""
Description: create backend service
version: 0.1.1
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 13:08:18
FilePath: /flask_restx_marshmallow/examples/app/__init__.py
"""
import datetime
import random
import re
import sys
from http import HTTPStatus
from secrets import token_urlsafe

from app.config import Config
from app.configs import PROJECT_NAME
from app.managers import auth_ns, role_ns, route_ns, user_ns
from app.models import Roles, Routes, Users
from app.utils import api, api_blueprint, cache, db
from flask import Flask, Response, jsonify
from flask_jwt_extended import JWTManager
from sqlalchemy import exc


def create_app(config=Config) -> Flask:
    """
    Author: 1746104160
    msg: create backend service
    """
    app: Flask = Flask(__name__)
    app.config.from_object(config)
    jwt: JWTManager = JWTManager(app)

    db.init_app(app)
    api.add_namespace(auth_ns, path="/auth/user")
    api.add_namespace(role_ns, path="/admin/role")
    api.add_namespace(route_ns, path="/admin/route")
    api.add_namespace(user_ns, path="/admin/user")
    if app.config["DEVELOPING"] is True:
        api.register_doc(app, api_blueprint)
    else:
        api.register_doc_production(app, api_blueprint)

    app.register_blueprint(api_blueprint)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(
        _jwt_header: dict[str, str], jwt_payload: dict
    ) -> bool:
        jti: str = jwt_payload["jti"]
        exp: int = jwt_payload["exp"]
        user_id: int = jwt_payload["sub"]
        return (
            exp < datetime.datetime.now().timestamp()
            or cache.get(jti)
            or not Users.judge_user_valid_by_id(user_id)
        )

    @jwt.user_identity_loader
    def user_identity_lookup(user: Users) -> str:
        return user.id.hex

    @jwt.user_lookup_loader
    def user_lookup_callback(
        _jwt_header: dict[str, str], jwt_payload: dict[str, str]
    ) -> Users:
        return Users.get_user_by_id(jwt_payload["sub"])

    @jwt.unauthorized_loader
    def unauthorized_callback(*_args, **_kwargs) -> Response:
        res: Response = jsonify(
            {
                "code": HTTPStatus.UNAUTHORIZED.value,
                "message": "user unauthorized",
                "success": False,
            }
        )
        res.status_code = HTTPStatus.UNAUTHORIZED.value
        return res

    @jwt.token_verification_failed_loader
    def token_verification_failed_callback(*_args, **_kwargs) -> Response:
        res: Response = jsonify(
            {
                "code": HTTPStatus.UNAUTHORIZED.value,
                "message": "user token verification failed",
                "success": False,
            }
        )
        res.status_code = HTTPStatus.UNAUTHORIZED.value
        return res

    @jwt.expired_token_loader
    def expired_token_callback(*_args, **_kwargs) -> Response:
        res: Response = jsonify(
            {
                "code": HTTPStatus.UNAUTHORIZED.value,
                "message": "user token expired",
                "success": False,
            }
        )
        res.status_code = HTTPStatus.UNAUTHORIZED.value
        return res

    @jwt.invalid_token_loader
    def invalid_token_callback(*_args, **_kwargs) -> Response:
        res: Response = jsonify(
            {
                "code": HTTPStatus.UNAUTHORIZED.value,
                "message": "user token invalid",
                "success": False,
            }
        )
        res.status_code = HTTPStatus.UNAUTHORIZED.value
        return res

    @jwt.revoked_token_loader
    def revoked_token_callback(*_args, **_kwargs) -> Response:
        res: Response = jsonify(
            {
                "code": HTTPStatus.UNAUTHORIZED.value,
                "message": "user is banned",
                "success": False,
            }
        )
        res.status_code = HTTPStatus.UNAUTHORIZED.value
        return res

    @app.cli.command("create_db", help="创建数据库")
    def create_db() -> None:
        try:
            db.create_all()
            app.logger.info("Database created.")
        except exc.OperationalError:
            uri: str = app.config["SQLALCHEMY_DATABASE_URI"]
            host: str = re.findall(r"@(\S+):", uri)[0]
            user: str = re.findall(r"://(\S+):", uri)[0].split(":")[0]
            password: str = re.findall(r":(\S+)@", uri)[0].split(":")[1]
            port: str = int(re.findall(r"@(\S+)/", uri)[0].split(":")[1])
            if uri.startswith("mysql"):
                from pymysql import connect, err  # pylint: disable=import-error
                from pymysql.connections import (
                    Connection,  # pylint: disable=import-error
                )
                from pymysql.cursors import (
                    Cursor,
                )  # pylint: disable=import-error

                try:
                    conn: Connection = connect(
                        host=host, user=user, password=password, port=port
                    )
                    cur: Cursor = conn.cursor()
                    sql: str = f"create database if not exists {PROJECT_NAME};"
                    cur.execute(sql)
                    conn.commit()
                    db.create_all()
                    app.logger.info("Database created.")
                except err.OperationalError:
                    app.logger.error("Database uri not correct.")
                    sys.exit(1)
            elif uri.startswith("postgresql"):
                from psycopg2 import (
                    connect,
                    errors,
                )  # pylint: disable=import-error
                from psycopg2.extensions import (  # pylint: disable=import-error
                    ISOLATION_LEVEL_AUTOCOMMIT,
                    connection,
                    cursor,
                )

                try:
                    conn: connection = connect(
                        host=host, user=user, password=password, port=port
                    )
                    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                    cur: cursor = conn.cursor()
                    sql: str = f"create database {PROJECT_NAME};"
                    cur.execute(sql)
                    conn.commit()
                    db.create_all()
                    app.logger.info("Database created.")
                except errors.OperationalError:
                    app.logger.error("Database uri not correct.")
                    sys.exit(1)
        except exc.ArgumentError:
            app.logger.error("Database uri not correct.")
            sys.exit()

    @app.cli.command("init_db", help="initialize database")
    def init_db() -> None:
        db.drop_all()
        db.create_all()
        Routes.add("/personal", "personal info")
        Routes.add("/system", "system manage")
        Routes.add("/system/role", "system role manage")
        Routes.add("/system/route", "system route manage")
        Routes.add("/system/user", "system user manage")
        Roles.add(
            name="admin",
            description="admin user",
            routes=["/system", "/personal"],
        )
        Roles.add(
            name="usermanager",
            description="user manager",
            routes=["/system/user", "/personal"],
        )
        Roles.add(
            name="rolemanager",
            description="role manager",
            routes=["/system/role", "/personal"],
        )
        Roles.add(
            name="routemanager",
            description="route manager",
            routes=["/system/route", "/personal"],
        )
        Roles.add(name="user", description="normal user")
        Users.add(
            name="administrator", password=token_urlsafe(6), roles=["admin"]
        )
        Users.add(
            name="usermanager", password=token_urlsafe(6), roles=["usermanager"]
        )
        Users.add(
            name="rolemanager", password=token_urlsafe(6), roles=["rolemanager"]
        )
        Users.add(
            name="routemanager",
            password=token_urlsafe(6),
            roles=["routemanager"],
        )
        for i in range(10):
            Users.add(
                name=f"testuser{i}",
                password=token_urlsafe(6),
                roles=random.sample(
                    ["usermanager", "rolemanager", "routemanager", "user"],
                    random.randint(1, 3),
                ),
            )

    @app.cli.command("drop_db", help="drop database")
    def drop_db() -> None:
        db.drop_all()

    return app
