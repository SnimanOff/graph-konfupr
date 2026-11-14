import io
import tarfile
from typing import NamedTuple
from urllib.request import urlopen


class RepositoryError(ValueError):
    pass


class Node(NamedTuple):
    name: str
    version: str


def dep_name(raw: str) -> str:
    for sign in "<>=~":
        raw = raw.split(sign, 1)[0]
    return raw


def download_index(url: str) -> str:
    if not url.endswith("APKINDEX.tar.gz"):
        url = url.rstrip("/") + "/APKINDEX.tar.gz"
    try:
        with urlopen(url, timeout=20) as response:
            body = response.read()
        with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as archive:
            data = archive.extractfile("APKINDEX").read()
    except (OSError, tarfile.TarError, KeyError) as exc:
        raise RepositoryError(f"Не удалось прочитать {url}: {exc}") from exc
    return data.decode("utf-8", errors="replace")


def parse_index(text: str) -> list[dict[str, str]]:
    records = []
    for block in text.split("\n\n"):
        fields = dict(line.split(":", 1) for line in block.splitlines()
                      if len(line) > 1 and line[1] == ":")
        if "P" in fields and "V" in fields:
            records.append(fields)
    if not records:
        raise RepositoryError("В APKINDEX нет записей пакетов")
    return records


class AlpineRepository:
    def __init__(self, url: str):
        self.deps: dict[Node, list[str]] = {}
        self.providers: dict[str, list[Node]] = {}
        for rec in parse_index(download_index(url)):
            node = Node(rec["P"], rec["V"])
            self.deps[node] = rec.get("D", "").split()
            for name in [node.name, *rec.get("p", "").split()]:
                self.providers.setdefault(dep_name(name), []).append(node)

    def root(self, package: str, version: str) -> Node:
        node = Node(package, version)
        if node not in self.deps:
            found = [n.version for n in self.providers.get(package, [])
                     if n.name == package]
            raise RepositoryError(
                f"Пакет {package}={version} не найден. "
                f"Есть версии: {', '.join(found) or 'нет'}")
        return node

    def direct(self, package: str, version: str) -> list[str]:
        return self.deps[self.root(package, version)]

    def resolve(self, raw: str) -> Node:
        candidates = self.providers.get(dep_name(raw))
        if not candidates:
            raise RepositoryError(f"Нет пакета для зависимости {raw}")
        return candidates[0]

    def neighbors(self, node: Node) -> list[Node]:
        result = []
        for raw in self.deps[node]:
            if not raw.startswith("!"):
                dep = self.resolve(raw)
                if dep not in result:
                    result.append(dep)
        return result
