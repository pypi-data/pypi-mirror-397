"""
Hash utilities for Trame content tracking.
"""

import hashlib


class TrameHasher:
    """Utility class for hash operations on Trame objects"""

    @staticmethod
    def compute_hash(markdown_content: str) -> str:
        """
        Compute SHA-256 hash of markdown content.

        Args:
            markdown_content: Raw markdown text

        Returns:
            64-character hexadecimal hash string
        """
        # Normalize line endings for cross-platform consistency
        content = markdown_content.replace("\r\n", "\n").replace("\r", "\n")
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def get_short_hash(hash_value: str, length: int = 8) -> str:
        """
        Get shortened hash for display.

        Args:
            hash_value: Full 64-character hash
            length: Number of characters to return (default: 8)

        Returns:
            Shortened hash string

        Example:
            >>> full_hash = "f0e4c2f76c58916e..."
            >>> TrameHasher.get_short_hash(full_hash)
            'f0e4c2f7'
        """
        return hash_value[:length]

    @staticmethod
    def has_changed(trame1, trame2) -> bool:
        """
        Check if content has changed between two Trame objects.

        Args:
            trame1: First Trame object
            trame2: Second Trame object

        Returns:
            True if content changed, False otherwise

        Example:
            >>> trame1 = TrameBuilder.from_string("test", "# V1")
            >>> trame2 = TrameBuilder.from_string("test", "# V2")
            >>> TrameHasher.has_changed(trame1, trame2)
            True
        """
        return trame1.md_content_hash != trame2.md_content_hash

    @staticmethod
    def are_identical(trame1, trame2) -> bool:
        """
        Check if two Trame objects have identical content.

        Args:
            trame1: First Trame object
            trame2: Second Trame object

        Returns:
            True if content identical, False otherwise
        """
        return trame1.md_content_hash == trame2.md_content_hash


# Example usage
if __name__ == "__main__":
    print("TrameHasher - Example Usage")
    print("=" * 50)

    # Example 1: Compute hash directly
    content = "# Hello World"
    hash_val = TrameHasher.compute_hash(content)
    print(f"\nContent: {repr(content)}")
    print(f"Hash: {hash_val}")

    # Example 2: Get short hash
    short = TrameHasher.get_short_hash(hash_val)
    print(f"Short hash (8 chars): {short}")

    short_12 = TrameHasher.get_short_hash(hash_val, length=12)
    print(f"Short hash (12 chars): {short_12}")
