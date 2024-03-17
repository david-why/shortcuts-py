import copy
from enum import StrEnum
from typing import Any, Literal, Self, cast, overload

__all__ = ['ContentItemClass', 't', 'coerce']


class ContentItemClass(StrEnum):
    AppStoreApp = 'WFAppStoreAppContentItem'
    Article = 'WFArticleContentItem'
    Boolean = 'WFBooleanContentItem'
    Contact = 'WFContactContentItem'
    Date = 'WFDateContentItem'
    Dictionary = 'WFDictionaryContentItem'
    EmailAddress = 'WFEmailAddressContentItem'
    EventAttendee = 'WFEKParticipantContentItem'
    File = 'WFGenericFileContentItem'
    Image = 'WFImageContentItem'
    ITunesMedia = 'WFMPMediaContentItem'
    ITunesProduct = 'WFiTunesProductContentItem'
    Location = 'WFLocationContentItem'
    MapsLink = 'WFDCMapsLinkContentItem'
    Media = 'WFAVAssetContentItem'
    Number = 'WFNumberContentItem'
    PDF = 'WFPDFContentItem'
    PhoneNumber = 'WFPhoneNumberContentItem'
    PhotoMedia = 'WFPhotoMediaContentItem'  # hidden
    Place = 'WFMKMapItemContentItem'
    RichText = 'WFRichTextContentItem'
    Text = 'WFStringContentItem'
    URL = 'WFURLContentItem'
    VCard = 'WFVCardContentItem'

    @overload
    def __call__(
        self: 'Literal[ContentItemClass.Dictionary]', variable: 'Variable'
    ) -> 'DictVariable': ...

    @overload
    def __call__(self, variable: 'Variable') -> 'Variable': ...

    def __call__(self, variable: 'Variable') -> 'Variable':
        return coerce(variable, self)


class Variable:
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
        if (
            len(aggrandizements) == 1
            and aggrandizements[0]['Type'] == 'WFCoercionVariableAggrandizement'
            and aggrandizements[0]['CoercionItemClass'] == ContentItemClass.Dictionary
            and self.__class__ is not DictVariable
        ):
            return DictVariable(
                self.type, self.aggrandizements, **self.properties
            ).aggrandize(*aggrandizements)
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


class DictVariable(Variable):
    def __getitem__(self, key: str) -> Variable:
        return self.aggrandize(
            {'Type': 'WFDictionaryValueVariableAggrandizement', 'DictionaryKey': key}
        )


class TemplateStr:
    __slots__ = ('parts',)

    parts: list[str | Variable]

    @overload
    def __new__(cls, /, obj: Self) -> Self: ...

    @overload
    def __new__(cls, /, *parts: str | Variable) -> Self: ...

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


def t(*parts: str | Variable):
    return TemplateStr(*parts)


@overload
def coerce(
    variable: Variable, type: Literal[ContentItemClass.Dictionary]
) -> DictVariable: ...


@overload
def coerce(variable: Variable, type: ContentItemClass) -> Variable: ...


def coerce(variable: Variable, type: ContentItemClass) -> Variable:
    return variable.aggrandize(
        {'Type': 'WFCoercionVariableAggrandizement', 'CoercionItemClass': type.value}
    )
