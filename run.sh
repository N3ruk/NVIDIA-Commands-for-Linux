#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"
if [ -x .venv/bin/python ]; then
    exec .venv/bin/python -m nvidia_commands "$@"
fi
exec /usr/bin/python3 -m nvidia_commands "$@"
