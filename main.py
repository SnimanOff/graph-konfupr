import argparse
import sys
from dataclasses import asdict
from pathlib import Path

from src.apkgraph.config import load_config
from src.apkgraph.graph import build_graph, label, load_order, to_mermaid
from src.apkgraph.local_repository import LocalRepository
from src.apkgraph.repository import AlpineRepository

MODES = ("config", "direct", "graph", "order", "mermaid")


def run(config, mode: str) -> None:
    if mode == "config":
        for key, value in asdict(config).items():
            print(f"{key}={value}")
        return
    if config.test_mode:
        repo = LocalRepository(config.repository, config.version)
    else:
        repo = AlpineRepository(config.repository)
    if mode == "direct":
        print("\n".join(repo.direct(config.package, config.version)))
        return
    root = repo.root(config.package, config.version)
    graph = build_graph(root, repo.neighbors, config.max_depth,
                        config.exclude)
    if mode == "graph":
        for node, deps in graph.items():
            print(f"{label(node)}: {', '.join(map(label, deps)) or '-'}")
    elif mode == "order":
        print(" -> ".join(map(label, load_order(graph))))
    else:
        print(to_mermaid(graph), end="")


def main() -> int:
    parser = argparse.ArgumentParser(description="Граф зависимостей APK")
    parser.add_argument("config", type=Path, help="путь к YAML")
    parser.add_argument("--mode", choices=MODES, default="mermaid")
    args = parser.parse_args()
    try:
        run(load_config(args.config), args.mode)
    except (OSError, ValueError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
