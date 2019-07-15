import unittest

from margos.parsing import parse


class TestParse(unittest.TestCase):
    def test_header_only(self) -> None:
        state = parse("Hello world")
        self.assertEqual(state.header, "Hello world")
        self.assertEqual(len(state.menu), 0)

    def test_full(self) -> None:
        state = parse(
            """Hello world
This is line 1|attr1 = 3 | attr2 = Hello

This is line 2
And line 3"""
        )
        self.assertEqual(state.header, "Hello world")
        self.assertEqual(state.menu[0], "This is line 1")
        self.assertEqual(state.menu[1], "This is line 2")
        self.assertEqual(state.menu[2], "And line 3")


if __name__ == "__main__":
    unittest.main()
