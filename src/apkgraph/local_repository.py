import json
import re
from pathlib import Path

from .repository import Node, RepositoryError


class LocalRepository:
    def __init__(self, path: str, version: str):
        self.data = json.loads(Path(path).read_text("utf-8"))
        self.version = version
        for name, deps in self.data.items():
            for item in [name, *deps]:
                if not re.fullmatch(r"[A-Z]+", item) or item not in self.data:
                    raise RepositoryError(f"неверный пакет {item!r}")

    def root(self, package: str, version: str) -> Node:
        if package not in self.data or version != self.version:
            raise RepositoryError(f"Пакет {package}={version} не найден")
        return Node(package, version)

    def direct(self, package: str, version: str) -> list[str]:
        return self.data[self.root(package, version).name]

    def neighbors(self, node: Node) -> list[Node]:
        return [Node(name, node.version) for name in self.data[node.name]]
