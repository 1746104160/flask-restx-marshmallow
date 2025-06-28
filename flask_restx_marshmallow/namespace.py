"""patched namespace of flask_restx_marshmallow."""

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import is_dataclass
from functools import wraps
from http import HTTPStatus
from typing import TYPE_CHECKING, Literal, Self, Unpack
from urllib.parse import unquote

from docstring_parser import parse_from_object
from flask_restx.namespace import Namespace as OriginalNamespace
from marshmallow.constants import missing
from webargs.flaskparser import FlaskParser, is_json_request
from werkzeug.exceptions import BadRequest

from ._json import json
from .enum import Location
from .parameter import Parameters
from .schema import Schema
from .type import ResourceRoute, Success, TupleResponse
from .util import (
    Request,
    Response,
    class_schema,
    make_default_schema,
    raise_validation_error,
    security_helper,
    unpack,
)

if TYPE_CHECKING:
    from flask.views import MethodView

    from .type import DataclassInstance, SchemaInitKwargs

parser = FlaskParser(error_handler=raise_validation_error)  # type: ignore[assignment]


@parser.location_loader("auto")
def load_data(request: "Request", params: "Parameters") -> "dict":
    """Load data from locations.

    Args:
        request (Request): request
        params (Parameters): parameters

    Raises:
        BadRequest: if request is not JSON

    Returns:
        MultiDictProxy: json data
    """
    data = {}
    if "body" in params.locations:
        if is_json_request(request) is False:
            raise BadRequest(description="Invalid JSON body.")
        data.update(json.loads(request.get_data(cache=True)))
    for field, location, is_multiple in params.field_locations:
        match location:
            case "path":
                data[field] = (
                    missing
                    if request.view_args is None
                    else unquote(value)
                    if (value := request.view_args.get(field))
                    else missing
                )
            case "formData":
                data[field] = (
                    [
                        unquote(value) if value else missing
                        for value in request.form.getlist(field)
                    ]
                    or request.files.getlist(field)
                    if is_multiple
                    else unquote(_data)
                    if (_data := request.form.get(field))
                    else missing or request.files.get(field, missing)
                )
            case "query":
                values = [unquote(value) for value in request.args.getlist(field)] or [
                    missing,
                ]
                data[field] = values if is_multiple else values[0]
            case "header":
                values = [
                    unquote(value) for value in request.headers.getlist(field)
                ] or [missing]
                data[field] = values if is_multiple else values[0]
            case "cookie":
                values = [
                    unquote(value) for value in request.cookies.getlist(field)
                ] or [missing]
                data[field] = values if is_multiple else values[0]
    return data


class Namespace(OriginalNamespace):
    """Patched Namespace."""

    if TYPE_CHECKING:
        name: str
        description: str | None
        models: Mapping[str, Schema]
        resources: list[ResourceRoute]

    def security[A, S: str | Mapping[str, list[str] | str], M: "MethodView", **P](
        self: Self,
        security: S | Sequence[S],
    ) -> Callable[
        [Callable[P, TupleResponse[A] | Response | A] | type[M]],
        Callable[P, TupleResponse[A] | Response | A] | type[M],
    ]:
        """Endpoint security decorator.

        Args:
            security (S | Sequence[S]): security name or instance.

        Returns:
            (((((...) -> (TupleResponse | Response | Any)) | subclass[MethodView])) -> (((...) -> (TupleResponse | Response | Any)) | subclass[MethodView])): decorator.
        """  # noqa: E501
        security_ = (
            [security_helper(security)]
            if not isinstance(security, Sequence)
            else [security_helper(s) for s in security]
        )

        def decorator(
            func_or_class: Callable[P, TupleResponse[A] | Response | A] | type[M],
        ) -> Callable[P, TupleResponse[A] | Response | A] | type[M]:
            """Decorator.

            Args:
                func_or_class (((...) -> (TupleResponse | Response | Any)) | subclass[MethodView]): function or class to decorate.

            Returns:
                ((...) -> (TupleResponse | Response | Any)) | subclass[MethodView]) -> (((...) -> (TupleResponse | Response | Any)) | subclass[MethodView]) : decorated function or class.
            """  # noqa: E501
            if not isinstance(func_or_class, type):
                # * function case
                return self.doc(security=security_)(func_or_class)
            # * class case
            func_or_class.decorators.append(self.doc(security=security_))
            return func_or_class

        return decorator

    def parameters[A, T: "DataclassInstance", M: "MethodView", **P](
        self: Self,
        params: "type[DataclassInstance | Parameters] | Parameters",
        *,
        location: Location
        | Literal["query", "header", "formData", "body", "cookie", "path"]
        | None = None,
        as_kwargs: bool = False,
        validate: "Callable[[dict], bool] | None" = None,
        **kwargs: Unpack["SchemaInitKwargs"],
    ) -> Callable[
        [Callable[P, TupleResponse[A] | Response | A] | type[M]],
        Callable[P, TupleResponse[A] | Response | A] | type[M],
    ]:
        """Endpoint parameters registration decorator.

        Args:
            params (subclass[DataclassInstance | Parameters] | Parameters): parameters class or instance.
            as_kwargs (bool, optional): whether set parameters as key word arguments
                arguments or not. Defaults to False.
            validate ((dict) -> bool, optional): validation function. Defaults to None.
            location (Location, optional): location of the parameters. Defaults to None.
            **kwargs (ParamsInitKwargs): parameters initialization keyword.

        Raises:
            TypeError: if params is not subclass of Parameters

        Returns:
            (((((...) -> (TupleResponse | Response | Any)) | subclass[MethodView])) -> (((...) -> (TupleResponse | Response | Any)) | subclass[MethodView])): decorator.


        """  # noqa: E501
        if is_dataclass(params):
            params = class_schema(params, base=Parameters, use_origin_load=as_kwargs)
        if isinstance(params, type) and issubclass(params, Parameters):
            params = params(location=location, **kwargs)
        elif not isinstance(params, Parameters):
            msg = f"params must be subclass of Parameters, got {type(params).__name__}"
            raise TypeError(msg)

        def decorator(
            func_or_class: Callable[P, TupleResponse[A] | Response | A] | type[M],
        ) -> Callable[P, TupleResponse[A] | Response | A] | type[M]:
            """Decorator.

            Args:
                func_or_class (((...) -> (TupleResponse | Response | Any)) | subclass[MethodView]): function or class to decorate.

            Raises:
                ValueError: if location is None.

            Returns:
                ((...) -> (TupleResponse | Response | Any)) | subclass[MethodView]) -> (((...) -> (TupleResponse | Response | Any)) | subclass[MethodView]) : decorated function or class.
            """  # noqa: E501
            locations = params.locations
            if None in locations:
                msg = f"location must be specified, {params} has None location."
                raise ValueError(msg)
            if not isinstance(func_or_class, type):
                # * function case
                return parser.use_args(
                    params,
                    location="auto",
                    as_kwargs=as_kwargs,
                    validate=validate,
                )(self.doc(params=params)(func_or_class))
            # * class case
            func_or_class.decorators.append(
                parser.use_args(
                    params,
                    location="auto",
                    as_kwargs=as_kwargs,
                    validate=validate,
                )(self.doc(params=params)),
            )
            return func_or_class

        return decorator

    def responses[A, T: "DataclassInstance", M: "MethodView", **P](  # noqa: C901
        self: Self,
        *,
        success: bool = True,
        code: HTTPStatus | int = HTTPStatus.OK,
        schema: "type[T | Schema] | Schema | None" = None,
        message: str | None = None,
        headers: Iterable[str] | None = None,
        **kwargs: Unpack["SchemaInitKwargs"],
    ) -> Callable[
        [Callable[P, TupleResponse[A] | Response | A] | type[M]],
        Callable[P, TupleResponse[A] | Response | A] | type[M],
    ]:
        """Endpoint response OpenAPI documentation decorator.

        Args:
            success (bool, optional): whether response is successful or not. Defaults to True.
            code (HTTPStatus | int, optional): response status code. Defaults to HTTPStatus.OK.
            message (str, optional): response message. Defaults to None.
            schema (subclass[DataclassInstance | Schema] | Schema, optional): schema class or instance.
            headers (Iterable[str], optional): header fields. Defaults to None.
            **kwargs (SchemaInitKwargs): schema initialization keyword arguments.

        Raises:
            TypeError: if schema is not subclass of Schema.

        Returns:
           (((((...) -> (TupleResponse | Response | Any)) | subclass[MethodView])) -> (((...) -> (TupleResponse | Response | Any)) | subclass[MethodView])): decorator.
        """  # noqa: E501
        if is_dataclass(schema):
            schema = class_schema(schema, base=Schema)
        if isinstance(schema, type) and issubclass(schema, Schema):
            schema = schema(header_fields=headers, **kwargs)
        elif not isinstance(schema, Schema) and schema is not None:
            msg = f"schema must be subclass of Schema, got {type(schema).__name__}"
            raise TypeError(msg)

        def decorator(
            func_or_class: Callable[P, TupleResponse[A] | Response | A] | type[M],
        ) -> Callable[P, TupleResponse[A] | Response | A] | type[M]:
            """Decorator.

            Args:
                func_or_class (((...) -> (TupleResponse | Response | Any)) | subclass[MethodView]): function or class to decorate.

            Returns:
                ((...) -> (TupleResponse | Response | Any)) | subclass[MethodView]) -> (((...) -> (TupleResponse | Response | Any)) | subclass[MethodView]) : decorated function or class.
            """  # noqa: E501
            if schema is None:
                splits = func_or_class.__qualname__.split(".")
                name = f"{''.join(s.capitalize() for s in splits)}Schema"
                schema_ = make_default_schema(
                    name,
                    success=success,
                    code=code,
                    message=message,
                )(**kwargs)
                doc = parse_from_object(func_or_class)
                schema_.description = (
                    doc.long_description or doc.short_description or schema_.description
                )
            else:
                schema_ = schema
                name = type(schema_).__name__
                doc = parse_from_object(schema_)
                schema_.description = (
                    doc.long_description or doc.short_description or schema_.description
                )
            body_schema = schema_.copy_body_fields()
            header_schema = schema_.copy_header_fields()
            if not isinstance(func_or_class, type):
                # * function case

                @wraps(func_or_class)
                def wrapper(
                    *args: P.args,
                    **kwargs: P.kwargs,
                ) -> TupleResponse[A] | Response | A:
                    """Wrapper.

                    Args:
                        *args (P.args): arguments
                        **kwargs (P.kwargs): key word arguments

                    Returns:
                        TupleResponse | Response | Any: response
                    """
                    resp = func_or_class(*args, **kwargs)
                    extra_headers = {}

                    if isinstance(resp, Response):
                        return resp
                    if isinstance(resp, tuple):
                        response, status_code, extra_headers = unpack(resp)
                    else:
                        response = Success(result=resp)
                        status_code = HTTPStatus.OK
                    if HTTPStatus(status_code) is HTTPStatus(code):
                        response = body_schema.dump(response)
                        extra_headers = header_schema.dump(extra_headers)
                    return TupleResponse(
                        response=response,
                        status_code=status_code,
                        extra_headers=extra_headers,
                    )

                return self.doc(responses={str(HTTPStatus(code)): schema_})(wrapper)
            func_or_class.decorators.append(
                self.doc(responses={str(HTTPStatus(code)): schema_}),
            )
            return func_or_class

        return decorator
