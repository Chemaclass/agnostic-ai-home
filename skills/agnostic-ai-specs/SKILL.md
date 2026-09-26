---
name: agnostic-ai-specs
description: "Conventions for editing agnostic-ai sources and their generated agent files. Use when changing a `.agnostic-ai/` directory (project or `~/.agnostic-ai`), running `agnostic-ai sync`, or touching generated instruction files such as CLAUDE.md, AGENTS.md, `.cursor/`, or emitted skills."
---

# agnostic-ai specs

- Edit the canonical source, never the generated output. Native instruction files and emitted skills are overwritten on the next sync.
- Personal defaults live in `~/.agnostic-ai/`, private overrides in its gitignored `local/`; each project's domain, review, testing, CI, and release policies live in its own `.agnostic-ai/`.
- Keep generated output ignored where the project uses canonical specs.
- After editing, run `agnostic-ai sync`, then `agnostic-ai sync --check`. For personal defaults, run `~/.agnostic-ai/sync.sh && ~/.agnostic-ai/sync.sh --check`; `~/.agnostic-ai` links to a git clone, so commit source edits there.
- Verify that shared instructions remain usable after generation, including referenced files. When one body is emitted at different directory depths, use explicit repository-root paths and state that convention; a clean sync alone does not prove the references work.
- Tool-specific skills that depend on one CLI's connectors stay in that CLI's own skills directory, outside the source.
