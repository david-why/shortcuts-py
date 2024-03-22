from typing import Any, Callable, Literal, Self, Type, TypeVar
from uuid import uuid4

from shortcuts_py.condition import Condition
from shortcuts_py.data import shortcut_data
from shortcuts_py.shortcuts import Action
from shortcuts_py.utils import parse_attachment, pop_stack
from shortcuts_py.variable import TextVariable, Variable

__all__ = ['if_begin', 'if_otherwise', 'if_end', 'If', 'Otherwise']

VariableT = TypeVar('VariableT', bound=Variable)


def if_begin(condition: Condition) -> None:
    assert shortcut_data['started']
    grouping = str(uuid4()).upper()
    Action(
        'is.workflow.actions.conditional',
        {'GroupingIdentifier': grouping, 'WFControlFlowMode': 0, **condition.dump()},
    )
    shortcut_data['stack'].append(
        {'type': 'if', 'grouping': grouping, 'otherwise': False}
    )


def if_otherwise() -> None:
    assert shortcut_data['started']
    if not shortcut_data['stack']:
        raise RuntimeError('No if block to define otherwise')
    if shortcut_data['stack'][-1]['otherwise']:
        raise RuntimeError('Otherwise already defined')
    entry = shortcut_data['stack'][-1]
    entry['otherwise'] = True
    Action(
        'is.workflow.actions.conditional',
        {'GroupingIdentifier': entry['grouping'], 'WFControlFlowMode': 1},
    )


def if_end(variable_cls: Type[VariableT] = Variable) -> VariableT:
    assert shortcut_data['started']
    if not shortcut_data['stack']:
        raise RuntimeError('No if block to end')
    entry = shortcut_data['stack'].pop()
    action = Action(
        'is.workflow.actions.conditional',
        {'GroupingIdentifier': entry['grouping'], 'WFControlFlowMode': 2},
    )
    return action.output('If Result', variable_cls)


class If:
    def __init__(self, condition: Condition):
        self.condition = condition
        self.data = {
            'type': 'if',
            'grouping': str(uuid4()).upper(),
            'otherwise': False,
            'no_finish': True,
            'finish': self.on_finish,
        }
        self._result = None

    def __call__(self, func: Callable[[], Any]) -> Self:
        shortcut_data['stack'].append(self.data)
        Action(
            'is.workflow.actions.conditional',
            {
                'GroupingIdentifier': self.data['grouping'],
                'WFControlFlowMode': 0,
                **self.condition.dump(),
            },
        )
        func()
        pop_stack()
        self.data['no_finish'] = False
        return self

    def otherwise(self, func: Callable[[], Any]) -> Variable:
        if self.data['otherwise']:
            raise RuntimeError('Otherwise already defined')
        self.data['otherwise'] = True
        self.data['no_finish'] = True
        Action(
            'is.workflow.actions.conditional',
            {'GroupingIdentifier': self.data['grouping'], 'WFControlFlowMode': 1},
        )
        func()
        action = Action(
            'is.workflow.actions.conditional',
            {'GroupingIdentifier': self.data['grouping'], 'WFControlFlowMode': 2},
        )
        assert shortcut_data['stack'][-1] is self.data
        shortcut_data['stack'].pop()
        self._result = action.output('If Result')
        return self._result

    def on_finish(self):
        if self._result is not None:
            return self._result
        action = Action(
            'is.workflow.actions.conditional',
            {'GroupingIdentifier': self.data['grouping'], 'WFControlFlowMode': 2},
        )
        self._result = action.output('If Result')
        return self._result

    @property
    def result(self) -> Variable:
        if self._result is not None:
            return self._result
        self._result = self.on_finish()
        return self._result


class Otherwise:
    def __init__(self, if_: If):
        self.if_ = if_

    def __call__(self, func: Callable[[], Any]) -> Variable:
        return self.if_.otherwise(func)


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
