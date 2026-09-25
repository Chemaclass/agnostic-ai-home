# Personal defaults across projects

`AGNOSTIC_AI.md` is the canonical source for shared working agreements. `skills/` holds on-demand skills, `agents/` holds read-only subagents (`locator`, `claim-verifier`, `reviewer`), and `hooks/` holds `guard-shell`, which runs `scripts/guard-shell.py` before every shell command to block force pushes without a lease, recursive `rm` with globs, printing secret files, and em or en dashes in published text. Project-specific domain, review, testing, CI, and release policies belong in the project's `.agnostic-ai/` directory. Native instruction files are generated, and existing tool-specific configuration is preserved.

After editing the source:

```bash
./sync.sh          # write
./sync.sh --check  # verify no drift (also runs as the pre-commit hook)
```

This writes the managed instructions to `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, and `~/.cursor/AGENTS.md` (injected by a `sessionStart` hook), and emits each `skills/<name>/SKILL.md` to `~/.claude/skills/`, `~/.agents/skills/`, and `~/.cursor/skills/`. The Claude-only `@RTK.md` import remains outside the managed block. Restart an existing session to pick up changed global instructions reliably.

Model tiers: only Claude and Codex get explicit models; every other target, and every unlisted skill or agent, keeps the tool's own default. Agents pick a tier by job: `locator` is cheap (`haiku` / `gpt-6-luna`, low effort), `claim-verifier` is the workhorse (`sonnet` / `gpt-6-sol`), and `reviewer` spends more where a missed bug costs most (`opus` / `gpt-6-sol`, high effort). Skills run in the main session, so only `pr-value-audit` sets one: `model: opus`, `effort: xhigh`, which Claude applies for that turn and Codex ignores. Claude uses aliases that track the latest model; Codex slugs need a bump when OpenAI renames them.

Hook targeting: `sync --global` currently ignores `target`/`targets` on hook specs (a known agnostic-ai limitation, tracked upstream), so one Claude-style `PreToolUse` hook is emitted to all three CLIs. Cursor runs it through its third-party import of `~/.claude/settings.json` (on by default); the script also answers Cursor's native `beforeShellExecution` payload if that event is wired later.

Skills that depend on one CLI's connectors (a Notion or Slack integration, for example) stay in that CLI's own skills directory on purpose. Employer-specific notes never go in this repo: keep them in `~/.claude/skills/<name>/` and symlink that directory into `~/.agents/skills/` and `~/.cursor/skills/` so every CLI can load it. A skill directory that already exists unmanaged blocks sync with "unmanaged global skill collision"; move it into `backups/` before adopting it here.

Ownership state and migration backups are local artifacts and are ignored. The repo is pushed to a private GitHub remote as the off-machine copy. Install the drift check once per clone with `ln -sf ../../sync.sh .git/hooks/pre-commit`.
