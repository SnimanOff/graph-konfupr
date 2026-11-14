#!/bin/sh
cd "$(dirname "$0")" || exit 1
PYTHON=python3
"$PYTHON" -c "" >/dev/null 2>&1 || PYTHON=python
exec "$PYTHON" main.py "$@"
