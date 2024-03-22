from typing import Any, Literal

from shortcuts_py.actions.scripting import get_dictionary
from shortcuts_py.actions.web import get_contents_of_url
from shortcuts_py.consts import Text
from shortcuts_py.variable import (
    ContentItemClass,
    DictVariable,
    FileVariable,
    TextVariable,
    Variable,
)

__all__ = ['request', 'get', 'post', 'put', 'patch', 'delete']


class Response:
    def __init__(self, variable: FileVariable):
        self._variable = variable

    def json(self) -> DictVariable:
        return get_dictionary(self._variable)

    @property
    def text(self) -> TextVariable:
        return ContentItemClass.Text(self._variable)

    @property
    def data(self) -> FileVariable:
        return self._variable


def request(
    method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    url: Text,
    *,
    headers: dict[str, Any] = {},
    json: dict[Text, Any] | None = None,
    data: dict[Text, Any] | Variable | None = None,
) -> Response:
    result = get_contents_of_url(url, method, headers=headers, json=json, data=data)
    return Response(result)


def get(url: Text, *, headers: dict[str, Any] = {}) -> Response:
    return request('GET', url, headers=headers)


def post(
    url: Text,
    *,
    headers: dict[str, Any] = {},
    json: dict[Text, Any] | None = None,
    data: dict[Text, Any] | Variable | None = None,
) -> Response:
    return request('POST', url, headers=headers, json=json, data=data)


def put(
    url: Text,
    *,
    headers: dict[str, Any] = {},
    json: dict[Text, Any] | None = None,
    data: dict[Text, Any] | Variable | None = None,
) -> Response:
    return request('PUT', url, headers=headers, json=json, data=data)


def patch(
    url: Text,
    *,
    headers: dict[str, Any] = {},
    json: dict[Text, Any] | None = None,
    data: dict[Text, Any] | Variable | None = None,
) -> Response:
    return request('PATCH', url, headers=headers, json=json, data=data)


def delete(
    url: Text,
    *,
    headers: dict[str, Any] = {},
    json: dict[Text, Any] | None = None,
    data: dict[Text, Any] | Variable | None = None,
) -> Response:
    return request('DELETE', url, headers=headers, json=json, data=data)
