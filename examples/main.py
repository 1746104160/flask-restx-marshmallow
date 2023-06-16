"""
Description: flask_restx_marshmallow
version: 0.1.0
Author: 1746104160
Date: 2023-06-05 14:43:22
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-16 16:53:10
FilePath: /flask_restx_marshmallow/examples/main.py
"""
from app import create_app
from flask import Flask

app: Flask = create_app()
if __name__ == "__main__":
    app.run()
