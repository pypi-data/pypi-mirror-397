from trame import TrameBuilder
from trame.piece import Paragraph, Div, Title
from trame_tests import TrameTestCase


class TestFootnoteParsing(TrameTestCase):
    """Test suite for markdown footnote parsing"""

    def test_footnote_extension_loaded(self):
        """Test that footnotes extension generates expected HTML structure"""
        md = """Test[^1].

[^1]: Note.
"""
        trame = TrameBuilder.from_string("test", md)

        self.assertEqual(trame.html_content.count("fnref"), 2)

    def test_simple_footnote_pieces_count(self):
        """Test piece count with simple footnote"""
        md = """# Test Document

This is a paragraph with a footnote[^1].

[^1]: This is the footnote content.
"""
        trame = TrameBuilder.from_string("test", md)

        self.assertEqual(len(trame.pieces), 3)

    def test_simple_footnote_pieces_types(self):
        """Test piece types with simple footnote"""
        md = """# Test Document

This is a paragraph with a footnote[^1].

[^1]: This is the footnote content.
"""
        trame = TrameBuilder.from_string("test", md)

        self.assertIsInstance(trame.pieces[0], Title)
        self.assertIsInstance(trame.pieces[1], Paragraph)
        self.assertIsInstance(trame.pieces[2], Div)

    def test_paragraph_with_footnote_is_paragraph(self):
        """Test that paragraph with footnote reference is still Paragraph type"""
        md = """This has a footnote[^1].

[^1]: Footnote text.
"""
        trame = TrameBuilder.from_string("test", md)

        self.assertIsInstance(trame.pieces[0], Paragraph)

    def test_footnote_div_has_footnote_class(self):
        """Test that footnote div has 'footnote' class"""
        md = """Text[^1].

[^1]: Note.
"""
        trame = TrameBuilder.from_string("test", md)

        footnote_div = trame.pieces[1]
        self.assertEqual(footnote_div.page_element_bs4.get("class"), ["footnote"])

    def test_footnote_div_tag_name(self):
        """Test that footnote definitions use div tag"""
        md = """Text[^1].

[^1]: Note.
"""
        trame = TrameBuilder.from_string("test", md)

        footnote_div = trame.pieces[1]
        self.assertEqual(footnote_div.page_element_tag, "div")

    def test_multiple_footnotes_pieces_count(self):
        """Test piece count with multiple footnotes"""
        md = """Text with first[^1] and second[^2] footnotes.

[^1]: First footnote.
[^2]: Second footnote.
"""
        trame = TrameBuilder.from_string("test", md)

        self.assertEqual(len(trame.pieces), 2)

    def test_multiple_footnotes_pieces_types(self):
        """Test piece types with multiple footnotes"""
        md = """Text with first[^1] and second[^2] footnotes.

[^1]: First footnote.
[^2]: Second footnote.
"""
        trame = TrameBuilder.from_string("test", md)

        self.assertIsInstance(trame.pieces[0], Paragraph)
        self.assertIsInstance(trame.pieces[1], Div)

    def test_multiple_footnotes_sup_count(self):
        """Test that multiple footnotes generate exactly two sup tags"""
        md = """Text with first[^1] and second[^2] footnotes.

[^1]: First footnote.
[^2]: Second footnote.
"""
        trame = TrameBuilder.from_string("test", md)

        paragraph = trame.pieces[0]
        self.assertEqual(paragraph.page_element_string.count("<sup"), 2)

    def test_complex_footnote_pieces_count(self):
        """Test piece count with complex footnote content"""
        md = """Text with complex footnote[^complex].

[^complex]: This footnote has multiple elements.

    It has multiple paragraphs.
    
    - And a list
    - With items
"""
        trame = TrameBuilder.from_string("test", md)

        self.assertEqual(len(trame.pieces), 2)

    def test_complex_footnote_contains_list(self):
        """Test that complex footnote preserves list structure with two items"""
        md = """Text with complex footnote[^complex].

[^complex]: This footnote has multiple elements.

    - And a list
    - With items
"""
        trame = TrameBuilder.from_string("test", md)

        footnote_div = trame.pieces[1]
        self.assertEqual(footnote_div.page_element_string.count("<li>"), 2)

    def test_footnote_with_title_pieces_count(self):
        """Test piece count with title and footnote"""
        md = """# Title

Paragraph with footnote[^1].

[^1]: Note.
"""
        trame = TrameBuilder.from_string("test", md)

        self.assertEqual(len(trame.pieces), 3)

    def test_footnote_is_last_piece(self):
        """Test that footnote div is always last piece"""
        md = """# Title

First paragraph[^1].

Second paragraph.

[^1]: Footnote content.
"""
        trame = TrameBuilder.from_string("test", md)

        self.assertIsInstance(trame.pieces[-1], Div)
        self.assertEqual(trame.pieces[-1].page_element_bs4.get("class"), ["footnote"])

    def test_footnote_reference_in_paragraph_html(self):
        """Test that footnote reference appears exactly once in paragraph HTML"""
        md = """Text[^1].

[^1]: Note.
"""
        trame = TrameBuilder.from_string("test", md)

        paragraph = trame.pieces[0]
        self.assertEqual(paragraph.page_element_string.count("fnref"), 1)

    def test_footnote_id_in_div(self):
        """Test that footnote definition has exactly one ID"""
        md = """Text[^1].

[^1]: Note.
"""
        trame = TrameBuilder.from_string("test", md)

        footnote_div = trame.pieces[1]
        self.assertEqual(footnote_div.page_element_string.count('id="fn'), 1)

    def test_multiple_paragraphs_with_footnotes(self):
        """Test multiple paragraphs each with footnotes"""
        md = """First paragraph[^1].

Second paragraph[^2].

[^1]: First note.
[^2]: Second note.
"""
        trame = TrameBuilder.from_string("test", md)

        self.assertEqual(len(trame.pieces), 3)
        self.assertIsInstance(trame.pieces[0], Paragraph)
        self.assertIsInstance(trame.pieces[1], Paragraph)
        self.assertIsInstance(trame.pieces[2], Div)

    def test_footnote_with_code_in_definition(self):
        """Test footnote containing inline code"""
        md = """Text[^1].

[^1]: Note with `code`.
"""
        trame = TrameBuilder.from_string("test", md)

        footnote_div = trame.pieces[1]
        self.assertEqual(footnote_div.page_element_string.count("<code>"), 1)

    def test_footnote_div_contains_ol(self):
        """Test that footnote div contains an ordered list"""
        md = """Text[^1].

[^1]: Note.
"""
        trame = TrameBuilder.from_string("test", md)

        footnote_div = trame.pieces[1]
        self.assertEqual(footnote_div.page_element_string.count("<ol>"), 1)

    def test_single_footnote_one_li_in_div(self):
        """Test that single footnote creates exactly one list item"""
        md = """Text[^1].

[^1]: Note.
"""
        trame = TrameBuilder.from_string("test", md)

        footnote_div = trame.pieces[1]
        self.assertEqual(footnote_div.page_element_string.count("<li"), 1)

    def test_two_footnotes_two_li_in_div(self):
        """Test that two footnotes create exactly two list items"""
        md = """Text[^1] and more[^2].

[^1]: First.
[^2]: Second.
"""
        trame = TrameBuilder.from_string("test", md)

        footnote_div = trame.pieces[1]
        self.assertEqual(footnote_div.page_element_string.count("<li"), 2)
