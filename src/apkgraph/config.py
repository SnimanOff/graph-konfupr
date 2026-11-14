import re
from dataclasses import dataclass
from pathlib import Path

KEYS = ("package", "repository", "test_mode", "version", "max_depth",
        "exclude")


@dataclass(frozen=True)
class Config:
    package: str
    repository: str
    test_mode: bool
    version: str
    max_depth: int
    exclude: str


def read_yaml(path: Path) -> dict[str, str]:
    values = {}
    for number, line in enumerate(path.read_text("utf-8").splitlines(), 1):
        line = re.sub(r"\s+#.*$", "", line).strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not sep or key not in KEYS:
            raise ValueError(f"строка {number}: неизвестный ключ {key!r}")
        if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    missing = [key for key in KEYS if key not in values]
    if missing:
        raise ValueError(f"отсутствуют параметры: {', '.join(missing)}")
    return values


def load_config(path: Path) -> Config:
    v = read_yaml(path)
    if v["test_mode"] not in ("true", "false"):
        raise ValueError("test_mode: укажите true или false")
    test = v["test_mode"] == "true"
    if not v["max_depth"].isdigit():
        raise ValueError("max_depth: укажите целое число >= 0")
    name_rule = r"[A-Z]+" if test else r"[a-z0-9][\w.+-]*"
    if not re.fullmatch(name_rule, v["package"]):
        raise ValueError(f"package: недопустимое имя {v['package']!r}")
    if not re.fullmatch(r"[0-9][\w.+-]*", v["version"]):
        raise ValueError(f"version: недопустимая версия {v['version']!r}")
    repo = v["repository"]
    if test:
        repo = str((path.parent / repo).resolve())
        if not Path(repo).is_file():
            raise ValueError(f"repository: файл не найден: {repo}")
    elif not repo.startswith(("http://", "https://")):
        raise ValueError("repository: нужен URL http(s)")
    return Config(v["package"], repo, test, v["version"],
                  int(v["max_depth"]), v["exclude"])
