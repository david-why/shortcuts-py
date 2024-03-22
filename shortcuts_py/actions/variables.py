from shortcuts_py.shortcuts import Action
from shortcuts_py.utils import parse_attachment
from shortcuts_py.variable import Variable, VariableVariable

__all__ = ['set_variable', 'get_variable', 'add_to_variable']


def set_variable(name: str, value: Variable) -> VariableVariable:
    params = {'WFVariableName': name, 'WFInput': parse_attachment(value)}
    Action('is.workflow.actions.setvariable', params)
    return VariableVariable(name)


def get_variable(variable: Variable) -> None:
    params = {'WFVariable': parse_attachment(variable)}
    Action('is.workflow.actions.getvariable', params)


def add_to_variable(name: str, value: Variable) -> VariableVariable:
    params = {'WFVariableName': name, 'WFInput': parse_attachment(value)}
    Action('is.workflow.actions.appendvariable', params)
    return VariableVariable(name)
