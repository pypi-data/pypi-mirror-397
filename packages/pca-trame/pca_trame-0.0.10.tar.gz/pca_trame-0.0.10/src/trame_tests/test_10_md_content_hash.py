import unittest

from trame import TrameBuilder
from trame_tests import TrameTestCase


class TestContentHash(TrameTestCase):
    """Test suite for md_content_hash computed field - basic functionality"""

    def test_hash_exists(self):
        """Test that hash property exists"""
        md = "# Title"
        trame = TrameBuilder.from_string("test", md)
        self.assertIsNotNone(trame.md_content_hash)

    def test_hash_is_string(self):
        """Test that hash is a string"""
        md = "# Title"
        trame = TrameBuilder.from_string("test", md)
        self.assertIsInstance(trame.md_content_hash, str)

    def test_hash_length(self):
        """Test that hash has correct length for SHA-256 (64 hex chars)"""
        md = "# Title"
        trame = TrameBuilder.from_string("test", md)
        self.assertEqual(len(trame.md_content_hash), 64)

    def test_hash_is_hexadecimal(self):
        """Test that hash contains only hexadecimal characters"""
        md = "# Title"
        trame = TrameBuilder.from_string("test", md)
        self.assertTrue(all(c in "0123456789abcdef" for c in trame.md_content_hash))

    def test_same_content_same_hash(self):
        """Test that identical content produces identical hash"""
        md = "# Title\n\nContent here."
        trame1 = TrameBuilder.from_string("test1", md)
        trame2 = TrameBuilder.from_string("test2", md)
        self.assertEqual(trame1.md_content_hash, trame2.md_content_hash)

    def test_different_content_different_hash(self):
        """Test that different content produces different hash"""
        md1 = "# Title\n\nContent v1"
        md2 = "# Title\n\nContent v2"
        trame1 = TrameBuilder.from_string("test1", md1)
        trame2 = TrameBuilder.from_string("test2", md2)
        self.assertNotEqual(trame1.md_content_hash, trame2.md_content_hash)

    def test_hash_deterministic(self):
        """Test that hash computation is deterministic"""
        md = "# Title\n\nSome content with **formatting**"
        hashes = []
        for i in range(5):
            trame = TrameBuilder.from_string(f"test{i}", md)
            hashes.append(trame.md_content_hash)
        self.assertEqual(len(set(hashes)), 1)

    def test_empty_content_has_hash(self):
        """Test that even empty content produces a hash"""
        md = ""
        trame = TrameBuilder.from_string("test", md)
        self.assertIsNotNone(trame.md_content_hash)
        self.assertEqual(len(trame.md_content_hash), 64)

    def test_whitespace_differences_affect_hash(self):
        """Test that whitespace differences change the hash"""
        md1 = "# Title\n\nContent"
        md2 = "# Title\n\n\nContent"
        trame1 = TrameBuilder.from_string("test1", md1)
        trame2 = TrameBuilder.from_string("test2", md2)
        self.assertNotEqual(trame1.md_content_hash, trame2.md_content_hash)

    def test_unicode_content_hash(self):
        """Test hashing content with unicode characters"""
        md = "# Título\n\nContenu avec des accents: é, è, ê, à, ù"
        trame = TrameBuilder.from_string("test", md)
        self.assertIsNotNone(trame.md_content_hash)
        self.assertEqual(len(trame.md_content_hash), 64)

    def test_emoji_content_hash(self):
        """Test hashing content with emojis"""
        md = "# Title 🎉\n\nÉmojis: 🚀 💯"
        trame = TrameBuilder.from_string("test", md)
        self.assertIsNotNone(trame.md_content_hash)
        self.assertEqual(len(trame.md_content_hash), 64)

    def test_file_loading_produces_hash(self):
        """Test that loading from file produces content hash"""
        trame = TrameBuilder.from_file("src/trame_tests/data/dummy.md")
        self.assertIsNotNone(trame.md_content_hash)
        self.assertEqual(len(trame.md_content_hash), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in trame.md_content_hash))

    def test_complex_content_hash(self):
        """Test hashing complex markdown with multiple elements"""
        md = """# Title

Paragraph with **bold** and *italic*.

- List item 1
- List item 2

```python
code block
```

> Blockquote
"""
        trame = TrameBuilder.from_string("test", md)
        self.assertIsNotNone(trame.md_content_hash)
        self.assertEqual(len(trame.md_content_hash), 64)

    def test_line_ending_normalization_unix_vs_windows(self):
        """Test that Unix (LF) and Windows (CRLF) line endings produce same hash"""
        md_unix = "# Title\nContent\nMore"
        md_windows = "# Title\r\nContent\r\nMore"
        trame_unix = TrameBuilder.from_string("test1", md_unix)
        trame_windows = TrameBuilder.from_string("test2", md_windows)
        self.assertEqual(trame_unix.md_content_hash, trame_windows.md_content_hash)

    def test_line_ending_normalization_old_mac(self):
        """Test that old Mac (CR) line endings produce same hash as Unix"""
        md_unix = "# Title\nContent\nMore"
        md_old_mac = "# Title\rContent\rMore"
        trame_unix = TrameBuilder.from_string("test1", md_unix)
        trame_old_mac = TrameBuilder.from_string("test2", md_old_mac)
        self.assertEqual(trame_unix.md_content_hash, trame_old_mac.md_content_hash)

    def test_line_ending_normalization_mixed(self):
        """Test that mixed line endings are normalized"""
        md_unix = "# Title\nContent\nMore\nEnd"
        md_mixed = "# Title\r\nContent\nMore\rEnd"
        trame_unix = TrameBuilder.from_string("test1", md_unix)
        trame_mixed = TrameBuilder.from_string("test2", md_mixed)
        self.assertEqual(trame_unix.md_content_hash, trame_mixed.md_content_hash)


if __name__ == "__main__":
    unittest.main()
