#!/bin/sh
# Pre-commit runs this with no arguments, which means --check.
set -e
cd "$(dirname "$0")"
[ "$(basename "$0")" = pre-commit ] && set -- --check
exec agnostic-ai sync --global --only claude,codex,cursor "$@"
