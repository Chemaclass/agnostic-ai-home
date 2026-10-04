#!/bin/sh
# Reaps what agent tooling leaves behind once the directory it served is gone:
# a detached Codex review broker (and its app-server, code-mode host and MCP
# children) outlives the git worktree it was started in, and its state dir in
# $TMPDIR outlives the broker. Nothing here touches a process whose working
# directory still exists.
#
# Usage: reap-stale-agents.sh [--dry-run]
set -eu

dry_run=0
[ "${1:-}" = "--dry-run" ] && dry_run=1

say() { printf '%s %s\n' "$(date '+%Y-%m-%dT%H:%M:%S')" "$*"; }

kill_tree() {
    for child in $(pgrep -P "$1" 2>/dev/null || true); do
        kill_tree "$child"
    done
    [ "$dry_run" -eq 1 ] || kill "$1" 2>/dev/null || true
}

# The directory a process runs in, from lsof (macOS has no /proc).
process_cwd() {
    lsof -a -p "$1" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -n 1
}

reaped=0

# 1. Codex brokers whose --cwd no longer exists.
for pid in $(pgrep -f 'app-server-broker.mjs serve' 2>/dev/null || true); do
    cwd=$(ps -o command= -p "$pid" 2>/dev/null | sed -n 's/.*--cwd \([^ ]*\).*/\1/p')
    if [ -n "$cwd" ] && [ ! -d "$cwd" ]; then
        kill_tree "$pid"
        say "broker $pid ($cwd)"
        reaped=$((reaped + 1))
    fi
done

# 2. Orphans (parent is launchd) of the same tool family whose cwd is gone.
for pid in $(pgrep -f 'codex app-server|codex-code-mode-host|playwright.*mcp|mcp-server-playwright' 2>/dev/null || true); do
    [ "$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')" = "1" ] || continue
    cwd=$(process_cwd "$pid")
    if [ -n "$cwd" ] && [ ! -d "$cwd" ]; then
        kill_tree "$pid"
        say "orphan $pid ($cwd): $(ps -o command= -p "$pid" 2>/dev/null | cut -c1-80)"
        reaped=$((reaped + 1))
    fi
done

# 3. Broker state dirs whose broker is dead, older than an hour so a broker
#    that is still starting up keeps its dir.
# launchd may not set TMPDIR; the brokers use the per-user temp dir.
tmp_root=${TMPDIR:-$(getconf DARWIN_USER_TEMP_DIR 2>/dev/null || echo /tmp)}
tmp_root=${tmp_root%/}
case "$tmp_root" in
    /tmp*|/private/*|/var/folders/*) ;;
    *) say "unexpected TMPDIR $tmp_root, skipping state dirs"; tmp_root= ;;
esac
if [ -n "$tmp_root" ]; then
    for dir in $(find "$tmp_root" -maxdepth 1 -type d -name 'cxc-*' -mmin +60 2>/dev/null); do
        pid=$(cat "$dir/broker.pid" 2>/dev/null || true)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            continue
        fi
        [ "$dry_run" -eq 1 ] || rm -r "$dir"
        reaped=$((reaped + 1))
    done
fi

if [ "$dry_run" -eq 1 ]; then
    say "dry run: $reaped to reap"
else
    say "reaped $reaped"
fi
