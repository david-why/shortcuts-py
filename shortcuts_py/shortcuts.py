import plistlib
from typing import Any
from uuid import uuid4

from shortcuts_py.consts import ALL_WORKFLOW_TYPES, WorkflowType
from shortcuts_py.utils import sign_shortcut
from shortcuts_py.variable import ContentItemClass, TemplateStr, Variable


class Action:
    def __init__(self, identifier: str, parameters: dict | None = None) -> None:
        assert shortcut_data
        shortcut_data['actions'].append(self)
        self.identifier = identifier
        self.parameters = parameters or {}

    def output(self, name: str) -> Variable:
        if 'UUID' not in self.parameters:
            self.parameters['UUID'] = str(uuid4()).upper()
        return Variable(
            'ActionOutput', OutputName=name, OutputUUID=self.parameters['UUID']
        )

    def dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {'WFWorkflowActionIdentifier': self.identifier}
        if self.parameters:
            parameters = {}
            for param, value in self.parameters.items():
                if isinstance(value, (Variable, TemplateStr)):
                    parameters[param] = value.dump()
                else:
                    parameters[param] = value
            data['WFWorkflowActionParameters'] = parameters
        return data


shortcut_data = None


def begin_shortcut():
    global shortcut_data
    if shortcut_data is not None:
        raise RuntimeError('Shortcut already started')
    shortcut_data = {'actions': [], 'input': None}


def build_shortcut(sign: bool = False):
    global shortcut_data
    if shortcut_data is None:
        raise RuntimeError('Shortcut not started')
    data = {
        'WFWorkflowMinimumClientVersionString': '900',
        'WFWorkflowMinimumClientVersion': 900,
        'WFWorkflowIcon': {
            'WFWorkflowIconStartColor': 1440408063,
            'WFWorkflowIconGlyphNumber': 61440,
        },
        'WFWorkflowClientVersion': '1505.3.0.2',
        'WFWorkflowOutputContentItemClasses': [],
        'WFWorkflowHasOutputFallback': False,
        'WFWorkflowActions': [x.dump() for x in shortcut_data['actions']],
        'WFWorkflowImportQuestions': [],
        'WFQuickActionSurfaces': [],
        'WFWorkflowTypes': [],
        'WFWorkflowHasShortcutInputVariables': shortcut_data['input'] is not None,
    }
    if shortcut_data['input'] is not None:
        data['WFWorkflowInputContentItemClasses'] = [
            x.value for x in shortcut_data['input']['types']
        ]
        data['WFWorkflowTypes'] = [x.value for x in shortcut_data['input']['sources']]
        if shortcut_data['input']['or_else'] is not None:
            data['WFWorkflowNoInputBehavior'] = {
                'Name': 'WFWorkflowNoInputBehaviorAskForInput',
                'Parameters': {'ItemClass': shortcut_data['input']['or_else'].value},
            }
            if shortcut_data['input']['multiple']:
                data['WFWorkflowNoInputBehavior']['Parameters'][
                    'SerializedParameters'
                ] = {'WFSelectMultiple': True}
    shortcut_data = None
    content = plistlib.dumps(data, fmt=plistlib.FMT_BINARY)
    if sign:
        content = sign_shortcut(content)
    return content


def shortcut_input(
    types: list[ContentItemClass],
    *,
    sources: list[WorkflowType] = ALL_WORKFLOW_TYPES,
    or_else: ContentItemClass | None = None,
    multiple: bool = False,
) -> Variable:
    assert shortcut_data
    if shortcut_data['input'] is not None:
        raise RuntimeError('Shortcut input already set')
    or_else = {ContentItemClass.Image: ContentItemClass.PhotoMedia, None: None}.get(
        or_else, or_else
    )
    shortcut_data['input'] = {
        'types': types,
        'or_else': or_else,
        'sources': sources,
        'multiple': multiple,
    }
    return Variable('ExtensionInput')
