from typing import Literal, overload

from shortcuts_py.consts import Number, Text
from shortcuts_py.shortcuts import Action
from shortcuts_py.templ import TemplateStr
from shortcuts_py.utils import parse_attachment
from shortcuts_py.variable import DictVariable, NumberVariable, TextVariable, Variable

__all__ = [
    'text',
    'show_alert',
    'show_result',
    'ask_for_input',
    'base64_encode',
    'get_dictionary',
]


def text(text: Text) -> TextVariable:
    action = Action(
        'is.workflow.actions.gettext', {'WFTextActionText': TemplateStr(text).dump()}
    )
    return action.output('Text', TextVariable)


def show_alert(
    message: Text, title: Text | None = None, *, show_cancel: bool = True
) -> None:
    data = {
        'WFAlertActionMessage': TemplateStr(message).dump(),
        'WFAlertActionCancelButtonShown': show_cancel,
    }
    if title is not None:
        data['WFAlertActionTitle'] = TemplateStr(title).dump()
    Action('is.workflow.actions.alert', data)


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


def base64_encode(
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


def get_dictionary(data: Variable) -> DictVariable:
    action = Action(
        'is.workflow.actions.detect.dictionary', {'WFInput': parse_attachment(data)}
    )
    return action.output('Dictionary', DictVariable)
