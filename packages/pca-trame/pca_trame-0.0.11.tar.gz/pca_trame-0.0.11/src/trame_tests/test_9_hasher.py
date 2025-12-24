import unittest

from trame import TrameBuilder
from trame.hasher import TrameHasher
from trame_tests import TrameTestCase


class TestTrameHasher(TrameTestCase):
    """Test suite for TrameHasher utility class"""

    def test_compute_hash_returns_string(self):
        """Test that compute_hash returns a string"""
        content = "# Test"
        hash_val = TrameHasher.compute_hash(content)
        self.assertIsInstance(hash_val, str)

    def test_compute_hash_length(self):
        """Test that compute_hash returns 64-character hash"""
        content = "# Test"
        hash_val = TrameHasher.compute_hash(content)
        self.assertEqual(len(hash_val), 64)

    def test_compute_hash_deterministic(self):
        """Test that compute_hash is deterministic"""
        content = "# Test"
        hash1 = TrameHasher.compute_hash(content)
        hash2 = TrameHasher.compute_hash(content)
        self.assertEqual(hash1, hash2)

    def test_get_short_hash_default_length(self):
        """Test that get_short_hash returns 8 characters by default"""
        full_hash = "f0e4c2f76c58916ec258f246851bea091d14d4247a2fc3e18694461b1816e13b"
        short = TrameHasher.get_short_hash(full_hash)
        self.assertEqual(len(short), 8)
        self.assertEqual(short, "f0e4c2f7")

    def test_get_short_hash_custom_length(self):
        """Test that get_short_hash respects custom length"""
        full_hash = "f0e4c2f76c58916ec258f246851bea091d14d4247a2fc3e18694461b1816e13b"
        short_12 = TrameHasher.get_short_hash(full_hash, length=12)
        self.assertEqual(len(short_12), 12)
        self.assertEqual(short_12, "f0e4c2f76c58")

    def test_get_short_hash_from_beginning(self):
        """Test that get_short_hash takes characters from the beginning"""
        full_hash = "abcdef0123456789"
        short = TrameHasher.get_short_hash(full_hash, length=6)
        self.assertEqual(short, "abcdef")

    def test_has_changed_with_different_content(self):
        """Test that has_changed returns True for different content"""
        trame1 = TrameBuilder.from_string("test1", "# Version 1")
        trame2 = TrameBuilder.from_string("test2", "# Version 2")
        self.assertTrue(TrameHasher.has_changed(trame1, trame2))

    def test_has_changed_with_same_content(self):
        """Test that has_changed returns False for same content"""
        content = "# Same content"
        trame1 = TrameBuilder.from_string("test1", content)
        trame2 = TrameBuilder.from_string("test2", content)
        self.assertFalse(TrameHasher.has_changed(trame1, trame2))

    def test_are_identical_with_same_content(self):
        """Test that are_identical returns True for same content"""
        content = "# Same content"
        trame1 = TrameBuilder.from_string("test1", content)
        trame2 = TrameBuilder.from_string("test2", content)
        self.assertTrue(TrameHasher.are_identical(trame1, trame2))

    def test_are_identical_with_different_content(self):
        """Test that are_identical returns False for different content"""
        trame1 = TrameBuilder.from_string("test1", "# Version 1")
        trame2 = TrameBuilder.from_string("test2", "# Version 2")
        self.assertFalse(TrameHasher.are_identical(trame1, trame2))

    def test_has_changed_and_are_identical_opposite(self):
        """Test that has_changed and are_identical are opposites"""
        trame1 = TrameBuilder.from_string("test1", "# Content")
        trame2 = TrameBuilder.from_string("test2", "# Content")
        trame3 = TrameBuilder.from_string("test3", "# Different")

        # Same content
        self.assertEqual(
            TrameHasher.has_changed(trame1, trame2), not TrameHasher.are_identical(trame1, trame2)
        )

        # Different content
        self.assertEqual(
            TrameHasher.has_changed(trame1, trame3), not TrameHasher.are_identical(trame1, trame3)
        )

    def test_compute_hash_matches_trame_hash(self):
        """Test that compute_hash produces same result as Trame.md_content_hash"""
        content = "# Test Content\n\nSome text here."
        trame = TrameBuilder.from_string("test", content)
        direct_hash = TrameHasher.compute_hash(content)
        self.assertEqual(trame.md_content_hash, direct_hash)

    def test_get_short_hash_with_trame_object(self):
        """Test using get_short_hash with a Trame object's hash"""
        trame = TrameBuilder.from_string("test", "# Hello")
        short = TrameHasher.get_short_hash(trame.md_content_hash)
        self.assertEqual(len(short), 8)
        self.assertTrue(trame.md_content_hash.startswith(short))


if __name__ == "__main__":
    unittest.main()
