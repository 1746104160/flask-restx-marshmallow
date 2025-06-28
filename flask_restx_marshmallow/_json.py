# ruff: noqa: ANN401,FBT001
"""json of flask_restx_marshmallow."""

from importlib.util import find_spec, module_from_spec
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from collections.abc import Callable
    from json import JSONDecoder
    from typing import Any, Protocol

    class JSON(Protocol):
        @overload
        def dumps(
            self,
            __obj: Any,
            /,
            default: Callable[..., Any] | None = ...,
            option: int | None = ...,
        ) -> bytes: ...

        @overload
        def dumps(
            self,
            obj: Any,
            ensure_ascii: bool = ...,
            double_precision: int = ...,
            encode_html_chars: bool = ...,
            escape_forward_slashes: bool = ...,
            sort_keys: bool = ...,
            indent: int = ...,
            allow_nan: bool = ...,
            reject_bytes: bool = ...,
            default: Callable[..., Any] | None = None,
            separators: tuple[str, str] | None = None,
        ) -> str: ...

        @overload
        def dumps(
            self,
            s: str | bytes | bytearray,
            *,
            cls: type[JSONDecoder] | None = None,
            object_hook: Callable[[dict[Any, Any]], Any] | None = None,
            parse_float: Callable[[str], Any] | None = None,
            parse_int: Callable[[str], Any] | None = None,
            parse_constant: Callable[[str], Any] | None = None,
            object_pairs_hook: (Callable[[list[tuple[Any, Any]]], Any]) | None = None,
            **kwds: Any,
        ) -> Any: ...

        @overload
        def loads(self, __obj: bytes | bytearray | memoryview[int] | str) -> dict: ...  # noqa: PYI063

        @overload
        def loads(
            self,
            s: str | bytes | bytearray,
            precise_float: bool = ...,
        ) -> Any: ...

        @overload
        def loads(
            self,
            s: str | bytes | bytearray,
            *,
            cls: type[JSONDecoder] | None = None,
            object_hook: Callable[[dict[Any, Any]], Any] | None = None,
            parse_float: Callable[[str], Any] | None = None,
            parse_int: Callable[[str], Any] | None = None,
            parse_constant: Callable[[str], Any] | None = None,
            object_pairs_hook: (Callable[[list[tuple[Any, Any]]], Any]) | None = None,
            **kwds: Any,
        ) -> Any: ...

    json: JSON
else:
    modulespec = (
        find_spec(name="orjson") or find_spec(name="ujson") or find_spec(name="json")
    )
    json = module_from_spec(spec=modulespec)
    if loader := modulespec.loader:
        loader.exec_module(module=json)
