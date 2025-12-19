import inspect
from typing import Any, Generic, TypeVar, get_args, get_origin

from aiohttp import web

T = TypeVar('T')

def dashed(s: str) -> list[str]:
    return s.split("-")

class Path(Generic[T]):

    @staticmethod
    def provide(request: web.Request, key: str, value_type: list[T]) -> Any:
        value = request.match_info.get(key)
        if value is None:
            return None

        if value_type:
            return value_type[0](value)

        return value

class Provider:

    def __init__(self):
        self.__types = {
            web.Request: lambda request, *args: request,
            Path: Path.provide,
        }

    def __provide(self, request: web.Request, arg_name: str, parameter: inspect.Parameter) -> Any:
        # annotation type... get_origin(list[str]) -> list, "or" is here because get_origin(str) -> None
        parameter_type = get_origin(parameter.annotation) or parameter.annotation
        # annotation parameter arguments get_args(tuple[int, str, bool]) -> (int, str, bool)
        parameter_args = get_args(parameter.annotation)
        provider = self.__types.get(parameter_type)
        if provider is None:
            raise Exception("Invalid annotation")

        return provider(request, arg_name, parameter_args)

    @web.middleware
    async def middleware(self, request: web.Request, handler) -> web.Response:
        sig = inspect.signature(handler)
        kwargs = {arg_name: self.__provide(request, arg_name, param) for arg_name, param in sig.parameters.items()}
        return await handler(**kwargs)
