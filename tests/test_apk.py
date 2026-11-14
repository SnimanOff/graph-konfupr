import io
import tarfile
from unittest import TestCase
from unittest.mock import patch

from src.apkgraph.repository import AlpineRepository, Node, RepositoryError

INDEX = b"P:app\nV:1.0-r0\nD:so:libx.so.1 lib>=2.0 !old\n\n" \
        b"P:lib\nV:2.0-r0\np:so:libx.so.1\n"


def archive() -> bytes:
    body = io.BytesIO()
    with tarfile.open(fileobj=body, mode="w:gz") as tar:
        info = tarfile.TarInfo("APKINDEX")
        info.size = len(INDEX)
        tar.addfile(info, io.BytesIO(INDEX))
    return body.getvalue()


def make_repo() -> AlpineRepository:
    with patch("src.apkgraph.repository.urlopen",
               return_value=io.BytesIO(archive())):
        return AlpineRepository("https://host/main/x86_64")


class ApkTests(TestCase):
    def test_direct_and_neighbors(self):
        repo = make_repo()
        self.assertEqual(repo.direct("app", "1.0-r0"),
                         ["so:libx.so.1", "lib>=2.0", "!old"])
        node = repo.root("app", "1.0-r0")
        self.assertEqual(repo.neighbors(node), [Node("lib", "2.0-r0")])

    def test_wrong_version(self):
        with self.assertRaisesRegex(RepositoryError, "1.0-r0"):
            make_repo().root("app", "9.9")
