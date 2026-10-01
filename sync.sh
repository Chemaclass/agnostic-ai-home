#!/bin/sh
# Sync reads ~/.agnostic-ai from any directory. As pre-commit it runs scripts/check.sh and --check, and only when that link points at the repo being committed.
set -e
home="$HOME/.agnostic-ai"
[ -d "$home" ] || { echo "sync.sh: $home is missing. Link it to your clone: ln -s <clone> $home" >&2; exit 1; }
series=0.76
version=$(agnostic-ai --version 2>/dev/null | awk '{print $NF}')
case "$version" in
  "$series".*) ;;
  *) echo "sync.sh: needs agnostic-ai $series.x (found ${version:-none}). Run: agnostic-ai upgrade --version v$series.0" >&2; exit 1 ;;
esac
targets=claude,codex,cursor
[ -f "$home/local/targets" ] && targets=$(tr -d ' \n' < "$home/local/targets")
if [ "$(basename "$0")" = pre-commit ]; then
  [ "$(pwd -P)" = "$(cd -P "$home" && pwd)" ] || { echo "sync.sh: $home does not point at this repo" >&2; exit 1; }
  "$home/scripts/check.sh"
  set -- --check
fi
exec agnostic-ai sync --global --only "$targets" "$@"
