from abc import ABC
import re

from typing import Optional, OrderedDict

from bs4.element import Tag, NavigableString, PageElement, Comment

from pydantic import BaseModel, ConfigDict

import strictyaml

from trame.piece.consolidate import clean_text_nodes


class Actor(BaseModel, ABC): ...


class Piece(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    page_element_bs4: PageElement
    page_element_tag: str = None
    page_element_string: str = None
    html: str = None
    actors: Optional[list[Actor]] = None

    def model_post_init(self, context):
        # NOTE mad: this avoids decorator and caching spaghetti
        # and raises error early as we can
        super().model_post_init(context)
        # The tag name of the parsed html element
        self.page_element_tag = str(self.page_element_bs4.name)
        # The complete string of the parsed html element
        self.page_element_string = str(self.page_element_bs4)
        # Clean html we want to display
        self.html = clean_text_nodes(self.page_element_bs4)

    @classmethod
    def build_from_bs4_element(cls, element: PageElement) -> "Piece":
        return PieceBuilder.from_bs4_element(element)


#####################################################################
# EMPTY STRINGS
####################################################################


class EmptyNavigableString: ...


#####################################################################
# CONCRETE ACTORS
#####################################################################


class ListElement(Actor): ...


class YamlContent(Actor):
    yaml_str: str
    data: OrderedDict = None
    pca_nature: str = None

    def model_post_init(self, context):
        yaml = strictyaml.load(self.yaml_str)

        self.data = yaml.data
        self.pca_nature = self.data.pop("pca_nature", "pure_yaml")


#####################################################################
# CONCRETE PIECES
#####################################################################


class Paragraph(Piece): ...


class Title(Piece):
    level: int = None

    def model_post_init(self, context):
        super().model_post_init(context)
        m = re.match(r"h(?P<level>[1-5])", self.page_element_tag)
        self.level = int(m.group("level"))


class UnorderedList(Piece):
    def model_post_init(self, context):
        super().model_post_init(context)
        self.actors = list(
            ListElement(html=str(element)) for element in self.page_element_bs4.find_all("li")
        )


class Code(Piece):
    language: Optional[str] = None
    code_str: str = None
    content: Actor = None

    def model_post_init(self, context):
        super().model_post_init(context)

        code_tag = self.page_element_bs4.find("code")

        # NOTE: decode_contents for python unicode, encode for utf8 encoded bytestring
        self.code_str = code_tag.decode_contents()

        self.language = None
        classes = code_tag.get("class", [])
        if classes:
            for cls in classes:
                if isinstance(cls, str) and cls.startswith("language-"):
                    self.language = cls.replace("language-", "", 1)
                    break


class YamlCode(Code):
    def model_post_init(self, context):
        super().model_post_init(context)
        self.content = YamlContent(yaml_str=self.code_str)
        self.actors = [self.content]


class Image(Piece):
    description: str = None

    def model_post_init(self, context):
        super().model_post_init(context)
        self.description = self.page_element_bs4.get("alt", None)


class Table(Piece): ...


class HRule(Piece): ...


class Div(Piece): ...


# class EmptyParagraph(Piece): ...


# class NoTagName: ...


# NOTE : en utilisant la position on en a pas besoin
# car pas besoin de faire des groupes arbitraires
# class VGroup(Piece):
#     pieces: list[Piece]


class PieceBuilder:
    @staticmethod
    def from_bs4_element(element: PageElement) -> Piece:
        """Build a Piece from a BeautifulSoup element (FROM HTML=MARKDOWN PARSED)."""

        # Check for NavigableString first
        if isinstance(element, NavigableString):
            if isinstance(element, Comment):
                return None
            if element.strip() == "":
                return None
            else:
                raise NotImplementedError(f"Non-empty NavigableString: {element}")

        elif isinstance(element, Tag):
            return PieceBuilder.from_bs4_tag(element)

    def from_bs4_tag(tag: Tag) -> Piece:
        # Paragraph
        # NOTE: paragraph also encapsulate other stuff when parsed by markdown, such as images for instance

        if tag.name == "p":
            # Look for an image first
            sub_elements = tag.find_all()
            if len(sub_elements) == 1 and (sub_element := sub_elements[0]).name == "img":
                return Image(page_element_bs4=sub_element)

            # Else assume it is a paragraph
            text_content = tag.get_text(strip=True)
            if text_content == "":
                # return Paragraph(page_element_bs4=tag)
                None
            else:
                return Paragraph(page_element_bs4=tag)

        # Lists

        elif tag.name == "ul":
            return UnorderedList(page_element_bs4=tag)

        elif tag.name == "table":
            return Table(page_element_bs4=tag)

        # Code
        elif tag.name == "pre":
            code = Code(page_element_bs4=tag)
            if code.language == "yaml":
                return YamlCode(page_element_bs4=tag)
            return code

        # Titles
        elif re.match(r"^h[1-5]$", tag.name):
            return Title(page_element_bs4=tag)

        elif tag.name == "hr":
            return HRule(page_element_bs4=tag)

        # Arbitrary div
        elif tag.name == "div":
            return Div(page_element_bs4=tag)

        else:
            raise NotImplementedError(f"{type(tag)=} - {tag.name=} - {str(tag)=}")
