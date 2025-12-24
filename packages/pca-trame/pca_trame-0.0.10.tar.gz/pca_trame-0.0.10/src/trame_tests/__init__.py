import unittest


class TrameTestCase(unittest.TestCase):
    def assertDictStructureMatches(self, actual, expected):
        """
        Compare dict structure where expected can use:
        - ...: accept any value (Ellipsis)
        - set: compare keys only
        - dict: recurse
        """
        if expected is Ellipsis:
            return
        elif type(actual) is not type(expected):
            self.fail()
        elif isinstance(expected, dict) and isinstance(actual, dict):
            self.assertEqual(set(expected.keys()), set(actual.keys()))
            for key, val in expected.items():
                self.assertDictStructureMatches(actual[key], val)
        elif isinstance(expected, str) and isinstance(actual, str):
            self.assertEqual(actual, expected)
        else:
            raise NotImplementedError(f"{type(actual)}, {type(expected)}")

    def assertAllLeafValuesType(self, obj, expected_type, path=""):
        """Assert all leaf values are of expected type"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else str(key)
                self.assertAllLeafValuesType(value, expected_type, current_path)

        elif isinstance(obj, (list, tuple)):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                self.assertAllLeafValuesType(item, expected_type, current_path)

        else:
            # Valeur terminale
            self.assertIsInstance(
                obj,
                expected_type,
                f"At {path or 'root'}: expected {expected_type.__name__}, got {type(obj).__name__}",
            )
