import re
from dataclasses import dataclass
from pathlib import Path

KEYS = ("package", "repository", "test_mode", "version", "max_depth",
        "exclude")
REAL_NAME = r"[a-z0-9][\w.+-]*"
TEST_NAME = r"[A-Z]+"
VERSION = r"[0-9][\w.+-]*"


@dataclass(frozen=True)
class Config:
    package: str
    repository: str
    test_mode: bool
    version: str
    max_depth: int
    exclude: str


def unquote(value: str) -> str:
    match = re.fullmatch(r"(['\"])(.*)\1", value)
    return match.group(2) if match else value


def parse_line(number: int, line: str):
    line = re.sub(r"(^|\s+)#.*$", "", line).strip()
    if not line:
        return None
    key, sep, value = line.partition(":")
    key = key.strip()
    if not sep or key not in KEYS:
        raise ValueError(f"строка {number}: неизвестный ключ {key!r}")
    return key, unquote(value.strip())


def read_yaml(path: Path) -> dict[str, str]:
    lines = path.read_text("utf-8").splitlines()
    pairs = (parse_line(n, line) for n, line in enumerate(lines, 1))
    values = dict(pair for pair in pairs if pair)
    missing = [key for key in KEYS if key not in values]
    if missing:
        raise ValueError(f"отсутствуют параметры: {', '.join(missing)}")
    return values


def parse_test_mode(value: str) -> bool:
    if value not in ("true", "false"):
        raise ValueError("test_mode: укажите true или false")
    return value == "true"


def parse_depth(value: str) -> int:
    if not value.isdigit():
        raise ValueError("max_depth: укажите целое число >= 0")
    return int(value)


def check_match(key: str, rule: str, value: str) -> str:
    if not re.fullmatch(rule, value):
        raise ValueError(f"{key}: недопустимое значение {value!r}")
    return value


def resolve_repository(path: Path, repo: str, test: bool) -> str:
    if not test:
        if not repo.startswith(("http://", "https://")):
            raise ValueError("repository: нужен URL http(s)")
        return repo
    full = (path.parent / repo).resolve()
    if not full.is_file():
        raise ValueError(f"repository: файл не найден: {full}")
    return str(full)


def load_config(path: Path) -> Config:
    v = read_yaml(path)
    test = parse_test_mode(v["test_mode"])
    depth = parse_depth(v["max_depth"])
    package = check_match("package", TEST_NAME if test else REAL_NAME,
                          v["package"])
    version = check_match("version", VERSION, v["version"])
    repo = resolve_repository(path, v["repository"], test)
    return Config(package, repo, test, version, depth, v["exclude"])
