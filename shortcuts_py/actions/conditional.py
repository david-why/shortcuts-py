from typing import Type, TypeVar
from uuid import uuid4

from shortcuts_py.condition import Condition
from shortcuts_py.data import shortcut_data
from shortcuts_py.shortcuts import Action
from shortcuts_py.variable import Variable


__all__ = ['if_begin', 'if_otherwise', 'if_end']

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
