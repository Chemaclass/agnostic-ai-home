# Personal defaults across projects

`AGNOSTIC_AI.md` is the canonical source for shared working agreements, and `skills/` holds the shared skills. Project-specific domain, review, testing, CI, and release policies belong in the project's `.agnostic-ai/` directory. Native instruction files are generated, and existing tool-specific configuration is preserved.

After editing the source:

```bash
./sync.sh          # write
./sync.sh --check  # verify no drift (also runs as the pre-commit hook)
```

This writes the managed instructions to `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, and `~/.cursor/AGENTS.md` (injected by a `sessionStart` hook), and emits each `skills/<name>/SKILL.md` to `~/.claude/skills/`, `~/.agents/skills/`, and `~/.cursor/skills/`. The Claude-only `@RTK.md` import remains outside the managed block. Restart an existing session to pick up changed global instructions reliably.

Skills that depend on one CLI's connectors (for example `notion-work`, `perso_slack-me`, `incident`) stay in that CLI's own skills directory on purpose. Employer-specific notes never go in this repo: keep them in `~/.claude/skills/<name>/` and symlink that directory into `~/.agents/skills/` and `~/.cursor/skills/` so every CLI can load it. A skill directory that already exists unmanaged blocks sync with "unmanaged global skill collision"; move it into `backups/` before adopting it here.

Ownership state and migration backups are local artifacts and are ignored. The repo is pushed to a private GitHub remote as the off-machine copy. Install the drift check once per clone with `ln -sf ../../sync.sh .git/hooks/pre-commit`.
