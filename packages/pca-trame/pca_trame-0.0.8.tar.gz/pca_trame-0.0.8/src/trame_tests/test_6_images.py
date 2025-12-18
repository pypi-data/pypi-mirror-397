from bs4 import BeautifulSoup

from trame.piece import Piece, Image
from trame import TrameBuilder
from trame_tests import TrameTestCase


# NOTE mad: all images are in a paragraph, as they are retrieved by markdown


class TestImageDetection(TrameTestCase):
    """Test suite for Image detection and parsing"""

    def test_html_to_image(self):
        """Test that img tags are detected as Image"""
        html = '<p><img src="test.png" alt="Test image"></p>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        image = Piece.build_from_bs4_element(element)
        self.assertIsInstance(image, Image)
        self.assertEqual(image.description, "Test image")

    def test_html_to_image_without_alt(self):
        """Test that img without alt attribute has None description"""
        html = '<p><img src="test.png"></p>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        image = Piece.build_from_bs4_element(element)
        self.assertIsInstance(image, Image)
        self.assertIsNone(image.description)

    def test_html_to_image_with_empty_alt(self):
        """Test that img with empty alt has empty string description"""
        html = '<p><img src="test.png" alt=""></p>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        image = Piece.build_from_bs4_element(element)
        self.assertIsInstance(image, Image)
        self.assertEqual(image.description, "")

    def test_html_to_image_with_special_characters_in_alt(self):
        """Test that img alt with special characters is preserved"""
        html = '<p><img src="test.png" alt="Math: $x = y + 2$"></p>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        image = Piece.build_from_bs4_element(element)
        self.assertIsInstance(image, Image)
        self.assertEqual(image.description, "Math: $x = y + 2$")

    def test_markdown_to_image(self):
        """Test that markdown images are detected as Image"""
        md = """# Some title

![Test image](test.png)
"""
        trame = TrameBuilder.from_string("test", md)
        image = trame.pieces[1]
        self.assertIsInstance(image, Image)
        self.assertEqual(image.description, "Test image")

    def test_markdown_to_image_without_alt(self):
        """Test markdown image without alt text"""
        md = """# Some title

![](test.png)
"""
        trame = TrameBuilder.from_string("test", md)
        image = trame.pieces[1]
        self.assertIsInstance(image, Image)
        self.assertEqual(image.description, "")

    def test_markdown_to_image_with_title(self):
        """Test markdown image with title attribute"""
        md = """# Some title

![Alt text](test.png "Title text")
"""
        trame = TrameBuilder.from_string("test", md)
        image = trame.pieces[1]
        self.assertIsInstance(image, Image)
        self.assertEqual(image.description, "Alt text")

    def test_markdown_multiple_images(self):
        """Test multiple images in markdown"""
        md = """# Gallery

![First image](img1.png)

Some text between images.

![Second image](img2.png)
"""
        trame = TrameBuilder.from_string("test", md)
        images = [piece for piece in trame.pieces if isinstance(piece, Image)]
        self.assertEqual(len(images), 2)
        self.assertEqual(images[0].description, "First image")
        self.assertEqual(images[1].description, "Second image")

    def test_markdown_image_with_complex_alt(self):
        """Test image with complex alt text including special characters"""
        md = """# Document

![Graph showing $f(x) = x^2$ with domain [0, 10]](graph.png)
"""
        trame = TrameBuilder.from_string("test", md)
        image = trame.pieces[1]
        self.assertIsInstance(image, Image)
        self.assertEqual(image.description, "Graph showing $f(x) = x^2$ with domain [0, 10]")

    def test_markdown_image_with_url_path(self):
        """Test image with various URL formats"""
        test_cases = [
            ("![Local](./images/test.png)", "Local"),
            ("![Absolute](/path/to/image.png)", "Absolute"),
            ("![URL](https://example.com/image.png)", "URL"),
            ("![Relative](../images/test.png)", "Relative"),
        ]
        for md_snippet, expected_alt in test_cases:
            md = f"# Test\n\n{md_snippet}"
            trame = TrameBuilder.from_string("test", md)
            image = trame.pieces[1]
            self.assertIsInstance(image, Image)
            self.assertEqual(image.description, expected_alt)

    def test_html_image_with_additional_attributes(self):
        """Test that images with extra HTML attributes are still parsed"""
        html = '<p><img src="test.png" alt="Test" width="100" height="200" class="centered"></p>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("p")
        image = Piece.build_from_bs4_element(element)
        self.assertIsInstance(image, Image)
        self.assertEqual(image.description, "Test")
