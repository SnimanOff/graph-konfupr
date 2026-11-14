# Вариант 22: граф зависимостей Alpine (apk)

CLI на Python 3.10+. Читает YAML, скачивает APKINDEX, строит граф (BFS),
выводит порядок загрузки и диаграмму Mermaid.

Запуск: `python main.py examples/tree.yaml --mode РЕЖИМ`.

Режимы: `config`, `direct`, `graph`, `order`, `mermaid` (по умолчанию).

Тесты: `python -m unittest discover -s tests`

Настройки YAML: `package`, `repository`, `test_mode`, `version`,
`max_depth`, `exclude`.

Сравнение с apk: порядок для tree, nano, jq совпал с `apk add --simulate`.
`apk dot` подписывает рёбра виртуальными именами (`so:...`), CLI показывает
сами пакеты.
