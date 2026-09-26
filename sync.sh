#!/bin/sh
# Sync reads ~/.agnostic-ai from any directory. As pre-commit it runs --check, and only when that link points at the repo being committed.
set -e
home="$HOME/.agnostic-ai"
[ -d "$home" ] || { echo "sync.sh: $home is missing. Link it to your clone: ln -s <clone> $home" >&2; exit 1; }
if [ "$(basename "$0")" = pre-commit ]; then
  [ "$(pwd -P)" = "$(cd -P "$home" && pwd)" ] || { echo "sync.sh: $home does not point at this repo" >&2; exit 1; }
  set -- --check
fi
exec agnostic-ai sync --global --only claude,codex,cursor "$@"
