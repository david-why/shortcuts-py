from typing import Any, Literal, overload

from shortcuts_py.consts import Number, Text
from shortcuts_py.shortcuts import Action
from shortcuts_py.templ import TemplateStr
from shortcuts_py.utils import parse_attachment, parse_dict
from shortcuts_py.variable import NumberVariable, TextVariable, Variable

__all__ = ['text', 'show_result', 'ask_for_input', 'requests', 'b64encode']


def text(text: Text) -> TextVariable:
    action = Action(
        'is.workflow.actions.gettext', {'WFTextActionText': TemplateStr(text).dump()}
    )
    return action.output('Text', TextVariable)


def show_result(text: Text) -> None:
    Action('is.workflow.actions.showresult', {'Text': TemplateStr(text)})


@overload
def ask_for_input(
    type: Literal['URL', 'Date', 'Date and Time', 'Time'],
    prompt: str,
    *,
    default: Text | None = None,
) -> Variable: ...
@overload
def ask_for_input(
    type: Literal['Text'] | type[str],
    prompt: str,
    *,
    default: Text | None = None,
) -> TextVariable: ...
@overload
def ask_for_input(
    type: Literal['Number'] | type[int] | type[float],
    prompt: str,
    *,
    allow_negative: bool = True,
    allow_decimal: bool = True,
    default: Number | None = None,
) -> Variable: ...
def ask_for_input(
    type, prompt, *, default=None, allow_negative=True, allow_decimal=True
):
    if type is int:
        allow_decimal = False
    type = {int: 'Number', float: 'Number', str: 'Text'}.get(type, type)
    params = {'WFAskActionPrompt': prompt, 'WFInputType': type}
    suffix = type.title().replace(' ', '') if type != 'Text' else ''
    if default is not None:
        if isinstance(default, (int, float)):
            default = str(default)
        if suffix == 'Number':
            params['WFAskActionDefaultAnswerNumber'] = parse_attachment(default)
        else:
            params[f'WFAskActionDefaultAnswer{suffix}'] = TemplateStr(default)
    if type == 'Number':
        params['WFAskActionAllowsDecimalNumbers'] = allow_decimal
        params['WFAskActionAllowsNegativeNumbers'] = allow_negative
    action = Action('is.workflow.actions.ask', params)
    var = action.output('Provided Input')
    if type == 'Number':
        var = NumberVariable.of(var)
    elif type == 'Text':
        var = TextVariable.of(var)
    return var


class requests:
    @staticmethod
    def request(
        method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
        url: str,
        *,
        headers: dict[str, Any] = {},
        json: dict[Text, Any] | None = None,
        data: dict[Text, Any] | Variable | None = None,
    ) -> Variable:
        if json and data:
            raise ValueError('At most one of json, form, or file can be provided')
        if method == 'GET' and (json or data):
            raise ValueError('GET requests cannot have a body')
        if method != 'GET' and not (json or data):
            raise ValueError('Non-GET requests must have a body')
        params = {'ShowHeaders': True, 'WFURL': url, 'WFHTTPMethod': method}
        if headers:
            params['WFHTTPHeaders'] = headers
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
        return action.output('Contents of URL')

    @staticmethod
    def get(url: str, *, headers: dict[str, Any] = {}) -> Variable:
        return requests.request('GET', url, headers=headers)

    @staticmethod
    def post(
        url: str,
        *,
        headers: dict[str, Any] = {},
        json: dict[Text, Any] | None = None,
        data: dict[Text, Any] | Variable | None = None,
    ) -> Variable:
        return requests.request('POST', url, headers=headers, json=json, data=data)

    @staticmethod
    def put(
        url: str,
        *,
        headers: dict[str, Any] = {},
        json: dict[Text, Any] | None = None,
        data: dict[Text, Any] | Variable | None = None,
    ) -> Variable:
        return requests.request('PUT', url, headers=headers, json=json, data=data)

    @staticmethod
    def patch(
        url: str,
        *,
        headers: dict[str, Any] = {},
        json: dict[Text, Any] | None = None,
        data: dict[Text, Any] | Variable | None = None,
    ) -> Variable:
        return requests.request('PATCH', url, headers=headers, json=json, data=data)

    @staticmethod
    def delete(
        url: str,
        *,
        headers: dict[str, Any] = {},
        json: dict[Text, Any] | None = None,
        data: dict[Text, Any] | Variable | None = None,
    ) -> Variable:
        return requests.request('DELETE', url, headers=headers, json=json, data=data)


def b64encode(
    data: Variable,
    line_break: Literal[
        'Every 64 Characters', 'Every 76 Characters', 'None'
    ] = 'Every 76 Characters',
) -> Variable:
    action = Action(
        'is.workflow.actions.base64encode',
        {'WFInput': parse_attachment(data), 'WFBase64LineBreakMode': line_break},
    )
    return action.output('Base64 Encoded', TextVariable)
