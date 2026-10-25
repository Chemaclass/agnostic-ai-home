#!/bin/sh
# Re-sync the global setup and every project after an agnostic-ai upgrade.
#   upgrade-and-sync.sh [--dry-run] [--no-upgrade]  upgrade, then sync the global setup and each project found under the project roots
#   upgrade-and-sync.sh --session-start             hook: sync the global setup and the current project once per installed version
# Never commits. Outputs edited by hand stay in place (sync --keep-edits). Tracked files a sync changes are listed, not committed.
home="$HOME/.agnostic-ai"
stamps="$home/state/synced-versions"
# Project roots: $AGNOSTIC_AI_PROJECTS (colon-separated), else one path per line in local/project-roots, else ~/Code.
roots=${AGNOSTIC_AI_PROJECTS:-$(sed "s|^~|$HOME|" "$home/local/project-roots" 2>/dev/null | grep -v '^#' | paste -s -d : -)}
roots=${roots:-$HOME/Code}

installed_version() {
  agnostic-ai --version 2>/dev/null | awk '{print $NF}'
}

stamp_file() {
  printf '%s/%s' "$stamps" "$(printf '%s' "$1" | cksum | awk '{print $1}')"
}

stamped() {
  [ "$(cat "$(stamp_file "$1")" 2>/dev/null)" = "$(printf '%s\n%s' "$version" "$1")" ]
}

stamp() {
  target=$(stamp_file "$1")
  mkdir -p "$stamps" && printf '%s\n%s\n' "$version" "$1" > "$target.$$" && mv -f "$target.$$" "$target"
}

first_error() {
  printf '%s\n' "$1" | grep -m 1 -E 'AAI-|error|Error|needs agnostic-ai' || printf '%s\n' "$1" | tail -n 1
}

# Main checkouts with agnostic-ai.yaml at the root. Skips worktrees (a sync there would leave outputs in a feature branch), this home repo, and the agnostic-ai source repo (it syncs with `go run`).
is_project() {
  [ -f "$1/agnostic-ai.yaml" ] && [ -d "$1/.git" ] || return 1
  [ "$(cd -P "$1" && pwd)" != "$(cd -P "$home" 2>/dev/null && pwd)" ] || return 1
  [ ! -d "$1/cmd/agnostic-ai" ]
}

dirty_paths() {
  git -C "$1" status --porcelain --untracked-files=all 2>/dev/null | cut -c 4- | sort
}

# Reads paths on stdin and prints "<content hash> <path>", so a rewrite of an already dirty file shows up.
fingerprints() {
  while IFS= read -r path; do
    [ -n "$path" ] || continue
    printf '%s %s\n' "$(git -C "$1" hash-object -- "$path" 2>/dev/null || echo -)" "$path"
  done
}

without() {
  if [ -n "$1" ]; then grep -v -x -F "$1"; else cat; fi
}

# Sets $status for the project; returns non-zero when the sync failed.
sync_project() {
  dir=$1
  if out=$(cd "$dir" && agnostic-ai sync --check 2>&1); then
    status="up to date"
    return 0
  fi
  if [ "$dry_run" = 1 ]; then
    case "$out" in *AAI-*) status="failed: $(first_error "$out")"; return 1 ;; esac
    status="would sync"
    return 0
  fi
  before=$(dirty_paths "$dir")
  before_prints=$(printf '%s\n' "$before" | fingerprints "$dir")
  if ! out=$(cd "$dir" && agnostic-ai sync --keep-edits 2>&1); then
    status="failed: $(first_error "$out")"
    return 1
  fi
  added=$(dirty_paths "$dir" | without "$before")
  rewritten=$(printf '%s\n' "$before" | fingerprints "$dir" | without "$before_prints" | cut -d ' ' -f 2-)
  changed=$(printf '%s\n%s\n' "$added" "$rewritten" | grep -v '^$' | sort -u | paste -s -d ' ' -)
  kept=$(printf '%s\n' "$out" | sed -n 's/^  ~ kept \([^ ]*\) (edited.*/\1/p' | paste -s -d ' ' -)
  status="synced"
  [ -z "$changed" ] || status="files changed, left uncommitted: $changed"
  [ -z "$kept" ] || status="$status; kept hand edits: $kept"
  leftovers=$(printf '%s\n' "$out" | grep -c -E '^  ~ kept (orphan|leftover) ')
  [ "$leftovers" = 0 ] || status="$status; kept $leftovers leftover files (see agnostic-ai doctor)"
  return 0
}

sync_global() {
  if out=$("$home/sync.sh" --check 2>&1); then
    status="up to date"
    return 0
  fi
  if [ "$dry_run" = 1 ]; then
    case "$out" in *"needs agnostic-ai"*|*AAI-*) status="failed: $(first_error "$out")"; return 1 ;; esac
    status="would sync"
    return 0
  fi
  if out=$("$home/sync.sh" 2>&1); then
    status="synced"
    return 0
  fi
  status="failed: $(first_error "$out")"
  return 1
}

session_start() {
  version=$(installed_version)
  [ -n "$version" ] && [ -d "$home" ] || return 0
  lock="$stamps/.lock"
  mkdir -p "$stamps" || return 0
  [ -z "$(find "$lock" -maxdepth 0 -mmin +10 2>/dev/null)" ] || rmdir "$lock" 2>/dev/null
  mkdir "$lock" 2>/dev/null || return 0
  trap 'rmdir "$lock" 2>/dev/null' EXIT INT TERM
  report=""
  if ! stamped global; then
    if sync_global; then stamp global; else report="global setup $status"; fi
  fi
  top=$(git -C "${CLAUDE_PROJECT_DIR:-$PWD}" rev-parse --show-toplevel 2>/dev/null) || top=""
  if [ -n "$top" ] && is_project "$top" && ! stamped "$top"; then
    if sync_project "$top"; then
      stamp "$top"
      case "$status" in "up to date"|synced) ;; *) report="$report${report:+; }this project: $status" ;; esac
    else
      report="$report${report:+; }this project: $status"
    fi
  fi
  [ -z "$report" ] || echo "agnostic-ai $version re-sync: $report"
}

sync_everything() {
  if [ "$upgrade" = 1 ] && [ "$dry_run" = 0 ]; then
    agnostic-ai upgrade || { echo "upgrade-and-sync: agnostic-ai upgrade failed" >&2; return 1; }
  fi
  version=$(installed_version)
  [ -n "$version" ] || { echo "upgrade-and-sync: agnostic-ai not found" >&2; return 1; }
  echo "agnostic-ai $version"
  failures=0
  if sync_global; then [ "$dry_run" = 1 ] || stamp global; else failures=$((failures + 1)); fi
  printf '  %-34s %s\n' "global setup" "$status"
  old_ifs=$IFS
  IFS=:
  for root in $roots; do
    IFS=$old_ifs
    configs=$(find "$root" -mindepth 1 -maxdepth 3 -name agnostic-ai.yaml -not -path '*/node_modules/*' -not -path '*/.agnostic-ai/*' 2>/dev/null | sort)
    while IFS= read -r config; do
      [ -n "$config" ] || continue
      dir=$(dirname "$config")
      case "$(basename "$dir")" in *-wt-*) continue ;; esac
      is_project "$dir" || continue
      if sync_project "$dir"; then [ "$dry_run" = 1 ] || stamp "$dir"; else failures=$((failures + 1)); fi
      printf '  %-34s %s\n' "${dir#"$root"/}" "$status"
    done <<EOF
$configs
EOF
  done
  IFS=$old_ifs
  [ "$failures" = 0 ]
}

dry_run=0
upgrade=1
mode=all
for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    --no-upgrade) upgrade=0 ;;
    --session-start) mode=hook ;;
    -h|--help) sed -n '2,5p' "$0" | cut -c 3-; exit 0 ;;
    *) echo "upgrade-and-sync: unknown argument $arg" >&2; exit 2 ;;
  esac
done

if [ "$mode" = hook ]; then
  session_start
  exit 0
fi
sync_everything
