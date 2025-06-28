"""Enums for flask_restx_marshmallow."""

from enum import IntEnum, StrEnum


class ResponseCode(IntEnum):
    """response code."""

    SUCCESS = 0
    ERROR = -1
    WARNING = 1


class Location(StrEnum):
    """Location Enum."""

    FORM_DATA = "formData"
    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"
    BODY = "body"
    PATH = "path"


class ResponseType(IntEnum):
    """response code."""

    SUCCESS = 0
    ERROR = -1
    WARNING = 1
