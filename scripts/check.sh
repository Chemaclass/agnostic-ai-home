#!/bin/sh
# Local and CI gate: guard tests, spec lint, and no em or en dashes in tracked files.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)

python3 -m unittest discover -s "$root/tests"

AGNOSTIC_AI_HOME="$root" agnostic-ai lint --global --strict
AGNOSTIC_AI_HOME="$root" agnostic-ai validate --global

if git -C "$root" grep -n -I -e "$(printf '\342\200\224')" -e "$(printf '\342\200\223')" -- .; then
  echo "check.sh: em or en dash found" >&2
  exit 1
fi
echo "check.sh: ok"
