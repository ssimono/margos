import unittest

from margos.display import config_from_gsettings


class TestConfigFromGSettings(unittest.TestCase):
    def test_defaults(self) -> None:
        config = config_from_gsettings("/")
        self.assertIsNotNone(config)
        if config is not None:
            self.assertEqual(config.command, "date")
            self.assertEqual(config.interval, 1)

    def test_invalid_path(self) -> None:
        config = config_from_gsettings("/nonexistent")
        self.assertIsNone(config)


if __name__ == "__main__":
    unittest.main()
