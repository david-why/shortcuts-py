from typing import Any, Literal, overload

from shortcuts_py.consts import Number
from shortcuts_py.shortcuts import Action
from shortcuts_py.utils import parse_attachment
from shortcuts_py.variable import Variable

__all__ = ['resize_image', 'convert_image', 'get_image_detail']


@overload
def resize_image(
    image: Variable, *, width: Number, height: Number | None = None
) -> Variable: ...
@overload
def resize_image(
    image: Variable, *, width: Number | None = None, height: Number
) -> Variable: ...
@overload
def resize_image(image: Variable, *, longest_edge: Number) -> Variable: ...
@overload
def resize_image(image: Variable, *, percentage: Number) -> Variable: ...
def resize_image(
    image: Variable, width=None, height=None, longest_edge=None, percentage=None
) -> Variable:
    params: dict[str, Any] = {'WFImage': parse_attachment(image)}
    if width is not None or height is not None:
        if width is None:
            width = ''
        if height is None:
            height = ''
        params['WFImageResizeWidth'] = parse_attachment(width)
        params['WFImageResizeHeight'] = parse_attachment(height)
    elif longest_edge is not None:
        params['WFImageResizeKey'] = 'Longest Edge'
        params['WFImageResizeLength'] = parse_attachment(longest_edge)
    elif percentage is not None:
        params['WFImageResizeKey'] = 'Percentage'
        params['WFImageResizePercentage'] = parse_attachment(percentage)
    action = Action('is.workflow.actions.image.resize', params)
    return action.output('Resized Image')


def convert_image(
    image: Variable, format: Literal['JPEG', 'PNG', 'TIFF', 'GIF', 'BMP', 'PDF', 'HEIF']
) -> Variable:
    params = {'WFInput': parse_attachment(image), 'WFImageFormat': format}
    action = Action('is.workflow.actions.image.convert', params)
    return action.output('Converted Image')


def get_image_detail(image: Variable, property: str):
    params = {'WFInput': parse_attachment(image), 'WFContentItemPropertyName': property}
    action = Action('is.workflow.actions.properties.images', params)
    return action.output(property)
