#!/bin/sh
# Sync reads ~/.agnostic-ai from any directory. As pre-commit it runs scripts/check.sh and --check, and only when that link points at the repo being committed.
set -e
home="$HOME/.agnostic-ai"
[ -d "$home" ] || { echo "sync.sh: $home is missing. Link it to your clone: ln -s <clone> $home" >&2; exit 1; }
minimum=0.84.0
version=$(agnostic-ai --version 2>/dev/null | awk '{print $NF}')
oldest=$(printf '%s\n%s\n' "$minimum" "${version:-0}" | sort -V | head -n 1)
if [ -z "$version" ] || [ "$oldest" != "$minimum" ]; then
  echo "sync.sh: needs agnostic-ai $minimum or newer (found ${version:-none}). Run: agnostic-ai upgrade" >&2
  exit 1
fi
if [ "$(basename "$0")" = pre-commit ]; then
  [ "$(pwd -P)" = "$(cd -P "$home" && pwd)" ] || { echo "sync.sh: $home does not point at this repo" >&2; exit 1; }
  "$home/scripts/check.sh"
  set -- --check
fi
if [ -f "$home/local/targets" ]; then
  targets=$(tr -d ' \n' < "$home/local/targets")
  set -- --target "$targets" "$@"
fi
exec agnostic-ai sync --global "$@"
