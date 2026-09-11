# Personal defaults across projects

`AGNOSTIC_AI.md` is the canonical source for shared working agreements. Project-specific domain rules belong in the project's `.agnostic-ai/` directory. Native instruction files are generated, and existing tool-specific configuration is preserved.

After editing the source:

```bash
agnostic-ai sync --global --only claude,codex
agnostic-ai sync --global --only claude,codex --check
```

This writes the managed block in `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`. The Claude-only `@RTK.md` import remains outside that block. Restart an existing session to pick up changed global instructions reliably.

Ownership state and migration backups are local artifacts and are ignored. This directory has local Git history; no remote is configured and no personal configuration is published. Add a private backup destination separately if cross-machine distribution is needed.
