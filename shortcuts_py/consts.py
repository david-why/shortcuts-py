from enum import StrEnum
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from shortcuts_py.variable import TemplateStr, Variable

Text = Union[str, 'TemplateStr', 'Variable']
Number = Union[int, float, 'Variable']


class WorkflowType(StrEnum):
    ShareSheet = 'ActionExtension'
    QuickActions = 'QuickActions'
    Watch = 'Watch'
    MenuBar = 'MenuBar'
    WhatsOnScreen = 'ReceivesOnScreenContent'


ALL_WORKFLOW_TYPES = [
    WorkflowType.ShareSheet,
    WorkflowType.QuickActions,
    WorkflowType.Watch,
    WorkflowType.MenuBar,
    WorkflowType.WhatsOnScreen,
]
