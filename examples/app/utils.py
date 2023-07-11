"""
Description: utils for the example app.
version: 0.1.1
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-07-11 13:10:31
FilePath: /flask_restx_marshmallow/examples/app/utils.py
"""
import getpass
import os

import toml
from flask import Blueprint
from flask_caching import Cache

from flask_restx_marshmallow import Api, SQLAlchemy

PROJECT_CONFIG: dict = (
    poetry
    if os.path.exists("pyproject.toml")
    and os.path.isfile("pyproject.toml")
    and os.path.getsize("pyproject.toml") > 0
    and (file := toml.load("pyproject.toml"))
    and isinstance(tool := file.get("tool"), dict)
    and isinstance(poetry := tool.get("poetry"), dict)
    else {}
)
LICENSE2URL: dict = {
    "Apache 2.0": "http://www.apache.org/licenses/LICENSE-2.0.html",
    "BSD 3-Clause": "https://opensource.org/licenses/BSD-3-Clause",
    "BSD 2-Clause": "https://opensource.org/licenses/BSD-2-Clause",
    "GPLv2": "https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html",
    "GPLv3": "https://www.gnu.org/licenses/gpl-3.0.en.html",
    "LGPLv3": "https://www.gnu.org/licenses/lgpl-3.0.en.html",
    "AGPLv3": "https://www.gnu.org/licenses/agpl-3.0.en.html",
    "GNU FDLv1.3": "https://www.gnu.org/licenses/fdl-1.3.en.html",
    "IPLv1": "https://opensource.org/licenses/IPL-1.0",
    "MIT": "https://opensource.org/licenses/MIT",
    "MPLv2.0": "https://opensource.org/licenses/MPL-2.0",
    "EPLv1": "https://opensource.org/licenses/EPL-1.0",
    "BSLv1": "https://opensource.org/licenses/BSL-1.0",
    "CC0v1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC-BYv4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC-BY-SA-v4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "CC-BY-NC-v4.0": "https://creativecommons.org/licenses/by-nc/4.0/",
    "CC-BY-NC-SA-v4.0": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    "CC-BY-ND-v4.0": "https://creativecommons.org/licenses/by-nd/4.0/",
    "CC-BY-NC-ND-v4.0": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
}
db: SQLAlchemy = SQLAlchemy()
cache: Cache = Cache()
api_blueprint: Blueprint = Blueprint(
    "api",
    __name__,
    url_prefix=f'/api/v{PROJECT_CONFIG.get("version", "1.0.0")}',
)
api: Api = Api(
    version=PROJECT_CONFIG.get("version", "1.0.0"),
    title=PROJECT_CONFIG.get("title", os.path.basename(os.getcwd())),
    description=PROJECT_CONFIG.get("description", ""),
    contact=PROJECT_CONFIG.get("authors", [getpass.getuser()])[0].split(" ")[0],
    contact_email=PROJECT_CONFIG.get("authors", [""])[0].split(" ")[1],
    contact_url=PROJECT_CONFIG.get("homepage", ""),
    license=PROJECT_CONFIG.get("license", "Apache 2.0"),
    license_url=LICENSE2URL[PROJECT_CONFIG.get("license", "Apache 2.0")],
)
api.init_app(api_blueprint)
