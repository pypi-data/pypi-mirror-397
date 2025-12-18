from trame import TrameBuilder
from trame_tests import TrameTestCase


class TestMetadataParsing(TrameTestCase):
    """Test suite for markdown metadata parsing"""

    def test_markdown_with_frontmatter(self):
        """Test that YAML frontmatter is parsed correctly"""
        md = """---
title: My Document
author: John Doe
date: 2024-01-15
---

# Content here

Some text.
"""
        trame = TrameBuilder.from_string("test", md)
        self.assertIsNotNone(trame.metadata)
        self.assertEqual(trame.metadata.get("title"), ["My Document"])
        self.assertEqual(trame.metadata.get("author"), ["John Doe"])
        self.assertEqual(trame.metadata.get("date"), ["2024-01-15"])

    def test_markdown_without_frontmatter(self):
        """Test that markdown without frontmatter has empty metadata"""
        md = """# Just a title

Some content without metadata.
"""
        trame = TrameBuilder.from_string("test", md)
        self.assertEqual(trame.metadata, {})

    def test_markdown_with_multiline_metadata(self):
        """Test metadata with multiple values on same key"""
        md = """---
title: Main Title
tags: python
tags: markdown
tags: testing
---

# Content
"""
        trame = TrameBuilder.from_string("test", md)
        self.assertIn("tags", trame.metadata)
        self.assertEqual(len(trame.metadata.get("tags")), 3)
        self.assertListEqual(trame.metadata.get("tags"), ["python", "markdown", "testing"])

    def test_markdown_with_empty_metadata_value(self):
        """Test metadata with empty values"""
        md = """---
title: Document Title
description:
author: Jane Smith
---

# Content
"""
        trame = TrameBuilder.from_string("test", md)
        self.assertEqual(trame.metadata.get("title"), ["Document Title"])
        self.assertEqual(trame.metadata.get("description"), [""])
        self.assertEqual(trame.metadata.get("author"), ["Jane Smith"])

    def test_metadata_does_not_affect_content(self):
        """Test that metadata doesn't interfere with content parsing"""
        md = """---
title: Test Document
---

# Heading
```yaml
key: value
```
"""
        trame = TrameBuilder.from_string("test", md)
        self.assertEqual(trame.metadata.get("title"), ["Test Document"])
        self.assertEqual(len(trame.pieces), 2)
        # First piece should be heading, second should be YamlCode
        from trame.piece import YamlCode

        self.assertIsInstance(trame.pieces[1], YamlCode)

    def test_metadata_with_special_characters(self):
        """Test metadata with special characters and colons"""
        md = """---
title: Document: A Study
url: https://example.com
math: $x = y + 2$
---

# Content
"""
        trame = TrameBuilder.from_string("test", md)
        self.assertEqual(trame.metadata.get("title"), ["Document: A Study"])
        self.assertEqual(trame.metadata.get("url"), ["https://example.com"])
        self.assertEqual(trame.metadata.get("math"), ["$x = y + 2$"])

    def test_existing_files_have_metadata_structure(self):
        """Test that existing test files return metadata dict (even if empty)"""
        trame = TrameBuilder.from_file("src/trame_tests/data/sujet_0_spe_sujet_1.md")
        self.assertIsInstance(trame.metadata, dict)
