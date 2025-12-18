from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup

# from markdown import markdown
import markdown
from pydantic import BaseModel

from trame.config import MD_EXTENSIONS, ENCODING, BS4_HTML_PARSER

from trame.piece import Piece


class Trame(BaseModel):
    path: Optional[Path]
    markdown_content: str
    html_content: str
    pieces: list[Piece]
    origin: str
    metadata: dict = {}
    # base_url: str

    @classmethod
    def from_file(self, path: Optional[Path]):
        return TrameBuilder.from_file(path)


class TrameBuilder:
    md = markdown.Markdown(extensions=MD_EXTENSIONS)

    @classmethod
    def from_string(cls, origin: str, markdown_content: str) -> Trame:
        # NOTE: Depending on which options and/or extensions are being used, the parser may need its state reset between each call to convert.
        # See: https://python-markdown.github.io/reference/#the-details
        cls.md.reset()
        # NOTE mad: looks like it is the case when we use Meta.
        # We just reinstantiate instead of using reset
        html_content = cls.md.convert(markdown_content)
        soup = BeautifulSoup(html_content, features=BS4_HTML_PARSER)
        pieces = []
        for element in soup.children:
            # print(element) # XXX: uncomment to debug
            piece = Piece.build_from_bs4_element(element)
            # Only for EmptyNavigableString and NoTagName
            if piece is not None:
                pieces.append(piece)
        return Trame(
            path=None,
            markdown_content=markdown_content,
            html_content=html_content,
            pieces=pieces,
            origin=origin,
            metadata=cls.md.Meta,
        )

    @classmethod
    def from_file(cls, path: Path, encoding=ENCODING) -> "Trame":
        with open(path, encoding=encoding) as f:
            md_content = f.read()

        trame = cls.from_string(origin=str(path), markdown_content=md_content)
        # Override path field to store the actual Path object
        trame.path = path
        return trame
