from pathlib import Path
import unittest


from trame import TrameBuilder
from trame.piece import Title, Table, Paragraph, UnorderedList, Code, YamlCode, Image, Div


class SmokeTest(unittest.TestCase):
    """Just try to build any markdown on tests/data"""

    files = [
        ("src/trame_tests/data/dummy.md", 21),
        ("src/trame_tests/data/rgpd_maths.pm.md", 52),
        ("src/trame_tests/data/sujet_0_spe_sujet_1.md", 1),
        ("src/trame_tests/data/sujet_0_spe_sujet_2.md", 1),
    ]

    def test(self):
        for file, n_pieces in self.files:
            with self.subTest(file=file):
                trame = TrameBuilder.from_file(Path(file))
                self.assertEqual(len(trame.pieces), n_pieces)

    def test_dumm(self):
        trame = TrameBuilder.from_file(Path("src/trame_tests/data/dummy.md"))
        self.assertIsInstance(trame.pieces[0], Title)
        self.assertIsInstance(trame.pieces[1], Title)
        self.assertIsInstance(trame.pieces[2], Title)
        self.assertIsInstance(trame.pieces[3], Paragraph)
        self.assertIsInstance(trame.pieces[4], UnorderedList)
        self.assertIsInstance(trame.pieces[5], Paragraph)
        self.assertIsInstance(trame.pieces[6], UnorderedList)
        self.assertIsInstance(trame.pieces[7], Code)
        self.assertIsInstance(trame.pieces[8], Code)
        self.assertIsInstance(trame.pieces[9], Code)
        self.assertIsInstance(trame.pieces[10], YamlCode)
        self.assertIsInstance(trame.pieces[11], Table)
        self.assertIsInstance(trame.pieces[12], Paragraph)
        self.assertIsInstance(trame.pieces[13], Paragraph)
        self.assertIsInstance(trame.pieces[14], Paragraph)
        self.assertIsInstance(trame.pieces[15], Paragraph)
        self.assertIsInstance(trame.pieces[16], Paragraph)
        self.assertIsInstance(trame.pieces[17], Paragraph)
        self.assertIsInstance(trame.pieces[18], Image)
        self.assertIsInstance(trame.pieces[19], Image)
        self.assertIsInstance(trame.pieces[20], Div)
        self.assertIsInstance(trame.pieces[20], Div)


if __name__ == "__main__":
    unittest.main()
