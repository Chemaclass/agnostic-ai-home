#!/bin/sh
# Sync reads ~/.agnostic-ai from any directory. As pre-commit it runs scripts/check.sh and --check, and only when that link points at the repo being committed.
set -e
home="$HOME/.agnostic-ai"
[ -d "$home" ] || { echo "sync.sh: $home is missing. Link it to your clone: ln -s <clone> $home" >&2; exit 1; }
minimum=0.90.0
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
# Every tool loads AGNOSTIC_AI.md, so stop a write that would ship an
# uncommitted change removing most of it, such as a prompt pasted over it.
case " $* " in *" --plan "*|*" --check "*|*" --dry-run "*) ;; *)
  if [ -z "${AGNOSTIC_AI_SYNC_ANYWAY:-}" ] && git -C "$home" rev-parse --verify -q HEAD:AGNOSTIC_AI.md >/dev/null 2>&1; then
    committed=$(git -C "$home" show HEAD:AGNOSTIC_AI.md | wc -l | tr -d ' ')
    removed=$(git -C "$home" diff --numstat HEAD -- AGNOSTIC_AI.md | awk '{print $2}')
    if [ "${removed:-0}" -gt 0 ] && [ $((removed * 2)) -gt "$committed" ]; then
      echo "sync.sh: $home/AGNOSTIC_AI.md has an uncommitted change that removes $removed of its $committed committed lines, and every tool would load it." >&2
      echo "Review it with: git -C $home diff AGNOSTIC_AI.md. Restore it with git restore, commit it, or rerun with AGNOSTIC_AI_SYNC_ANYWAY=1." >&2
      exit 1
    fi
  fi
esac
if [ -f "$home/local/targets" ]; then
  targets=$(tr -d ' \n' < "$home/local/targets")
  set -- --target "$targets" "$@"
fi
exec agnostic-ai sync --global "$@"
