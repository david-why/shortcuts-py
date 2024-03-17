from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from shortcuts_py.variable import Variable

__all__ = ['Condition']


class Condition:
    def __init__(self, input: 'Variable', condition: int, **parameters: Any) -> None:
        self.input = input
        self.condition = condition
        self.parameters = parameters

    def dump(self) -> dict[str, Any]:
        return {
            'WFInput': {
                'Type': 'Variable',
                'Variable': {
                    'Value': self.input.dump(),
                    'WFSerializationType': 'WFTextTokenAttachment',
                },
            },
            'WFCondition': self.condition,
            **self.parameters,
        }
