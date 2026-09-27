#!/bin/sh
# Local and CI gate: guard tests, spec lint, and no em or en dashes in tracked files.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)

python3 -m unittest discover -s "$root/tests"

tmp=$(mktemp -d)
case "$tmp" in /tmp/*|/var/folders/*|/private/*|"${TMPDIR:-/nonexistent}"*) ;; *) echo "check.sh: unexpected temp dir $tmp" >&2; exit 1 ;; esac
trap 'rm -r "$tmp"' EXIT
mkdir "$tmp/.agnostic-ai"
cp -R "$root/agents" "$root/skills" "$root/hooks" "$root/scripts" "$root/AGNOSTIC_AI.md" "$tmp/.agnostic-ai/"
printf 'targets: [claude, codex, cursor]\n' > "$tmp/agnostic-ai.yaml"
(cd "$tmp" && agnostic-ai lint --strict && agnostic-ai validate)

if git -C "$root" grep -n -I -e "$(printf '\342\200\224')" -e "$(printf '\342\200\223')" -- .; then
  echo "check.sh: em or en dash found" >&2
  exit 1
fi
echo "check.sh: ok"
