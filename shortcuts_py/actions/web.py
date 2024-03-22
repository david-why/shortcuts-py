from typing import Any, Literal, cast

from shortcuts_py.consts import Text
from shortcuts_py.shortcuts import Action
from shortcuts_py.templ import TemplateStr
from shortcuts_py.utils import parse_dict
from shortcuts_py.variable import FileVariable, Variable

__all__ = ['get_web_page_contents', 'get_contents_of_url']


def get_web_page_contents(url: Text) -> Variable:
    action = Action(
        'is.workflow.actions.getwebpagecontents', {'WFInput': TemplateStr(url).dump()}
    )
    return action.output('Contents of Web Page')


def get_contents_of_url(
    url: Text,
    method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] = 'GET',
    *,
    headers: dict[str, Any] = {},
    json: dict[Text, Any] | None = None,
    data: dict[Text, Any] | Variable | None = None,
) -> FileVariable:
    if json and data:
        raise ValueError('At most one of json, form, or file can be provided')
    if method == 'GET' and (json or data):
        raise ValueError('GET requests cannot have a body')
    if method != 'GET' and not (json or data):
        raise ValueError('Non-GET requests must have a body')
    params = {'ShowHeaders': True, 'WFURL': TemplateStr(url), 'WFHTTPMethod': method}
    if headers:
        params['WFHTTPHeaders'] = parse_dict(cast(dict[Text, Any], headers))
    elif json:
        params['WFJSONValues'] = parse_dict(json)
    elif isinstance(data, Variable):
        params['WFHTTPBodyType'] = 'File'
        params['WFRequestVariable'] = {
            'Value': data.dump(),
            'WFSerializationType': 'WFTextTokenAttachment',
        }
    elif data:
        params['WFHTTPBodyType'] = 'Form'
        params['WFFormValues'] = parse_dict(data)
    action = Action('is.workflow.actions.downloadurl', params)
    return action.output('Contents of URL', FileVariable)
