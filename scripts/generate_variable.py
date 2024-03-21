import yaml

with open('scripts/variables.yaml') as f:
    DATA = yaml.safe_load(f)

type_cls = {}

for cls, data in DATA['variables'].items():
    type_cls[data['type']] = cls

contents = '''\
# This file is generated by scripts/generate_variable.py. DO NOT MODIFY!

import copy
from enum import StrEnum
from typing import Any, ClassVar, Literal, overload

from shortcuts_py.condition import Condition
from shortcuts_py.consts import Number, Text
from shortcuts_py.templ import TemplateStr
from shortcuts_py.utils import parse_attachment

__all__ = ['ContentItemClass', 'coerce']


class ContentItemClass(StrEnum):
'''

for name, value in DATA['classes'].items():
    contents += f"    {name} = '{value}'\n"

contents += '\n'

for type, cls in type_cls.items():
    contents += f'''\
    @overload
    def __call__(self: 'Literal[ContentItemClass.{type}]', variable: 'Variable') -> '{cls}': ...
'''

contents += '''\
    @overload
    def __call__(self, variable: 'Variable') -> 'Variable': ...
    def __call__(self, variable):
        return coerce(variable, self)


class Variable:
    __shortcuts_is_variable__: ClassVar[Literal[True]] = True

    def __init__(
        self,
        type: str,
        aggrandizements: list[dict[str, Any]] | None = None,
        /,
        **properties: Any,
    ) -> None:
        self.type = type
        self.properties = properties
        self.aggrandizements = aggrandizements or []

    @classmethod
    def of(cls, variable: 'Variable'):
        return cls(variable.type, variable.aggrandizements, **variable.properties)

    def __hash__(self) -> int:
        return hash(
            (self.type, tuple(self.aggrandizements), frozenset(self.properties.items()))
        )

    @property
    def coercion_type(self) -> ContentItemClass | None:
        for agg in self.aggrandizements:
            if agg['Type'] == 'WFCoercionVariableAggrandizement':
                return ContentItemClass(agg['CoercionItemClass'])

    def aggrandize(self, *aggrandizements: dict[str, Any]) -> 'Variable':
        new_agg = copy.deepcopy(self.aggrandizements)
        for agg in aggrandizements:
            for old_agg in new_agg:
                if old_agg['Type'] == agg['Type']:
                    old_agg.update(agg)
                    break
            else:
                new_agg.append(agg)
        return self.__class__(self.type, new_agg, **self.properties)

    def dump(self) -> dict[str, Any]:
        data = {'Type': self.type, **self.properties}
        if self.aggrandizements:
            data['Aggrandizements'] = self.aggrandizements
        return data

    def __getitem__(self, property: str) -> 'Variable':
        return self.aggrandize(
            {'Type': 'WFPropertyVariableAggrandizement', 'PropertyName': property}
        )

    @property
    def has_value(self) -> Condition:
        return Condition(self, 100)

    @property
    def has_no_value(self) -> Condition:
        return Condition(self, 101)


'''

for cls, data in DATA['variables'].items():
    contents += f'''\
class {cls}(Variable):
'''
    if not any([data.get('getitem'), data.get('conditions')]):
        contents += '    pass\n\n'
        continue
    if data.get('getitem'):
        getitem = data['getitem']
        key = getitem['key']
        aggrandizement = getitem['aggrandizement']
        property = getitem['property']
        returns = getitem['returns']
        contents += f'''\
    def __getitem__(self, key: '{key}') -> '{returns}':
        return self.aggrandize(
            {{'Type': '{aggrandizement}', '{property}': key}}
        )

'''
    for condition, condata in data.get('conditions', {}).items():
        type = condata['type']
        params = condata['params']
        defstr = ''
        condparams = ''
        for param in params:
            defstr += f', {param["name"]}: {param["type"]}'
            valtmpl = {
                'Text': 'TemplateStr({n})',
                'Number': 'parse_attachment({n})',
            }.get(param['type'], '{n}')
            valstr = valtmpl.format(n=param['name'])
            condparams += f', {param["parameter"]}={valstr}'
        contents += f'''\
    def {condition}(self{defstr}) -> Condition:
        return Condition(self, {type}{condparams})

'''
    contents += '\n'

for type, cls in type_cls.items():
    contents += f'''\
@overload
def coerce(variable: Variable, type: Literal[ContentItemClass.{type}]) -> {cls}: ...
'''

contents += '''\
@overload
def coerce(variable: Variable, type: ContentItemClass) -> Variable: ...
def coerce(variable, type):
'''

if type_cls:
    contents += '    new_cls = {'
    for type, cls in type_cls.items():
        contents += f'ContentItemClass.{type}: {cls}, '
    contents = (
        contents[:-2]
        + '''}.get(type)
    if new_cls is not None:
        variable = new_cls.of(variable)
'''
    )

contents += '''\
    return variable.aggrandize(
        {'Type': 'WFCoercionVariableAggrandizement', 'CoercionItemClass': type.value}
    )
'''

print(contents)

if input('Generate shortcuts_py/variable.py? (Y/n) ') in 'yY':
    with open('shortcuts_py/variable.py', 'w') as f:
        f.write(contents)
else:
    exit()


# item_classes.py

contents = '''
# This file is generated by scripts/generate_variable.py. DO NOT MODIFY!

from shortcuts_py.variable import ContentItemClass

__all__ = [
'''

for name in DATA['classes']:
    contents += f"    '{name}',\n"

contents += ']\n\n'

for name in DATA['classes']:
    contents += f"{name} = ContentItemClass.{name}\n"

print('-------------------------')
print(contents)

if input('Generate shortcuts_py/item_classes.py? (Y/n) ') in 'yY':
    with open('shortcuts_py/item_classes.py', 'w') as f:
        f.write(contents)
else:
    exit()
