from typing import TYPE_CHECKING, Any, Self, cast, overload

if TYPE_CHECKING:
    from shortcuts_py.variable import Variable

__all__ = ['TemplateStr', 't']


class TemplateStr:
    __slots__ = ('parts',)

    parts: list['str | Variable']

    @overload
    def __new__(cls, /, obj: Self) -> Self: ...
    @overload
    def __new__(cls, /, *parts: 'str | Variable') -> Self: ...
    def __new__(cls, /, *parts) -> Self:
        if len(parts) == 1 and isinstance(parts[0], TemplateStr):
            return cast(Self, parts[0])
        obj = super().__new__(cls)
        obj.parts = list(parts)
        return obj

    def __hash__(self):
        return hash(tuple(self.parts))

    def dump(self) -> dict[str, Any]:
        text = ''
        attachments = {}
        for part in self.parts:
            if isinstance(part, str):
                text += part
            else:
                attachments[f'{{{len(text)}, 1}}'] = part.dump()
                text += '\ufffc'
        return {
            'Value': {'string': text, 'attachmentsByRange': attachments},
            'WFSerializationType': 'WFTextTokenString',
        }


def t(*parts: 'str | Variable'):
    return TemplateStr(*parts)
