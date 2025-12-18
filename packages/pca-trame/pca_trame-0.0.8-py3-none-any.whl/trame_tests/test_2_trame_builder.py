import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from trame import Trame, TrameBuilder
from trame.piece import Title, Paragraph, UnorderedList, Code, Table, HRule


class TestTrameBuilder(unittest.TestCase):
    """Test suite for TrameBuilder.from_string() method"""

    def test_simple_paragraph(self):
        markdown_content = "This is a paragraph."
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        self.assertIsInstance(trame, Trame)
        self.assertEqual(trame.origin, "test")
        self.assertEqual(trame.markdown_content, markdown_content)
        self.assertEqual(len(trame.pieces), 1)
        self.assertIsInstance(trame.pieces[0], Paragraph)

    def test_title(self):
        markdown_content = "# This is a title"
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        self.assertEqual(len(trame.pieces), 1)
        self.assertIsInstance(trame.pieces[0], Title)

    def test_unordered_list(self):
        markdown_content = """- Item 1
- Item 2
- Item 3"""
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        self.assertEqual(len(trame.pieces), 1)
        self.assertIsInstance(trame.pieces[0], UnorderedList)

    def test_code_block(self):
        markdown_content = """```python
print("Hello, World!")
```"""
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        self.assertEqual(len(trame.pieces), 1)
        self.assertIsInstance(trame.pieces[0], Code)

    def test_code_block_with_language(self):
        markdown_content = """```javascript
console.log("Hello, World!");
```"""
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        self.assertEqual(len(trame.pieces), 1)
        piece = trame.pieces[0]
        self.assertIsInstance(piece, Code)
        self.assertEqual(piece.language, "javascript")

    def test_horizontal_rule(self):
        markdown_content = """Paragraph before

---

Paragraph after"""
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        self.assertEqual(len(trame.pieces), 3)
        self.assertIsInstance(trame.pieces[0], Paragraph)
        self.assertIsInstance(trame.pieces[1], HRule)
        self.assertIsInstance(trame.pieces[2], Paragraph)

    def test_table(self):
        markdown_content = """| Name | Age |
|------|-----|
| John | 30  |
| Jane | 25  |"""
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        self.assertEqual(len(trame.pieces), 1)
        self.assertIsInstance(trame.pieces[0], Table)

    def test_mixed_content(self):
        markdown_content = """# Main Title

This is an introduction paragraph.

## Features

- Feature 1
- Feature 2
- Feature 3

## Code Example

```python
def hello():
    print("Hello!")
```

---

End of document."""
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        # Should have: Title, Paragraph, Title, UnorderedList, Title, Code, HRule, Paragraph
        self.assertEqual(len(trame.pieces), 8)
        self.assertIsInstance(trame.pieces[0], Title)
        self.assertIsInstance(trame.pieces[1], Paragraph)
        self.assertIsInstance(trame.pieces[2], Title)
        self.assertIsInstance(trame.pieces[3], UnorderedList)
        self.assertIsInstance(trame.pieces[4], Title)
        self.assertIsInstance(trame.pieces[5], Code)
        self.assertIsInstance(trame.pieces[6], HRule)
        self.assertIsInstance(trame.pieces[7], Paragraph)

    def test_non_empty_markdown(self):
        markdown_content = ""
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        self.assertEqual(len(trame.pieces), 0)

    def test_multiple_pieces(self):
        markdown_content = """# Title

This is a paragraph.

## Subtitle

Another paragraph."""
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        self.assertEqual(len(trame.pieces), 4)
        self.assertIsInstance(trame.pieces[0], Title)
        self.assertIsInstance(trame.pieces[1], Paragraph)
        self.assertIsInstance(trame.pieces[2], Title)
        self.assertIsInstance(trame.pieces[3], Paragraph)

    def test_origin_preserved(self):
        markdown_content = "Test content"
        origin = "test_document.md"
        trame = TrameBuilder.from_string(origin=origin, markdown_content=markdown_content)

        self.assertEqual(trame.origin, origin)

    def test_html_content_generated(self):
        markdown_content = "# Title\n\nParagraph"
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        expected_html = "<h1>Title</h1>\n<p>Paragraph</p>"
        self.assertEqual(trame.html_content, expected_html)

    def test_empty_markdown(self):
        """Test parsing empty markdown string"""
        markdown_content = ""
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)
        self.assertEqual(len(trame.pieces), 0)
        self.assertEqual(trame.markdown_content, "")

    def test_whitespace_only_markdown(self):
        """Test parsing markdown with only whitespace"""
        markdown_content = "   \n\n   \n"
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)
        self.assertLessEqual(len(trame.pieces), 1)

    def test_blank_lines_only(self):
        """Test parsing markdown with only blank lines"""
        markdown_content = "\n\n\n\n"
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)
        self.assertEqual(len(trame.pieces), 0)

    def test_utf8_characters(self):
        """Test parsing markdown with UTF-8 characters"""
        markdown_content = (
            "# Français et Émojis 🎉\n\nVoici des accents: é, è, ê, ë.\n\nEt des emojis: 😀 🎈 ✨"
        )
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)
        self.assertGreater(len(trame.pieces), 0)
        # Verify UTF-8 is preserved in first piece (title)
        self.assertIsInstance(trame.pieces[0], Title)
        self.assertIsInstance(trame.pieces[1], Paragraph)
        self.assertIsInstance(trame.pieces[2], Paragraph)
        self.assertEqual("<h1>Français et Émojis 🎉</h1>", trame.pieces[0].page_element_string)
        self.assertEqual(
            "<p>Voici des accents: é, è, ê, ë.</p>", trame.pieces[1].page_element_string
        )
        self.assertEqual("<p>Et des emojis: 😀 🎈 ✨</p>", trame.pieces[2].page_element_string)

    def test_special_characters(self):
        """Test parsing markdown with special characters"""
        markdown_content = "Special chars: < > & \" ' @ # $ % ^"
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)
        self.assertEqual(len(trame.pieces), 1)
        self.assertIsInstance(trame.pieces[0], Paragraph)
        # HTML entities should be properly escaped
        html = trame.pieces[0].page_element_string
        self.assertEqual(html, "<p>Special chars: &lt; &gt; &amp; \" ' @ # $ % ^</p>")

    def test_mixed_heading_level_sequence(self):
        """Test mixed heading levels in specific sequence"""
        markdown_content = """# H1 Title
## H2 Title
### H3 Title
## Another H2
# Another H1"""
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        titles = [piece for piece in trame.pieces if isinstance(piece, Title)]
        self.assertEqual(len(titles), 5)

        # Verify exact level sequence
        levels = [title.level for title in titles]
        self.assertEqual(levels, [1, 2, 3, 2, 1])

    def test_multiple_blank_lines_between_paragraphs(self):
        """Test that multiple blank lines collapse properly"""
        markdown_content = "Paragraph 1\n\n\n\nParagraph 2"
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        paragraphs = [piece for piece in trame.pieces if isinstance(piece, Paragraph)]
        self.assertEqual(len(paragraphs), 2)

    def test_inline_formatting(self):
        """Test markdown with inline formatting"""
        markdown_content = "This is **bold** and *italic* and `code` text."
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        self.assertEqual(len(trame.pieces), 1)
        paragraph = trame.pieces[0]
        self.assertIsInstance(paragraph, Paragraph)
        html = paragraph.page_element_string
        self.assertEqual(
            html,
            "<p>This is <strong>bold</strong> and <em>italic</em> and <code>code</code> text.</p>",
        )

    def test_links_in_paragraph(self):
        """Test markdown with links"""
        markdown_content = "Check out [this link](https://example.com) for more."
        trame = TrameBuilder.from_string(origin="test", markdown_content=markdown_content)

        self.assertEqual(len(trame.pieces), 1)
        paragraph = trame.pieces[0]
        self.assertIsInstance(paragraph, Paragraph)
        html = paragraph.page_element_string
        self.assertEqual(
            html, '<p>Check out <a href="https://example.com">this link</a> for more.</p>'
        )


class TestTrameBuilderFromFile(unittest.TestCase):
    """Test suite for TrameBuilder.from_file() method"""

    @classmethod
    def setUpClass(cls):
        """Set up test file path"""
        cls.test_file_path = Path(__file__).parent / "data" / "rgpd_maths.pm.md"
        assert cls.test_file_path.exists(), f"Test file not found: {cls.test_file_path}"

    def test_from_file_complete_structure_and_content(self):
        """Test complete file loading, parsing, and structure validation"""
        trame = TrameBuilder.from_file(self.test_file_path)

        # === Basic instance and metadata ===
        self.assertIsInstance(trame, Trame)
        self.assertEqual(trame.path, self.test_file_path)
        self.assertEqual(trame.origin, str(self.test_file_path))

        # === Markdown content ===
        self.assertIsNotNone(trame.markdown_content)
        self.assertEqual(len(trame.markdown_content), 5288)
        self.assertTrue(trame.markdown_content.startswith("# RGPD & Confidentialité"))
        self.assertTrue(
            trame.markdown_content.endswith(
                "ay  \nFrance\n\n&nbsp;\n\n---\n\n*Dernière mise à jour : Octobre 2025*\n{: .text-sm .text-base-content/60}\n\n"
            )
        )

        # === HTML content ===
        self.assertIsNotNone(trame.html_content)
        self.assertEqual(len(trame.html_content), 6441)
        self.assertTrue(trame.html_content.startswith("<h1>RGPD &amp; Confidentialité</h1>"))
        self.assertTrue(
            trame.html_content.endswith(
                "p;</p>\n<hr />\n<p><em>Dernière mise à jour : Octobre 2025</em>\n{: .text-sm .text-base-content/60}</p>"
            )
        )

        # === Pieces structure ===
        self.assertIsNotNone(trame.pieces)
        self.assertEqual(len(trame.pieces), 52)

        # Verify first 12 pieces structure
        self.assertIsInstance(trame.pieces[0], Title)
        self.assertIsInstance(trame.pieces[1], Paragraph)
        self.assertIsInstance(trame.pieces[2], Title)
        self.assertIsInstance(trame.pieces[3], Paragraph)
        self.assertIsInstance(trame.pieces[4], Title)
        self.assertIsInstance(trame.pieces[5], Title)
        self.assertIsInstance(trame.pieces[6], Paragraph)
        self.assertIsInstance(trame.pieces[7], UnorderedList)
        self.assertIsInstance(trame.pieces[8], Title)
        self.assertIsInstance(trame.pieces[9], Paragraph)
        self.assertIsInstance(trame.pieces[10], UnorderedList)
        self.assertIsInstance(trame.pieces[11], Title)

        # === First piece (main title) ===
        first_piece = trame.pieces[0]
        self.assertIsInstance(first_piece, Title)
        self.assertEqual(first_piece.level, 1)
        self.assertEqual(first_piece.page_element_string, "<h1>RGPD &amp; Confidentialité</h1>")
        self.assertEqual(first_piece.page_element_tag, "h1")

        # === All titles validation ===
        titles = [piece for piece in trame.pieces if isinstance(piece, Title)]
        self.assertEqual(len(titles), 17)
        # Verify first few title levels
        self.assertEqual(titles[0].level, 1)  # h1
        self.assertEqual(titles[1].level, 2)  # h2
        self.assertEqual(titles[2].level, 2)  # h2
        self.assertEqual(titles[3].level, 3)  # h3
        self.assertEqual(titles[4].level, 3)  # h3
        # Complete level sequence for all 17 titles

        levels = [title.level for title in titles]
        self.assertEqual(levels, [1, 2, 2, 3, 3, 2, 3, 3, 3, 2, 2, 3, 3, 2, 2, 2, 2])

        # === All paragraphs validation ===
        paragraphs = [piece for piece in trame.pieces if isinstance(piece, Paragraph)]
        self.assertEqual(len(paragraphs), 25)
        # Verify specific paragraph with cleaned HTML
        para_3 = trame.pieces[3]
        self.assertIsInstance(para_3, Paragraph)
        expected_html_3 = "<p>La société POINTCARRE.APP accorde une importance primordiale à la protection de vos données personnelles. Pour le site <strong>Maths.pm</strong>, nous avons fait le choix d'une <strong>architecture zero-data</strong> qui garantit, par conception, l'absence de collecte de données personnelles.</p>"
        self.assertEqual(para_3.html, expected_html_3)

        # === All unordered lists validation ===
        lists = [piece for piece in trame.pieces if isinstance(piece, UnorderedList)]
        self.assertEqual(len(lists), 9)
        # Verify specific lists with exact item counts (using piece indices from structure)
        list_at_7 = trame.pieces[7]  # First list in structure
        self.assertIsInstance(list_at_7, UnorderedList)
        self.assertEqual(len(list_at_7.actors), 5)
        self.assertEqual(list_at_7.page_element_tag, "ul")
        list_at_10 = trame.pieces[10]  # Second list in structure
        self.assertIsInstance(list_at_10, UnorderedList)
        self.assertEqual(len(list_at_10.actors), 6)
        list_at_16 = trame.pieces[16]  # Third list in structure
        self.assertIsInstance(list_at_16, UnorderedList)
        self.assertEqual(len(list_at_16.actors), 4)

        # === Horizontal rule validation ===
        hrules = [piece for piece in trame.pieces if isinstance(piece, HRule)]
        self.assertEqual(len(hrules), 1)
        hrule_piece = hrules[0]
        self.assertEqual(hrule_piece.html, "<hr/>")
        self.assertEqual(hrule_piece.page_element_tag, "hr")

        # === HTML property validation for all piece types ===

        # Title pieces - verify HTML is cleaned
        self.assertEqual(trame.pieces[0].html, "<h1>RGPD &amp; Confidentialité</h1>")
        self.assertEqual(
            trame.pieces[2].html, "<h2>Notre engagement pour la protection de vos données</h2>"
        )
        self.assertEqual(
            trame.pieces[4].html, "<h2>Architecture zero-data : aucune collecte par design</h2>"
        )
        self.assertEqual(trame.pieces[5].html, "<h3>Sites statiques</h3>")
        self.assertEqual(trame.pieces[8].html, "<h3>Données non collectées</h3>")

        # Paragraph pieces - verify HTML is cleaned (newlines removed)
        self.assertEqual(trame.pieces[1].html, "<p>[TOC]</p>")
        self.assertEqual(
            trame.pieces[3].html,
            "<p>La société POINTCARRE.APP accorde une importance primordiale à la protection de vos données personnelles. Pour le site <strong>Maths.pm</strong>, nous avons fait le choix d'une <strong>architecture zero-data</strong> qui garantit, par conception, l'absence de collecte de données personnelles.</p>",
        )
        self.assertEqual(
            trame.pieces[6].html,
            "<p><strong>Maths.pm</strong> repose sur une architecture de <strong>sites statiques</strong>, ce qui signifie :</p>",
        )
        self.assertEqual(
            trame.pieces[9].html,
            "<p>Nous ne collectons, ne stockons et ne transmettons <strong>aucune des données suivantes</strong> :</p>",
        )

        # UnorderedList pieces - verify HTML is cleaned (newlines replaced with spaces)
        expected_ul_first = "<ul> <li><strong>Aucun serveur applicatif</strong> : Pas de traitement côté serveur de vos données</li> <li><strong>Aucune base de données</strong> : Aucun stockage de données utilisateur</li> <li><strong>Exécution locale</strong> : Tout le code s'exécute dans votre navigateur</li> <li><strong>Aucun cookie</strong> : Nous n'utilisons aucun cookie de suivi ou d'analyse</li> <li><strong>Aucun tracking</strong> : Aucun outil d'analyse de trafic ou de comportement</li> </ul>"
        self.assertEqual(list_at_7.html, expected_ul_first)

        expected_ul_second = "<ul> <li>Identité (nom, prénom, adresse email)</li> <li>Données de navigation (pages visitées, temps passé)</li> <li>Données d'utilisation (exercices réalisés, résultats obtenus)</li> <li>Données de géolocalisation</li> <li>Adresse IP (voir section suivante pour les exceptions)</li> <li>Informations sur votre appareil ou navigateur</li> </ul>"
        self.assertEqual(list_at_10.html, expected_ul_second)

        expected_ul_third = "<ul> <li>Votre <strong>adresse IP</strong></li> <li>La <strong>date et l'heure</strong> de votre connexion</li> <li>Les <strong>pages demandées</strong></li> <li>Le <strong>type de navigateur</strong> utilisé (User-Agent)</li> </ul>"
        self.assertEqual(list_at_16.html, expected_ul_third)

        # More title and paragraph validations
        self.assertEqual(trame.pieces[11].html, "<h2>Données techniques d'hébergement</h2>")
        self.assertEqual(trame.pieces[11].page_element_tag, "h2")
        self.assertEqual(trame.pieces[12].html, "<h3>Requêtes HTTP vues par l'hébergeur</h3>")
        self.assertEqual(
            trame.pieces[13].html,
            "<p>Bien que <strong>Maths.pm</strong> ne collecte aucune donnée, l'hébergement du site implique nécessairement le traitement de <strong>requêtes HTTP</strong> pour servir les pages :</p>",
        )
        self.assertEqual(
            trame.pieces[14].html, "<p><strong>Hébergeur actuel : GitHub Pages</strong></p>"
        )
        self.assertEqual(
            trame.pieces[15].html,
            "<p>Lorsque vous accédez au site, GitHub Pages (hébergeur temporaire) peut techniquement voir :</p>",
        )

        # === Last paragraph validation (space before {: not newline) ===
        last_piece = trame.pieces[-1]
        self.assertIsInstance(last_piece, Paragraph)
        self.assertEqual(
            last_piece.html,
            "<p><em>Dernière mise à jour : Octobre 2025</em> {: .text-sm .text-base-content/60}</p>",
        )

    def test_from_file_error_handling(self):
        """Test error cases for file loading"""
        nonexistent_path = Path("nonexistent_file.md")
        with self.assertRaises(FileNotFoundError):
            TrameBuilder.from_file(nonexistent_path)


class TestTrameBuilderFromFileEdgeCases(unittest.TestCase):
    """Test suite for edge cases when loading files"""

    def setUp(self):
        """Set up temporary files for testing"""
        self.temp_files = []

    def tearDown(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                Path(temp_file).unlink()
            except Exception:
                pass

    def create_temp_md_file(self, content):
        """Helper to create a temporary Markdown file"""
        temp = NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
        temp.write(content)
        temp.close()
        self.temp_files.append(temp.name)
        return Path(temp.name)

    def test_empty_file(self):
        """Test parsing an empty file"""
        filepath = self.create_temp_md_file("")
        trame = TrameBuilder.from_file(filepath)

        self.assertEqual(len(trame.pieces), 0)
        self.assertEqual(trame.markdown_content, "")
        self.assertEqual(trame.path, filepath)

    def test_whitespace_only_file(self):
        """Test parsing a file with only whitespace"""
        filepath = self.create_temp_md_file("   \n\n   \n")
        trame = TrameBuilder.from_file(filepath)

        self.assertLessEqual(len(trame.pieces), 1)
        self.assertEqual(trame.path, filepath)

    def test_blank_lines_only_file(self):
        """Test parsing a file with only blank lines"""
        filepath = self.create_temp_md_file("\n\n\n\n")
        trame = TrameBuilder.from_file(filepath)

        self.assertEqual(len(trame.pieces), 0)

    def test_utf8_file_with_emojis(self):
        """Test parsing a file with UTF-8 characters and emojis"""
        content = """# Français et Émojis 🎉

Voici un paragraphe avec des accents: é, è, ê, ë, à, ù.

Et des emojis: 😀 🎈 ✨"""
        filepath = self.create_temp_md_file(content)
        trame = TrameBuilder.from_file(filepath)

        self.assertGreater(len(trame.pieces), 0)
        # Check that UTF-8 is preserved
        title = trame.pieces[0]
        self.assertIsInstance(title, Title)
        self.assertEqual(title.page_element_string, "<h1>Français et Émojis 🎉</h1>")

    def test_file_with_multiple_code_blocks(self):
        """Test file with multiple code blocks in different languages"""
        content = """# Code Examples

Python code:

```python
def hello():
    print("Hello")
```

JavaScript code:

```javascript
console.log("Hello");
```"""
        filepath = self.create_temp_md_file(content)
        trame = TrameBuilder.from_file(filepath)

        code_pieces = [p for p in trame.pieces if isinstance(p, Code)]
        languages = [code.language for code in code_pieces]
        self.assertGreaterEqual(len(code_pieces), 2)
        self.assertListEqual(languages, ["python", "javascript"])

    def test_file_with_single_paragraph(self):
        """Test file with just a single paragraph"""
        content = "This is a simple paragraph."
        filepath = self.create_temp_md_file(content)
        trame = TrameBuilder.from_file(filepath)

        self.assertEqual(len(trame.pieces), 1)
        self.assertIsInstance(trame.pieces[0], Paragraph)

    def test_file_with_single_title(self):
        """Test file with just a single title"""
        content = "# Main Title"
        filepath = self.create_temp_md_file(content)
        trame = TrameBuilder.from_file(filepath)

        self.assertEqual(len(trame.pieces), 1)
        self.assertIsInstance(trame.pieces[0], Title)
        self.assertEqual(trame.pieces[0].level, 1)


if __name__ == "__main__":
    unittest.main()
