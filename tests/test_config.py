from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from src.apkgraph.config import load_config

VALID = {"package": "pkg", "repository": "https://host/main/x86_64/",
         "test_mode": "false", "version": '"1.2-r0"', "max_depth": "3",
         "exclude": '""'}


class ConfigTests(TestCase):
    def load(self, **changes):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "c.yaml"
            text = "\n".join(f"{k}: {v}" for k, v in (VALID | changes).items())
            path.write_text(text, encoding="utf-8")
            return load_config(path)

    def test_valid(self):
        config = self.load(exclude="'so'  # comment")
        self.assertEqual((config.version, config.max_depth, config.exclude),
                         ("1.2-r0", 3, "so"))

    def test_bad_values(self):
        bad = {"package": "Bad Name", "repository": "ftp://x",
               "test_mode": "yes", "version": "latest", "max_depth": "-1"}
        for key, value in bad.items():
            with self.subTest(key=key), self.assertRaisesRegex(ValueError,
                                                               key):
                self.load(**{key: value})
