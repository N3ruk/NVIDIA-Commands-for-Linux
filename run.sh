#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"
if [ -x .venv/bin/python ]; then
    exec .venv/bin/python -m dlss_studio "$@"
fi
exec /usr/bin/python3 -m dlss_studio "$@"
