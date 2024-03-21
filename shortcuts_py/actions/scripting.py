# This file is generated by scripts/generate_actions.py.

from typing import Literal, overload

from shortcuts_py.consts import Number, Text
from shortcuts_py.shortcuts import Action
from shortcuts_py.templ import TemplateStr
from shortcuts_py.utils import parse_attachment
from shortcuts_py.variable import DictVariable, NumberVariable, TextVariable, Variable

__all__ = [
    'ask_for_input',
    'base64_encode',
    'get_dictionary',
    'show_alert',
    'show_result',
]


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


def base64_encode(
    data: Variable,
    line_break: Literal[
        'Every 64 Characters', 'Every 76 Characters', 'None'
    ] = 'Every 76 Characters',
):
    params = {'WFInput': parse_attachment(data), 'WFBase64LineBreakMode': line_break}
    action = Action('is.workflow.actions.base64encode', params)
    return action.output('Base64 Encoded', TextVariable)


def get_dictionary(data: Variable):
    params = {'WFInput': parse_attachment(data)}
    action = Action('is.workflow.actions.detect.dictionary', params)
    return action.output('Dictionary', DictVariable)


def show_alert(message: Text, title: Text | None = None, show_cancel: bool = True):
    params = {
        'WFAlertActionMessage': TemplateStr(message),
        'WFAlertActionCancelButtonShown': show_cancel,
    }
    if title is not None:
        params['WFAlertActionTitle'] = TemplateStr(title)
    action = Action('is.workflow.actions.alert', params)


def show_result(text: Text):
    params = {'Text': TemplateStr(text)}
    action = Action('is.workflow.actions.showresult', params)