import unittest

from bs4 import BeautifulSoup

from trame.piece import Piece, Title, Paragraph, UnorderedList, Code, Table, HRule, Div
from trame.piece.consolidate import clean_text_nodes


class TestPieceModelFromBs4Element(unittest.TestCase):
    """Test suite for PieceModel.from_bs4_element() method"""

    def test_title(self):
        html = "<h1>Hello</h1>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h1")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, Title)
        self.assertEqual(piece.page_element_string, html)

    def test_paragraph(self):
        html = "<p>Hello</p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, Paragraph)
        self.assertEqual(piece.page_element_string, html)

    def test_unordered_list(self):
        html = "<ul><li>Hello</li><li>World</li></ul>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("ul")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, UnorderedList)
        self.assertEqual(piece.page_element_string, html)

    def test_code(self):
        html = "<pre><code>print('Hello, World!')</code></pre>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, Code)
        self.assertEqual(piece.page_element_string, html)

    def test_table(self):
        html = "<table><tr><th>Name</th><th>Age</th></tr><tr><td>John</td><td>30</td></tr></table>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("table")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, Table)
        self.assertEqual(piece.page_element_string, html)

    def test_hrule(self):
        html = "<hr>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("hr")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, HRule)
        # BeautifulSoup serializes <hr> as <hr/>
        self.assertEqual(piece.page_element_string, "<hr/>")

    def test_div(self):
        html = "<div>Hello</div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, Div)
        self.assertEqual(piece.page_element_string, html)


class TestPieceHtmlAttribute(unittest.TestCase):
    """Test suite for Piece.html property - ensures newlines are stripped"""

    def test_paragraph_with_newlines(self):
        """Test paragraph with newlines get cleaned"""
        html = "<p>Hello\nWorld</p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, Paragraph)
        expected = "<p>Hello World</p>"
        self.assertEqual(piece.html, expected)

    def test_paragraph_with_nested_elements(self):
        """Test paragraph with nested elements preserves HTML structure"""
        html = "<p>Hello<br/>World</p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        piece = Piece.build_from_bs4_element(element)
        self.assertEqual(piece.html, "<p>Hello<br/>World</p>")

    def test_title_with_newlines(self):
        """Test title with newlines get cleaned"""
        html = "<h1>Hello\nWorld</h1>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h1")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, Title)
        expected = "<h1>Hello World</h1>"
        self.assertEqual(piece.html, expected)

    def test_code_preserves_content(self):
        """Test code blocks preserve their content"""
        html = "<pre><code>print('Hello, World!')</code></pre>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, Code)
        self.assertEqual(piece.html, "<pre><code>print('Hello, World!')</code></pre>")

    def test_table_with_newlines(self):
        """Test table content is preserved"""
        html = "<table><tr><th>Name</th><th>Age</th></tr><tr><td>John</td><td>30</td></tr></table>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("table")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, Table)
        self.assertEqual(
            piece.html,
            "<table><tr><th>Name</th><th>Age</th></tr><tr><td>John</td><td>30</td></tr></table>",
        )

    def test_hrule(self):
        """Test hrule renders correctly"""
        html = "<hr>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("hr")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, HRule)
        self.assertEqual(piece.html, "<hr/>")

    def test_multiple_newlines(self):
        """Test with multiple consecutive newlines"""
        html = "<p>Hello\n\n\nWorld\n\nHow\nAre\n\n\nYou</p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        piece = Piece.build_from_bs4_element(element)
        expected = "<p>Hello   World  How Are   You</p>"
        self.assertEqual(piece.html, expected)

    def test_triple_quoted_string_newlines(self):
        """Test with triple-quoted string (actual line breaks)"""
        html = """<div>
First line
Second line
    Third line with indentation
Fourth line
</div>"""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        piece = Piece.build_from_bs4_element(element)
        expected = "<div> First line Second line     Third line with indentation Fourth line </div>"
        self.assertEqual(piece.html, expected)

    def test_complex_mixed_newlines(self):
        """Test with complex HTML structure and mixed newlines"""
        html = """<div>
<h2>Title\nWith\nNewlines</h2>
<p>First\n\nparagraph
with lots
of\n\n\nnewlines</p>
<ul>
<li>Item\none</li>
<li>Item\n\ntwo</li>
</ul>
</div>"""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        piece = Piece.build_from_bs4_element(element)
        expected = "<div> <h2>Title With Newlines</h2> <p>First  paragraph with lots of   newlines</p> <ul> <li>Item one</li> <li>Item  two</li> </ul> </div>"
        self.assertEqual(piece.html, expected)

    def test_unordered_list_with_newlines(self):
        """Test unordered list with newlines in items"""
        html = "<ul><li>Item\nOne</li><li>Item\n\nTwo</li></ul>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("ul")
        piece = Piece.build_from_bs4_element(element)
        self.assertIsInstance(piece, UnorderedList)
        expected = "<ul><li>Item One</li><li>Item  Two</li></ul>"
        self.assertEqual(piece.html, expected)

    def test_html_caching(self):
        """Test that html property is cached (computed once)"""
        html = "<p>Hello\nWorld</p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        piece = Piece.build_from_bs4_element(element)

        # Access html twice
        html1 = piece.html
        html2 = piece.html

        # Should return same cached value
        self.assertIs(html1, html2)
        self.assertEqual(html1, "<p>Hello World</p>")


class TestCleanTextNodesWithDivs(unittest.TestCase):
    """Test suite for clean_text_nodes function with div elements and nesting"""

    def test_simple_div_with_newlines(self):
        """Test simple div with newlines in text"""
        html = "<div>Hello\nWorld</div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        result = clean_text_nodes(element)
        self.assertEqual(result, "<div>Hello World</div>")
        self.assertNotIn("\n", result)

    def test_nested_divs_with_newlines(self):
        """Test nested divs with newlines in text nodes"""
        html = "<div>Outer\nText<div>Inner\nText</div>More\nOuter</div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        result = clean_text_nodes(element)
        expected = "<div>Outer Text<div>Inner Text</div>More Outer</div>"
        self.assertEqual(result, expected)

    def test_deeply_nested_divs(self):
        """Test deeply nested divs with newlines at each level"""
        html = """<div>Level\n1
<div>Level\n2
<div>Level\n3</div>
Back\nto\n2
</div>
Back\nto\n1
</div>"""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        result = clean_text_nodes(element)
        expected = "<div>Level 1 <div>Level 2 <div>Level 3</div> Back to 2 </div> Back to 1 </div>"
        self.assertEqual(result, expected)

    def test_div_with_mixed_nested_elements(self):
        """Test div containing various nested elements with newlines"""
        html = """<div>
Start\ntext
<p>Paragraph\nwith\nnewlines</p>
<div>Nested\ndiv</div>
<span>Span\ntext</span>
End\ntext
</div>"""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        result = clean_text_nodes(element)
        expected = "<div> Start text <p>Paragraph with newlines</p> <div>Nested div</div> <span>Span text</span> End text </div>"
        self.assertEqual(result, expected)

    def test_div_with_attributes_and_newlines(self):
        """Test div with attributes and newlines in content"""
        html = '<div class="container" id="main">Content\nwith\nnewlines</div>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        result = clean_text_nodes(element)
        expected = '<div class="container" id="main">Content with newlines</div>'
        self.assertEqual(result, expected)

    def test_multiple_sibling_divs_nested(self):
        """Test parent div with multiple sibling divs containing newlines"""
        html = """<div>
<div>First\nsibling</div>
<div>Second\nsibling</div>
<div>Third\nsibling</div>
</div>"""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        result = clean_text_nodes(element)
        expected = "<div> <div>First sibling</div> <div>Second sibling</div> <div>Third sibling</div> </div>"
        self.assertEqual(result, expected)

    def test_div_with_empty_nested_div(self):
        """Test div with empty nested div"""
        html = "<div>Before\n<div></div>\nAfter</div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        result = clean_text_nodes(element)
        expected = "<div>Before <div></div> After</div>"
        self.assertEqual(result, expected)

    def test_div_with_code_and_newlines(self):
        """Test div containing code blocks with newlines"""
        html = """<div>
Text\nbefore
<code>code\nwith\nnewlines</code>
Text\nafter
</div>"""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        result = clean_text_nodes(element)
        expected = "<div> Text before <code>code with newlines</code> Text after </div>"
        self.assertEqual(result, expected)

    def test_div_triple_quoted_with_indentation(self):
        """Test div with triple-quoted string maintaining indentation spaces"""
        html = """<div>
    First line with indent
        Second line with more indent
    Third line
</div>"""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        result = clean_text_nodes(element)
        expected = "<div>     First line with indent         Second line with more indent     Third line </div>"
        self.assertEqual(result, expected)


class TestTitleLevelProperty(unittest.TestCase):
    """Test suite for Title.level computed property"""

    def test_h1_level(self):
        """Test level computation for h1"""
        html = "<h1>Title</h1>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h1")
        title = Piece.build_from_bs4_element(element)
        self.assertIsInstance(title, Title)
        self.assertEqual(title.level, 1)

    def test_h2_level(self):
        """Test level computation for h2"""
        html = "<h2>Title</h2>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h2")
        title = Piece.build_from_bs4_element(element)
        self.assertIsInstance(title, Title)
        self.assertEqual(title.level, 2)

    def test_h3_level(self):
        """Test level computation for h3"""
        html = "<h3>Title</h3>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h3")
        title = Piece.build_from_bs4_element(element)
        self.assertIsInstance(title, Title)
        self.assertEqual(title.level, 3)

    def test_title_with_nested_code(self):
        """Test title with nested inline code"""
        html = "<h2>Title with <code>code</code></h2>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h2")
        title = Piece.build_from_bs4_element(element)
        self.assertIsInstance(title, Title)
        self.assertEqual(title.level, 2)
        self.assertEqual(title.page_element_string, html)

    def test_title_with_nested_emphasis(self):
        """Test title with nested emphasis"""
        html = "<h2>Title with <em>emphasis</em> and <strong>bold</strong></h2>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h2")
        title = Piece.build_from_bs4_element(element)
        self.assertIsInstance(title, Title)
        self.assertEqual(title.level, 2)


class TestCodeLanguageProperty(unittest.TestCase):
    """Test suite for Code.language computed property"""

    def test_python_language(self):
        """Test language extraction for Python"""
        html = '<pre><code class="language-python">def hello(): pass</code></pre>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)
        self.assertIsInstance(code, Code)
        self.assertEqual(code.language, "python")

    def test_javascript_language(self):
        """Test language extraction for JavaScript"""
        html = '<pre><code class="language-javascript">console.log("hello");</code></pre>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)
        self.assertIsInstance(code, Code)
        self.assertEqual(code.language, "javascript")

    def test_rust_language(self):
        """Test language extraction for Rust"""
        html = '<pre><code class="language-rust">fn main() {}</code></pre>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)
        self.assertIsInstance(code, Code)
        self.assertEqual(code.language, "rust")

    def test_go_language(self):
        """Test language extraction for Go"""
        html = '<pre><code class="language-go">func main() {}</code></pre>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)
        self.assertIsInstance(code, Code)
        self.assertEqual(code.language, "go")

    def test_no_language(self):
        """Test language extraction when no language specified"""
        html = "<pre><code>plain code</code></pre>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)
        self.assertIsInstance(code, Code)
        self.assertIsNone(code.language)

    def test_language_with_multiple_classes(self):
        """Test language extraction when code has multiple classes"""
        html = '<pre><code class="line-numbers language-python">code</code></pre>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)
        self.assertIsInstance(code, Code)
        self.assertEqual(code.language, "python")


class TestComplexContent(unittest.TestCase):
    """Test suite for complex nested HTML content"""

    def test_paragraph_with_nested_formatting(self):
        """Test paragraph with multiple nested elements"""
        html = "<p>This is <strong>bold</strong> and <em>italic</em> with <a href='#'>link</a></p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        paragraph = Piece.build_from_bs4_element(element)
        self.assertIsInstance(paragraph, Paragraph)
        # Verify all nested elements are preserved
        html_content = paragraph.page_element_string
        self.assertEqual(html.replace("'", "\""), html_content)

    def test_paragraph_with_line_breaks(self):
        """Test paragraph with br tags"""
        html = "<p>Line 1<br/>Line 2<br/>Line 3</p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        paragraph = Piece.build_from_bs4_element(element)
        self.assertIsInstance(paragraph, Paragraph)
        self.assertIn("<br/>", paragraph.page_element_string)

    def test_nested_unordered_list(self):
        """Test nested list structure"""
        html = """<ul>
<li>Item 1
<ul>
<li>Subitem 1.1</li>
<li>Subitem 1.2</li>
</ul>
</li>
<li>Item 2</li>
</ul>"""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("ul")
        ul = Piece.build_from_bs4_element(element)
        self.assertIsInstance(ul, UnorderedList)
        self.assertEqual(ul.page_element_string, html)

    def test_table_with_thead_tbody(self):
        """Test complex table structure"""
        html = """<table>
<thead>
<tr><th>Name</th><th>Age</th></tr>
</thead>
<tbody>
<tr><td>Alice</td><td>30</td></tr>
<tr><td>Bob</td><td>25</td></tr>
</tbody>
</table>"""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("table")
        table = Piece.build_from_bs4_element(element)
        self.assertIsInstance(table, Table)
        html_content = table.page_element_string
        self.assertEqual(table.page_element_string, html)

    def test_empty_paragraph(self):
        """Test empty paragraph returns None"""
        html = "<p></p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        paragraph = Piece.build_from_bs4_element(element)
        # Empty paragraphs are now filtered out
        self.assertIsNone(paragraph)

    def test_whitespace_only_paragraph(self):
        """Test paragraph with only whitespace returns None"""
        html = "<p>   </p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        paragraph = Piece.build_from_bs4_element(element)
        # Whitespace-only paragraphs are now filtered out
        self.assertIsNone(paragraph)


if __name__ == "__main__":
    unittest.main()
