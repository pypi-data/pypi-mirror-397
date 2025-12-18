"""
Dummy test file to ensure pytest always has at least one test to run.
"""
import unittest


class DummyTest(unittest.TestCase):
    """A dummy test class that always passes."""

    def test_dummy(self):
        """A dummy test that always passes."""
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
