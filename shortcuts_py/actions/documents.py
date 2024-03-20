from typing import Literal

from shortcuts_py.consts import AnyFile, Text
from shortcuts_py.shortcuts import Action
from shortcuts_py.templ import TemplateStr
from shortcuts_py.utils import parse_attachment
from shortcuts_py.variable import FileVariable, PDFVariable, TextVariable, Variable

__all__ = [
    'add_pdf_to_books',
    'append_to_text_file',
    'create_folder',
    'combine_text',
    'delete_files',
    'extract_text_from_image',
    'generate_qr_code',
    'get_contents_of_folder',
    'get_file_from_folder',
    'make_html_from_rich_text',
    'make_markdown_from_rich_text',
    'make_pdf',
    'select_file',
    'select_folder',
    'text',
]

# VariableT = TypeVar('VariableT', bound=Variable)


def add_pdf_to_books(file: Variable) -> None:
    Action('com.apple.iBooks.openin', {'BooksInput': parse_attachment(file)})


def append_to_text_file(
    folder: AnyFile, path: Text, text: Text, *, make_new_line: bool = True
) -> FileVariable:
    action = Action(
        'is.workflow.actions.file.append',
        {
            'WFFile': parse_attachment(folder),
            'WFFilePath': TemplateStr(path).dump(),
            'WFInput': TemplateStr(text).dump(),
            'WFAppendOnNewLine': make_new_line,
        },
    )
    return action.output('Appended File', FileVariable)


def create_folder(parent: AnyFile, name: Text) -> FileVariable:
    action = Action(
        'is.workflow.actions.files.createfolder',
        {
            'WFFolder': parse_attachment(parent),
            'WFFilePath': TemplateStr(name).dump(),
        },
    )
    return action.output('Created Folder', FileVariable)


def combine_text(
    text: Variable,
    separator: Text | None = None,
    sep_type: Literal['New Lines', 'Spaces', 'Custom'] | None = None,
) -> TextVariable:
    if sep_type is None:
        sep_type = 'New Lines' if separator is None else 'Custom'
    params = {'WFTextSeparator': sep_type, 'text': parse_attachment(text)}
    if separator is not None:
        params['WFTextCustomSeparator'] = TemplateStr(separator).dump()
    action = Action('is.workflow.actions.text.combine', params)
    return action.output('Combined Text', TextVariable)


# TODO delete immediately
def delete_files(files: AnyFile) -> None:
    Action('is.workflow.actions.file.delete', {'WFInput': parse_attachment(files)})


def extract_text_from_image(image: Variable) -> TextVariable:
    action = Action(
        'is.workflow.actions.extracttextfromimage', {'WFImage': parse_attachment(image)}
    )
    return action.output('Text from Image', TextVariable)


def generate_qr_code(
    text: Text, correction: Literal['Low', 'Medium', 'Quartile', 'High'] = 'Medium'
) -> Variable:
    action = Action(
        'is.workflow.actions.generatebarcode',
        {'WFText': TemplateStr(text).dump(), 'WFQRErrorCorrectionLevel': correction},
    )
    return action.output('QR Code', Variable)


# TODO recursive
def get_contents_of_folder(folder: AnyFile) -> FileVariable:
    action = Action(
        'is.workflow.actions.file.getfoldercontents',
        {'WFFolder': parse_attachment(folder)},
    )
    return action.output('Contents of Folder', FileVariable)


def get_file_from_folder(
    folder: AnyFile, path: str, *, error_not_found: bool = True
) -> FileVariable:
    action = Action(
        'is.workflow.actions.documentpicker.open',
        {
            'WFFile': parse_attachment(folder),
            'WFGetFilePath': TemplateStr(path).dump(),
            'WFFileErrorIfNotFound': error_not_found,
        },
    )
    return action.output('File', FileVariable)


# TODO make_full_document
def make_html_from_rich_text(rich_text: Variable) -> TextVariable:
    action = Action(
        'is.workflow.actions.gethtmlfromrichtext',
        {'WFInput': parse_attachment(rich_text)},
    )
    return action.output('HTML from Rich Text', TextVariable)


def make_markdown_from_rich_text(rich_text: Variable) -> TextVariable:
    action = Action(
        'is.workflow.actions.getmarkdownfromrichtext',
        {'WFInput': parse_attachment(rich_text)},
    )
    return action.output('Markdown from Rich Text', TextVariable)


# TODO make_rich_text_from_{html,markdown}


# TODO margin
def make_pdf(
    input: Variable,
    *,
    margin: bool = False,
    pages: int | tuple[int, int] | None = None,
    merge: Literal['Append', 'Shuffle'] = 'Append'
) -> PDFVariable:
    params = {'WFInput': parse_attachment(input), 'WFPDFDocumentMergeBehavior': merge}
    if pages is None:
        params['WFPDFIncludedPages'] = 'All Pages'
    elif isinstance(pages, int):
        params['WFPDFIncludedPages'] = 'Single Page'
        params['WFPDFSinglePage'] = str(pages)
    else:
        params['WFPDFIncludedPages'] = 'Page Range'
        params['WFPDFPageRangeStart'] = str(pages[0])
        params['WFPDFPageRangeEnd'] = str(pages[1])
    action = Action('is.workflow.actions.makepdf', params)
    return action.output('PDF', PDFVariable)


def select_file(multiple: bool = False):
    action = Action('is.workflow.actions.file.select', {'SelectMultiple': multiple})
    return action.output('File', FileVariable)


def select_folder(multiple: bool = False):
    action = Action(
        'is.workflow.actions.file.select',
        {'SelectMultiple': multiple, 'WFPickingMode': 'Folders'},
    )
    return action.output('File', FileVariable)


def text(text: Text) -> TextVariable:
    action = Action(
        'is.workflow.actions.gettext', {'WFTextActionText': TemplateStr(text).dump()}
    )
    return action.output('Text', TextVariable)
