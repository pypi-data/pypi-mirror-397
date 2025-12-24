from pathlib import Path
from typing import Optional
import hashlib

from bs4 import BeautifulSoup

# from markdown import markdown
import markdown
from pydantic import BaseModel, computed_field

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

    @computed_field
    @property
    def md_content_hash(self) -> str:
        """Compute SHA-256 hash of markdown content"""
        # NOTE ⚠️ The frontmatter is taken into account in the hash
        # Normalize line endings for cross-platform consistency
        content = self.markdown_content.replace("\r\n", "\n").replace("\r", "\n")
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


class TrameBuilder:
    md = markdown.Markdown(extensions=MD_EXTENSIONS)

    @classmethod
    def from_string(cls, origin: str, markdown_content: str) -> Trame:
        # NOTE: Depending on which options and/or extensions are being used, the parser may need its state reset between each call to convert.
        # See: https://python-markdown.github.io/reference/#the-details
        cls.md.reset()
        # NOTE: looks like it is the case when we use Meta.
        # We just reinstantiate instead of using reset
        html_content = cls.md.convert(markdown_content)
        soup = BeautifulSoup(html_content, features=BS4_HTML_PARSER)
        pieces = []
        for element in soup.children:
            # print(element) # XXX: uncomment to debug
            piece = Piece.build_from_bs4_element(element)
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
