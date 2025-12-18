import logging
import re
from tempfile import SpooledTemporaryFile
from typing import List, Type, cast

import mammoth
from bs4 import BeautifulSoup
from filetype import filetype
from markdownify import MarkdownConverter
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.converter import ConverterParameters, ConverterBase
from pymultirole_plugins.v1.schema import Document, AltText
from starlette.datastructures import UploadFile

logger = logging.getLogger("pymultirole")


class PyWordParameters(ConverterParameters):
    segment: bool = Field(
        False,
        extra="internal"
    )
    level_to_split_on: int = Field(
        -1,
        extra="internal"
    )
    include_image_base64_as_links: bool = Field(
        False, extra="advanced",
        description="""To include the image data as base64 links `![img-0.jpeg](data:image/jpeg;base64,`"""
    )
    include_image_base64_as_altTexts: bool = Field(
        False, extra="advanced",
        description="""To include the image data as base64 altTexts"""
    )


class PyWordConverter(ConverterBase):
    """Convert DOCX to Markdown using [mammoth](https://github.com/mwilliamson/python-mammoth)
    """

    def convert(self, source: UploadFile, parameters: ConverterParameters) \
            -> List[Document]:
        params: PyWordParameters = cast(PyWordParameters, parameters)
        doc: Document = None
        md = CustomMarkdownConverter(heading_style='atx', sup_symbol=" ", **params.dict())
        try:
            input_file = source.file._file if isinstance(source.file, SpooledTemporaryFile) else source.file
            result = mammoth.convert_to_html(input_file)
            html = auto_table_headers(result.value)
            text = md.convert(html)
            altTexts = []
            if params.include_image_base64_as_altTexts and md.images:
                for m_id, m_src in md.images.items():
                    m_mime, m_url = m_src
                    altTexts.append(AltText(name=m_id, text=m_url, properties={'mime-type': m_mime}))
            doc = Document(identifier=source.filename, text=text, altTexts=altTexts,
                           metadata={'original': source.filename, 'mime-type': 'text/markdown'})
        except BaseException:
            logger.warning(
                f"Cannot convert DOCX from file {source.filename}: ignoring",
                exc_info=True,
            )
        return [doc]

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return PyWordParameters


class CustomMarkdownConverter(MarkdownConverter):
    """
    Create a custom MarkdownConverter that adds two newlines after an image
    """

    def __init__(self, **options):
        self.ignore_pagenum = options.pop("ignore_pagenum", True)
        self.include_image_base64_as_links = options.pop("include_image_base64_as_links", False)
        self.include_image_base64_as_altTexts = options.pop("include_image_base64_as_altTexts", False)
        self.images = {}
        self.image_id = 0
        super().__init__(**options)

    def convert_pagenum(self, el, text, convert_as_inline):
        return f"\n\npage {text}\n\n" if self.ignore_pagenum else ""

    def convert_img(self, el, text, parent_tags):
        img_regex = r"data:(image/[^;]+);base64"
        img_src = el.attrs.get('src', None)
        if img_src is not None:
            matches = re.search(img_regex, img_src[0:30])
            if matches:
                mime = matches.group(1)
                kind = filetype.get_type(mime)
                if kind is not None:
                    img_id = f"img-{self.image_id}.{kind.extension}"
                    self.image_id += 1
                    if self.include_image_base64_as_altTexts:
                        self.images[img_id] = (kind.mime, img_src)
                    if self.include_image_base64_as_links:
                        return f"![{img_id}]({img_src})"
                    else:
                        return f"![{img_id}]({img_id})"
        alt = el.attrs.get('alt', None) or ''
        return f"[{alt}]" if alt else ""


def auto_table_headers(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        first_row = table.find("tr")
        if first_row:
            for cell in first_row.find_all("td", recursive=False):
                cell.name = "th"
    return str(soup)

# def lint_markdown(md: str) -> str:
#     # Optionnel – simulate basic Markdown fixes (e.g., trailing spaces, consistent bullets)
#     lines = md.strip().split('\n')
#     cleaned = []
#     for line in lines:
#         line = re.sub(r'[ \t]+$', '', line)  # Trim trailing spaces
#         if line.startswith('* '):
#             line = '- ' + line[2:]
#         cleaned.append(line)
#     return '\n'.join(cleaned).strip()
