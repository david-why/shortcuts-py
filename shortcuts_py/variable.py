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
    App = 'WFAppContentItem'
    AppStoreApp = 'WFAppStoreAppContentItem'
    Article = 'WFArticleContentItem'
    Boolean = 'WFBooleanContentItem'
    Contact = 'WFContactContentItem'
    Date = 'WFDateContentItem'
    Dictionary = 'WFDictionaryContentItem'
    Display = 'WFDisplayContentItem'
    EmailAddress = 'WFEmailAddressContentItem'
    EventAttendee = 'WFEKParticipantContentItem'
    File = 'WFGenericFileContentItem'
    Folder = 'WFFolderContentItem'
    Image = 'WFImageContentItem'
    ITunesMedia = 'WFMPMediaContentItem'
    ITunesProduct = 'WFiTunesProductContentItem'
    Location = 'WFLocationContentItem'
    MapsLink = 'WFDCMapsLinkContentItem'
    Media = 'WFAVAssetContentItem'
    Number = 'WFNumberContentItem'
    PDF = 'WFPDFContentItem'
    PhoneNumber = 'WFPhoneNumberContentItem'
    PhotoMedia = 'WFPhotoMediaContentItem'
    Place = 'WFMKMapItemContentItem'
    RichText = 'WFRichTextContentItem'
    SafariWebPage = 'WFSafariWebPageContentItem'
    Text = 'WFStringContentItem'
    URL = 'WFURLContentItem'
    VCard = 'WFVCardContentItem'
    Window = 'WFWindowContentItem'

    @overload
    def __call__(
        self: 'Literal[ContentItemClass.Dictionary]', variable: 'Variable'
    ) -> 'DictVariable': ...
    @overload
    def __call__(
        self: 'Literal[ContentItemClass.Text]', variable: 'Variable'
    ) -> 'TextVariable': ...
    @overload
    def __call__(
        self: 'Literal[ContentItemClass.Number]', variable: 'Variable'
    ) -> 'NumberVariable': ...
    @overload
    def __call__(
        self: 'Literal[ContentItemClass.File]', variable: 'Variable'
    ) -> 'FileVariable': ...
    @overload
    def __call__(
        self: 'Literal[ContentItemClass.RichText]', variable: 'Variable'
    ) -> 'RichTextVariable': ...
    @overload
    def __call__(
        self: 'Literal[ContentItemClass.PDF]', variable: 'Variable'
    ) -> 'PDFVariable': ...
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

    def has_value(self) -> Condition:
        return Condition(self, 100)

    def has_no_value(self) -> Condition:
        return Condition(self, 101)


class DictVariable(Variable):
    def __getitem__(self, key: 'str') -> 'Variable':
        return self.aggrandize(
            {'Type': 'WFDictionaryValueVariableAggrandizement', 'DictionaryKey': key}
        )


class TextVariable(Variable):
    def __eq__(self, text: Text) -> Condition:
        return Condition(self, 4, WFConditionalActionString=TemplateStr(text))

    def __ne__(self, text: Text) -> Condition:
        return Condition(self, 5, WFConditionalActionString=TemplateStr(text))

    def __contains__(self, text: Text) -> Condition:
        return Condition(self, 99, WFConditionalActionString=TemplateStr(text))

    def does_not_contain(self, text: Text) -> Condition:
        return Condition(self, 999, WFConditionalActionString=TemplateStr(text))

    def startswith(self, text: Text) -> Condition:
        return Condition(self, 8, WFConditionalActionString=TemplateStr(text))

    def endswith(self, text: Text) -> Condition:
        return Condition(self, 9, WFConditionalActionString=TemplateStr(text))


class NumberVariable(Variable):
    def __eq__(self, value: Number) -> Condition:
        return Condition(self, 4, WFNumberValue=parse_attachment(value))

    def __ne__(self, value: Number) -> Condition:
        return Condition(self, 5, WFNumberValue=parse_attachment(value))

    def __gt__(self, value: Number) -> Condition:
        return Condition(self, 2, WFNumberValue=parse_attachment(value))

    def __ge__(self, value: Number) -> Condition:
        return Condition(self, 3, WFNumberValue=parse_attachment(value))

    def __lt__(self, value: Number) -> Condition:
        return Condition(self, 0, WFNumberValue=parse_attachment(value))

    def __le__(self, value: Number) -> Condition:
        return Condition(self, 1, WFNumberValue=parse_attachment(value))

    def is_between(self, lower: Number, upper: Number) -> Condition:
        return Condition(
            self,
            1003,
            WFNumberValue=parse_attachment(lower),
            WFAnotherNumber=parse_attachment(upper),
        )


class FileVariable(Variable):
    pass


class RichTextVariable(Variable):
    pass


class PDFVariable(Variable):
    pass


@overload
def coerce(
    variable: Variable, type: Literal[ContentItemClass.Dictionary]
) -> DictVariable: ...
@overload
def coerce(
    variable: Variable, type: Literal[ContentItemClass.Text]
) -> TextVariable: ...
@overload
def coerce(
    variable: Variable, type: Literal[ContentItemClass.Number]
) -> NumberVariable: ...
@overload
def coerce(
    variable: Variable, type: Literal[ContentItemClass.File]
) -> FileVariable: ...
@overload
def coerce(
    variable: Variable, type: Literal[ContentItemClass.RichText]
) -> RichTextVariable: ...
@overload
def coerce(variable: Variable, type: Literal[ContentItemClass.PDF]) -> PDFVariable: ...
@overload
def coerce(variable: Variable, type: ContentItemClass) -> Variable: ...
def coerce(variable, type):
    new_cls = {
        ContentItemClass.Dictionary: DictVariable,
        ContentItemClass.Text: TextVariable,
        ContentItemClass.Number: NumberVariable,
        ContentItemClass.File: FileVariable,
        ContentItemClass.RichText: RichTextVariable,
        ContentItemClass.PDF: PDFVariable,
    }.get(type)
    if new_cls is not None:
        variable = new_cls.of(variable)
    return variable.aggrandize(
        {'Type': 'WFCoercionVariableAggrandizement', 'CoercionItemClass': type.value}
    )
