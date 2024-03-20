from typing import Any

import requests

from shortcuts_py.consts import Text
from shortcuts_py.data import shortcut_data
from shortcuts_py.templ import TemplateStr

__all__ = ['sign_shortcut']


def sign_shortcut(data: bytes) -> bytes:
    # credit to ActuallyTaylor on GitHub
    # https://github.com/ActuallyTaylor/Open-Jellycuts/blob/fe68218/Jellycuts/Helpers/Signing/ShortcutsSigner.swift#L69
    r = requests.post(
        'https://actuallyhome.herokuapp.com/API/routing/request',
        files={'upload': ('example.shortcut', data)},
    )
    r.raise_for_status()
    return r.content


def download_shortcut(url: str, signed: bool = False) -> bytes:
    if not url.startswith('https'):
        shortcut_id = url
    else:
        shortcut_id = url.split('/')[-1]
    data = requests.get(
        f'https://www.icloud.com/shortcuts/api/records/{shortcut_id}'
    ).json()
    shortcut_url = data['fields']['signedShortcut' if signed else 'shortcut']['value'][
        'downloadURL'
    ]
    return requests.get(shortcut_url).content


def pop_stack() -> None:
    assert shortcut_data['started']
    while shortcut_data['stack']:
        entry = shortcut_data['stack'][-1]
        if entry.get('no_finish') is None or entry['no_finish']:
            return
        entry['no_finish'] = True
        entry['finish']()
        shortcut_data['stack'].pop()


def parse_dict_list(data: list[Any]) -> dict[str, Any]:
    from shortcuts_py.variable import ContentItemClass  # prevent circular import

    value = []
    for item in data:
        if isinstance(item, str):
            value.append(item)
        elif isinstance(item, TemplateStr):
            value.append({'WFItemType': 0, 'WFValue': item.dump()})
        elif isinstance(item, bool):
            value.append(
                {
                    'WFItemType': 4,
                    'WFValue': {
                        'Value': item,
                        'WFSerializationType': 'WFNumberSubstitutableState',
                    },
                }
            )
        elif isinstance(item, (int, float)):
            value.append(
                {
                    'WFItemType': 3,
                    'WFValue': {
                        'Value': {'string': str(item)},
                        'WFSerializationType': 'WFTextTokenString',
                    },
                }
            )
        elif isinstance(item, list):
            value.append({'WFItemType': 2, 'WFValue': parse_dict_list(item)})
        elif isinstance(item, dict):
            value.append(
                {
                    'WFItemType': 1,
                    'WFValue': {
                        'Value': parse_dict(item),
                        'WFSerializationType': 'WFDictionaryFieldValue',
                    },
                }
            )
        elif getattr(item, '__shortcuts_is_variable__', False):
            if item.coercion_type is None:
                raise ValueError('List items must have a coercion type')
            if item.coercion_type is ContentItemClass.Text:
                type = 0
                v = TemplateStr(item).dump()
            elif item.coercion_type is ContentItemClass.Number:
                type = 3
                v = TemplateStr(ContentItemClass.Text(item)).dump()
            elif item.coercion_type is ContentItemClass.File:
                type = 5
                v = {
                    'Value': item.dump(),
                    'WFSerializationType': 'WFTextTokenAttachment',
                }
            else:
                raise ValueError('Unsupported variable type in list item')
            value.append({'WFItemType': type, 'WFValue': v})
    return {'Value': value, 'WFSerializationType': 'WFArrayParameterState'}


def parse_dict(data: dict[Text, Any]) -> dict[str, Any]:
    from shortcuts_py.variable import ContentItemClass  # prevent circular import

    items = []
    for k, v in data.items():
        k = TemplateStr(k)
        if isinstance(v, str):
            type = 0
            value = {'Value': {'string': v}, 'WFSerializationType': 'WFTextTokenString'}
        elif isinstance(v, bool):
            type = 4
            value = {'Value': v, 'WFSerializationType': 'WFNumberSubstitutableState'}
        elif isinstance(v, (int, float)):
            type = 3
            value = {
                'Value': {'string': str(v)},
                'WFSerializationType': 'WFTextTokenString',
            }
        elif isinstance(v, list):
            type = 2
            value = parse_dict_list(v)
        elif isinstance(v, dict):
            type = 1
            value = {
                'Value': parse_dict(v),
                'WFSerializationType': 'WFDictionaryFieldValue',
            }
        elif getattr(v, '__shortcuts_is_variable__', False):
            if v.coercion_type is None:
                raise ValueError('Dictionary values must have a coercion type')
            if v.coercion_type is ContentItemClass.Text:
                type = 0
                value = TemplateStr(v).dump()
            elif v.coercion_type is ContentItemClass.Number:
                type = 3
                value = TemplateStr(ContentItemClass.Text(v)).dump()
            elif v.coercion_type is ContentItemClass.File:
                type = 5
                value = {
                    'Value': v.dump(),
                    'WFSerializationType': 'WFTextTokenAttachment',
                }
            else:
                raise ValueError('Unsupported variable type in dictionary value')
        items.append({'WFKey': k.dump(), 'WFItemType': type, 'WFValue': value})
    return {
        'Value': {'WFDictionaryFieldValueItems': items},
        'WFSerializationType': 'WFDictionaryFieldValue',
    }


def parse_attachment(value: Any) -> str | dict[str, Any]:
    if isinstance(value, (str, int, float)):
        return str(value)
    if getattr(value, '__shortcuts_is_variable__', False):
        return {'Value': value.dump(), 'WFSerializationType': 'WFTextTokenAttachment'}
    if getattr(value, '__shortcuts_is_file__', False):
        return value.dump()
    raise ValueError('Unsupported text attachment type')
