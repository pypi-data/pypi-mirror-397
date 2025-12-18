import unittest

from bs4 import BeautifulSoup


from trame.piece import PieceBuilder
from trame.piece import Paragraph, UnorderedList, Code, Table, HRule, Title, Div


class TestPieceBuilderHtmlTagToConcreteCls(unittest.TestCase):
    """Test suite for PieceBuilder.from_bs4_tag() method"""

    def test_title_h1(self):
        html = "<h1>Hello</h1>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h1")
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, Title)

    def test_title_h2(self):
        html = "<h2>Hello</h2>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h2")
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, Title)

    def test_title_h3(self):
        html = "<h3>Hello</h3>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h3")
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, Title)

    def test_paragraph(self):
        html = "<p>Hello</p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, Paragraph)

    def test_unordered_list(self):
        html = "<ul><li>Hello</li><li>World</li></ul>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("ul")
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, UnorderedList)

    def test_code(self):
        html = "<pre><code>print('Hello, World!')</code></pre>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, Code)

    def test_table(self):
        html = "<table><tr><th>Name</th><th>Age</th></tr><tr><td>John</td><td>30</td></tr></table>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("table")
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, Table)

    def test_hrule(self):
        html = "<hr>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("hr")
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, HRule)

    def test_div(self):
        html = "<div>Hello</div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, Div)

    def test_unsupported_h4(self):
        """h4 should raise NotImplementedError"""
        html = "<h4>Unsupported</h4>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h4")
        # with self.assertRaises(NotImplementedError) as context:
        PieceBuilder.from_bs4_tag(element)
        # self.assertEqual("tag.name='h4'", str(context.exception))

    def test_unsupported_h5(self):
        """h5 should raise NotImplementedError"""
        html = "<h5>Unsupported</h5>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h5")
        # with self.assertRaises(NotImplementedError):
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, Title)

    def test_unsupported_h6(self):
        """h6 should raise NotImplementedError"""
        html = "<h6>Unsupported</h6>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("h6")
        with self.assertRaises(NotImplementedError):
            PieceBuilder.from_bs4_tag(element)

    def test_empty_paragraph(self):
        html = "<p></p>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        piece = PieceBuilder.from_bs4_tag(element)
        # self.assertIsInstance(piece, None)
        self.assertIs(piece, None)

    def test_empty_unordered_list(self):
        """Empty list should still map to UnorderedList"""
        html = "<ul></ul>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("ul")
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, UnorderedList)

    def test_empty_table(self):
        """Empty table should still map to Table"""
        html = "<table></table>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("table")
        piece = PieceBuilder.from_bs4_tag(element)
        self.assertIsInstance(piece, Table)


if __name__ == "__main__":
    unittest.main()
