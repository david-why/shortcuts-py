from typing import Literal

from shortcuts_py.consts import Number
from shortcuts_py.shortcuts import Action
from shortcuts_py.utils import parse_attachment

__all__ = ['start_timer']


def start_timer(number: Number, unit: Literal['sec', 'min', 'hr'] = 'min') -> None:
    Action(
        'is.workflow.actions.timer.start',
        {
            'WFDuration': {
                'Value': {'Unit': unit, 'Magnitude': parse_attachment(number)}
            }
        },
    )
