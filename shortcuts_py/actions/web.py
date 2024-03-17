from shortcuts_py.consts import Text
from shortcuts_py.shortcuts import Action
from shortcuts_py.variable import TemplateStr, Variable

__all__ = ['get_web_page_contents']


def get_web_page_contents(url: Text) -> Variable:
    action = Action(
        'is.workflow.actions.getwebpagecontents', {'WFInput': TemplateStr(url).dump()}
    )
    return action.output('Contents of Web Page')
