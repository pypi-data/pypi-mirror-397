from bs4 import BeautifulSoup

from trame.piece import Piece, YamlCode, Code
from trame import TrameBuilder

from trame_tests import TrameTestCase


class TestYamlCodeDetection(TrameTestCase):
    """Test suite for YamlCode subclass detection"""

    def test_html_to_yaml_code(self):
        """Test that YAML code blocks are detected as YamlCode"""
        html = '<pre><code class="language-yaml">key: value</code></pre>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)
        self.assertIsInstance(code, Code)
        self.assertIsInstance(code, YamlCode)
        self.assertEqual(code.language, "yaml")

        self.assertEqual(code.content, code.actors[0])

    def test_pca_nature(self):
        """Test that YAML code blocks are detected as YamlCode"""
        html = '<pre><code class="language-yaml">key: value</code></pre>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)

        self.assertEqual(code.language, "yaml")
        self.assertEqual(code.content.pca_nature, "pure_yaml")
        self.assertNotIn("pca_nature", code.content.data.keys())

        html = '<pre><code class="language-yaml">pca_nature: diagraphe\nkey: value\n</code></pre>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)

        self.assertEqual(code.language, "yaml")
        self.assertEqual(code.content.pca_nature, "diagraphe")
        self.assertNotIn("pca_nature", code.content.data.keys())

    def test_html_to_yaml_code_with_complex_content(self):
        """Test YamlCode with complex YAML content"""
        html = """<pre><code class="language-yaml">
person:
  name: John
  age: 30
  hobbies:
    - reading
    - coding
</code></pre>"""
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)
        self.assertIsInstance(code, YamlCode)
        self.assertEqual(
            code.code_str,
            """
person:
  name: John
  age: 30
  hobbies:
    - reading
    - coding
""",
        )

    def test_html_to_non_yaml_code_not_yamlcode(self):
        """Test that non-YAML code blocks are not YamlCode"""
        html = '<pre><code class="language-python">print("hello")</code></pre>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)
        self.assertIsInstance(code, Code)
        self.assertNotIsInstance(code, YamlCode)

    def test_html_to_yaml_code_with_multiple_classes(self):
        """Test YamlCode detection when code has multiple classes"""
        html = '<pre><code class="line-numbers language-yaml">key: value</code></pre>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)
        self.assertIsInstance(code, YamlCode)
        self.assertEqual(code.language, "yaml")

    def test_html_to_code_without_language_not_yamlcode(self):
        """Test that code without language is not YamlCode"""
        html = "<pre><code>plain code</code></pre>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("pre")
        code = Piece.build_from_bs4_element(element)
        self.assertIsInstance(code, Code)
        self.assertNotIsInstance(code, YamlCode)
        self.assertIsNone(code.language)

    def test_markdown_to_yaml_code(self):
        """Test that YAML code blocks are detected as YamlCode"""
        md = """ # Some title

```yaml
key: value
```
"""
        trame = TrameBuilder.from_string("test", md)
        code = trame.pieces[1]
        self.assertEqual(code.language, "yaml")
        self.assertIsInstance(code, Code)
        self.assertIsInstance(code, YamlCode)
        self.assertDictEqual(code.content.data, {"key": "value"})
        self.assertEqual(code.content.pca_nature, "pure_yaml")

    def test_markdown_to_yaml_code_with_complex_content(self):
        """Test YamlCode with complex YAML content"""
        md = """ # Some title

```yaml
person:
  name: John
  age: 30
  hobbies:
    - reading
    - coding
```
"""
        trame = TrameBuilder.from_string("test", md)
        code = trame.pieces[1]
        self.assertIsInstance(code, YamlCode)
        self.assertEqual(
            code.content.data,
            {
                "person": {
                    "name": "John",
                    # NOTE mad: int was parsed as string
                    "age": "30",
                    "hobbies": ["reading", "coding"],
                }
            },
        )

    def test_markdown_to_yaml_code_with_pipe(self):
        """Test YamlCode with complex YAML content"""
        md = """ # Some title

```yaml
person:
  name: John
  long: |-
    this is some long string with one line return after
  age : 30
```
"""
        trame = TrameBuilder.from_string("test", md)
        code = trame.pieces[1]
        self.assertIsInstance(code, YamlCode)
        self.assertEqual(
            code.content.data,
            {
                "person": {
                    "name": "John",
                    # NOTE mad: int was parsed as string
                    "age": "30",
                    "long": "this is some long string with one line return after",
                }
            },
        )


class Sujets0YamlTestCase(TrameTestCase):
    def test_1_type(self):
        trame = TrameBuilder.from_file("src/trame_tests/data/sujet_0_spe_sujet_1.md")
        code = trame.pieces[0]
        self.assertIsInstance(code, YamlCode)
        self.assertAllLeafValuesType(code.content.data, str)

    def test_2_type(self):
        trame = TrameBuilder.from_file("src/trame_tests/data/sujet_0_spe_sujet_2.md")
        code = trame.pieces[0]
        self.assertIsInstance(code, YamlCode)
        self.assertAllLeafValuesType(code.content.data, str)

    def test_1_structure(self):
        trame = TrameBuilder.from_file("src/trame_tests/data/sujet_0_spe_sujet_1.md")
        code = trame.pieces[0]
        self.assertIsInstance(code, YamlCode)
        # self.assertDictStructureMatches(code.content.data, {"part_1": ..., "part_2": ...})
        self.assertDictStructureMatches(
            code.content.data,
            {
                "part_1": {
                    "question_1": {
                        "statement": "L'inverse du double de $5$ est égal à :",
                        "choices": {
                            "a": "$\\dfrac{2}{5}$",
                            "b": "$\\dfrac{1}{10}$",
                            "c": "$\\dfrac{5}{2}$",
                            "d": "$10$",
                        },
                        "correct_answer": "b",
                    },
                    "question_2": {
                        "statement": ...,
                        "choices": {
                            "a": ...,
                            "b": ...,
                            "c": ...,
                            "d": ...,
                        },
                        "correct_answer": ...,
                    },
                    "question_3": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_4": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_5": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                        "table": ...,
                        "question": ...,
                    },
                    "question_6": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_7": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_8": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_9": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                        "fonctions": ...,
                        "question": ...,
                    },
                    "question_10": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_11": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_12": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                        "table": ...,
                        "question": ...,
                    },
                },
                "part_2": ...,
            },
        )

    def test_2_structure(self):
        trame = TrameBuilder.from_file("src/trame_tests/data/sujet_0_spe_sujet_2.md")
        code = trame.pieces[0]
        self.assertIsInstance(code, YamlCode)
        # self.assertDictStructureMatches(code.content.data, {"part_1": ..., "part_2": ...})
        self.assertDictStructureMatches(
            code.content.data,
            {
                "part_1": {
                    "question_1": {
                        "statement": ...,
                        "choices": {
                            "a": ...,
                            "b": ...,
                            "c": ...,
                            "d": ...,
                        },
                        "correct_answer": ...,
                    },
                    "question_2": {
                        "statement": ...,
                        "choices": {
                            "a": ...,
                            "b": ...,
                            "c": ...,
                            "d": ...,
                        },
                        "correct_answer": ...,
                    },
                    "question_3": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_4": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_5": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                        # "table": ...,
                        # "question": ...,
                    },
                    "question_6": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_7": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_8": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_9": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_10": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_11": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                    "question_12": {
                        "statement": ...,
                        "choices": ...,
                        "correct_answer": ...,
                    },
                },
                "part_2": ...,
            },
        )
