---
name: agnostic-ai-specs
description: "Edit agnostic-ai sources, never generated files. Use when changing a `.agnostic-ai/` directory or `~/.agnostic-ai`, running `agnostic-ai sync`, or touching generated CLAUDE.md, AGENTS.md, skills, or agents."
---

# agnostic-ai specs

- Edit the canonical source, never the generated output. Native instruction files and emitted skills are overwritten on the next sync.
- Personal defaults live in `~/.agnostic-ai/`, private overrides in its gitignored `local/` (a same-name spec there merges into the shared one: write only the changed fields); each project's domain, review, testing, CI, and release policies live in its own `.agnostic-ai/`.
- Keep generated output ignored where the project uses canonical specs.
- After editing, run `agnostic-ai sync`, then `agnostic-ai sync --check`. For personal defaults, run `~/.agnostic-ai/sync.sh && ~/.agnostic-ai/sync.sh --check`; `~/.agnostic-ai` links to a git clone, so commit source edits there.
- To upgrade agnostic-ai, run `~/.agnostic-ai/scripts/upgrade-and-sync.sh` (`--dry-run` first). Report the tracked files it lists per project; never commit them for the user.
- Check both Claude Code and Codex outputs when changing shared specs. Use portable fields first and target overrides only for behavior the portable fields cannot express. Codex skills do not select a model or effort; set those on agents. `readonly` does not enforce a sandbox in current Codex agents.
- A project pinned to another release needs its `requires` and schema reconciled before sync. Review its instructions and local changes first; run `agnostic-ai upgrade --requires` only as part of an authorized project upgrade. Session hooks must report the mismatch rather than change pins.
- Verify that shared instructions remain usable after generation, including referenced files. When one body is emitted at different directory depths, use explicit repository-root paths and state that convention; a clean sync alone does not prove the references work.
- Tool-specific skills that depend on one CLI's connectors stay in that CLI's own skills directory, outside the source.
