from bs4 import BeautifulSoup

from trame.piece import Piece, BlockQuote, Paragraph
from trame import TrameBuilder
from trame_tests import TrameTestCase


class TestBlockQuoteDetection(TrameTestCase):
    """Test suite for BlockQuote detection and parsing"""

    def test_html_to_blockquote(self):
        """Test that blockquote tags are detected as BlockQuote"""
        html = "<blockquote><p>Quoted text</p></blockquote>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("blockquote")
        blockquote = Piece.build_from_bs4_element(element)
        self.assertIsInstance(blockquote, BlockQuote)

    def test_html_to_blockquote_with_multiple_paragraphs(self):
        """Test blockquote with multiple paragraphs"""
        html = "<blockquote><p>First paragraph</p><p>Second paragraph</p></blockquote>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("blockquote")
        blockquote = Piece.build_from_bs4_element(element)
        self.assertIsInstance(blockquote, BlockQuote)

    def test_html_to_empty_blockquote(self):
        """Test empty blockquote"""
        html = "<blockquote></blockquote>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("blockquote")
        blockquote = Piece.build_from_bs4_element(element)
        self.assertIsInstance(blockquote, BlockQuote)

    def test_html_to_blockquote_with_nested_elements(self):
        """Test blockquote with nested elements like em, strong, code"""
        html = "<blockquote><p>Text with <em>emphasis</em> and <strong>bold</strong> and <code>code</code></p></blockquote>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("blockquote")
        blockquote = Piece.build_from_bs4_element(element)
        self.assertIsInstance(blockquote, BlockQuote)

    def test_markdown_to_blockquote(self):
        """Test that markdown blockquotes are detected as BlockQuote"""
        md = """# Some title

> This is a quote
"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[1]
        self.assertIsInstance(blockquote, BlockQuote)

    def test_markdown_to_blockquote_multiline(self):
        """Test multiline blockquote"""
        md = """# Some title

> First line
> Second line
> Third line
"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[1]
        self.assertIsInstance(blockquote, BlockQuote)

    def test_markdown_to_blockquote_without_continuation(self):
        """Test blockquote with lazy continuation"""
        md = """# Some title

> First line
Second line
Third line
"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[1]
        self.assertIsInstance(blockquote, BlockQuote)

    def test_markdown_multiple_blockquotes(self):
        """Test multiple blockquotes in markdown"""
        md = """# Document

> First quote

Some text between quotes.

> Second quote
"""
        trame = TrameBuilder.from_string("test", md)
        blockquotes = [piece for piece in trame.pieces if isinstance(piece, BlockQuote)]
        self.assertEqual(len(blockquotes), 2)

    def test_markdown_nested_blockquote(self):
        """Test nested blockquote"""
        md = """# Document

> First level
>> Second level
>>> Third level
"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[1]
        self.assertIsInstance(blockquote, BlockQuote)

    def test_markdown_blockquote_with_inline_formatting(self):
        """Test blockquote with inline formatting"""
        md = """# Document

> This has **bold** and *italic* and `code`
"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[1]
        self.assertIsInstance(blockquote, BlockQuote)
        self.assertIn("<strong>", blockquote.page_element_string)
        self.assertIn("<em>", blockquote.page_element_string)
        self.assertIn("<code>", blockquote.page_element_string)

    def test_markdown_blockquote_with_math(self):
        """Test blockquote with math notation"""
        md = """# Document

> The formula is $x = y + 2$
"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[1]
        self.assertIsInstance(blockquote, BlockQuote)

    def test_markdown_blockquote_with_list(self):
        """Test blockquote containing a list"""
        md = """# Document

> Some text:
> - Item 1
> - Item 2
> - Item 3
"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[1]
        self.assertIsInstance(blockquote, BlockQuote)
        self.assertIn("<ul>", blockquote.page_element_string)

    def test_markdown_blockquote_with_code_block(self):
        """Test blockquote containing a code block"""
        md = """# Document

> Example code:
> ```python
> print("hello")
> ```
"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[1]
        self.assertIsInstance(blockquote, BlockQuote)
        self.assertIn("<pre>", blockquote.page_element_string)

    def test_blockquote_tag_name(self):
        """Test that blockquote uses blockquote tag"""
        md = """> Quote"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[0]
        self.assertEqual(blockquote.page_element_tag, "blockquote")

    def test_blockquote_contains_paragraph(self):
        """Test that blockquote contains paragraph tags"""
        md = """> Quote text"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[0]
        self.assertIn("<p>", blockquote.page_element_string)

    def test_blockquote_with_multiple_paragraphs_count(self):
        """Test blockquote with multiple paragraphs creates multiple p tags"""
        md = """> First paragraph
>
> Second paragraph"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[0]
        self.assertEqual(blockquote.page_element_string.count("<p>"), 2)

    def test_document_with_mixed_content(self):
        """Test document with blockquotes mixed with other elements"""
        md = """# Title

Regular paragraph.

> Quote paragraph.

Another regular paragraph.
"""
        trame = TrameBuilder.from_string("test", md)
        self.assertEqual(len(trame.pieces), 4)
        self.assertIsInstance(trame.pieces[1], Paragraph)
        self.assertIsInstance(trame.pieces[2], BlockQuote)
        self.assertIsInstance(trame.pieces[3], Paragraph)

    def test_blockquote_with_citation(self):
        """Test blockquote with citation-like text"""
        md = """> This is a quote.
> — Author Name"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[0]
        self.assertIsInstance(blockquote, BlockQuote)

    def test_blockquote_with_link(self):
        """Test blockquote containing a link"""
        md = """> Read more at [example](https://example.com)"""
        trame = TrameBuilder.from_string("test", md)
        blockquote = trame.pieces[0]
        self.assertIsInstance(blockquote, BlockQuote)
        self.assertIn("<a ", blockquote.page_element_string)

    def test_html_blockquote_with_cite_attribute(self):
        """Test HTML blockquote with cite attribute"""
        html = '<blockquote cite="https://example.com"><p>Quote</p></blockquote>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("blockquote")
        blockquote = Piece.build_from_bs4_element(element)
        self.assertIsInstance(blockquote, BlockQuote)
