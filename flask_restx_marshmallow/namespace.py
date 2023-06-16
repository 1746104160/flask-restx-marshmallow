"""
Description: patched namespace of flask_restx_marshmallow
version: 0.1.0
Author: 1746104160
Date: 2023-06-02 12:56:56
LastEditors: 1746104160 shaojiahong2001@outlook.com
LastEditTime: 2023-06-04 21:38:50
FilePath: /flask_restx_marshmallow/flask_restx_marshmallow/namespace.py
"""
from functools import wraps
from http import HTTPStatus
from types import FunctionType
from typing import Optional

import flask
from flask_restx import Namespace as OriginalNamespace
from flask_restx.utils import merge, unpack
from marshmallow.base import FieldABC
from typing_extensions import override
from webargs.flaskparser import parser
from webargs.multidictproxy import MultiDictProxy
from werkzeug import exceptions as http_exceptions

from .parameter import Parameters
from .schema import DefaultHTTPErrorSchema, Model, Schema, StandardSchema
from .util import API_DEFAULT_HTTP_CODE_MESSAGES


class Namespace(OriginalNamespace):
    """
    Author: 1746104160
    msg: Patched Namespace
    """

    def _handle_api_doc(self, cls: Model, doc: dict) -> None:
        cls.__apidoc__ = (
            None if doc is False else merge(getattr(cls, "__apidoc__", {}), doc)
        )

    @override
    def model(
        self,
        name: Optional[str] = None,
        model: Optional[Schema] = None,
        mask: Optional[str] = None,
        strict=False,
        **kwargs,
    ) -> Model:
        """Model registration decorator.

        Args:
            name (str, optional): model name. Defaults to None.
            model (Schema, optional): model instance. Defaults to None.
            mask (str, optional): mask info. Defaults to None.
            strict (bool, optional): whether strict. Defaults to False.

        Returns:
            Model: model instance
        """
        if isinstance(
            model,
            (Schema, FieldABC),
        ):
            if name is None:
                name = model.__class__.__name__
            api_model: Model = Model(name, model, mask=mask, strict=strict)
            api_model.__apidoc__ = kwargs
            return self.add_model(name, api_model)
        return super().model(
            name=name, model=model, mask=mask, strict=strict, **kwargs
        )

    def parameters(
        self,
        params: Parameters,
        *,
        locations: Optional[list[str]] = None,
        location: Optional[str] = None,
        as_kwargs: bool = False,
    ):
        """Endpoint parameters registration decorator.

        Args:
            params (Parameters): parameters
            locations (list[str], optional): locations in `query|header|formData|body|cookie`.
            Defaults to None.
            location (str, optional): location in `query|header|formData|body|cookie`.
            Defaults to None.
            as_kwargs (bool, optional): whether set parameters as keyword arguments or not.
            Defaults to False.
        """

        def decorator(func: FunctionType):
            """decorator

            Args:
                func (FunctionType): function to decorate
            """
            assert location or locations
            if locations is not None:
                assert set(locations) <= {
                    "query",
                    "header",
                    "formData",
                    "body",
                    "cookie",
                }

                @parser.location_loader("_and_".join(locations))
                def load_data(
                    request: flask.Request, schema: Parameters
                ) -> MultiDictProxy:
                    """load data from locations

                    Args:
                        request (flask.Request): request instance
                        schema (Parameters): parameters

                    Returns:
                        MultiDictProxy: json data
                    """
                    new_data: dict = {}
                    for location in locations:
                        match location:
                            case "body":
                                try:
                                    new_data.update(
                                        request.get_json(
                                            force=True, silent=True
                                        )
                                    )
                                except TypeError:
                                    pass
                            case "formData":
                                new_data.update(request.form.to_dict())
                                new_data.update(
                                    {
                                        key: value
                                        if len(value) > 1
                                        else value[0]
                                        for key, value in request.files.lists()
                                    }
                                )
                            case "query":
                                new_data.update(request.args)
                            case "header":
                                new_data.update(request.headers)
                            case "cookie":
                                new_data.update(request.cookies)
                    return MultiDictProxy(new_data, schema)

                load_data.__name__ = "load_data_from_" + "_and_".join(locations)
                return self.doc(params=params)(
                    self.response(code=HTTPStatus.UNPROCESSABLE_ENTITY)(
                        parser.use_args(
                            params,
                            location="_and_".join(locations),
                            as_kwargs=as_kwargs,
                        )(func)
                    )
                )
            assert location in {
                "query",
                "header",
                "formData",
                "body",
                "cookie",
            }
            location2webargs_location = {
                "query": "query",
                "header": "headers",
                "formData": "form",
                "body": "json",
                "cookie": "cookies",
            }
            return self.doc(params=params)(
                self.response(code=HTTPStatus.UNPROCESSABLE_ENTITY)(
                    parser.use_args(
                        params, location=location2webargs_location[location], as_kwargs=as_kwargs
                    )(func)
                )
            )

        return decorator

    @override
    def response(
        self,
        code: HTTPStatus = HTTPStatus.OK,
        description: Optional[str] = None,
        model: Optional[Schema | StandardSchema] = None,
        *,
        name: Optional[str] = None,
        message: str = "ok",
        **_kwargs,
    ):
        """Endpoint response OpenAPI documentation decorator.

        Args:
            code (HTTPStatus, optional): http status code. Defaults to HTTPStatus.OK.
            description (str, optional): description. Defaults to None.
            model (Schema | StandardSchema | DefaultHTTPErrorSchema, optional): model
            instance. Defaults to None.
            name (str, optional):model name. Defaults to None.
            message (str, optional): message. Defaults to "ok".
        """
        code = HTTPStatus(code)
        description = (
            API_DEFAULT_HTTP_CODE_MESSAGES[code]
            if description is None
            else description
        )
        model = (
            model
            if model
            else StandardSchema(message)
            if code == HTTPStatus.OK
            else DefaultHTTPErrorSchema(http_code=code)
            if code != HTTPStatus.NO_CONTENT
            else None
        )
        name = name if code == HTTPStatus.OK else f"HTTPError{code}"

        def response_serializer_decorator(func: FunctionType):
            """handles responses to serialize the returned value with the model

            Args:
                func (FunctionType): function to be called
            """

            def dump_wrapper(*args, **kwargs):
                response = func(*args, **kwargs)

                extra_headers: None = None
                if isinstance(response, flask.Response) or model is None:
                    return response
                if isinstance(response, tuple):
                    response, _code, extra_headers = unpack(response)
                else:
                    _code = code

                if HTTPStatus(_code) is code:
                    response = model.dump(response)
                return response, _code, extra_headers

            return dump_wrapper

        def decorator(func_or_class):
            if code.value in http_exceptions.default_exceptions:
                decorated_func_or_class = func_or_class
            elif isinstance(func_or_class, type):
                # pylint: disable=protected-access
                func_or_class._apply_decorator_to_methods(
                    response_serializer_decorator
                )
                decorated_func_or_class = func_or_class
            else:
                decorated_func_or_class = wraps(func_or_class)(
                    response_serializer_decorator(func_or_class)
                )
            api_model = (
                model
                if not model or isinstance(model, Model)
                else self.model(model=model, name=name)
            )
            if getattr(model, "many", False):
                api_model = [api_model]
            return self.doc(responses={code.value: (description, api_model)})(
                decorated_func_or_class
            )

        return decorator
