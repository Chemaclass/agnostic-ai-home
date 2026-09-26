# agnostic-ai home

A global setup for AI coding CLIs, written once and synced to Claude Code, Codex, and Cursor with [agnostic-ai](https://agnostic-ai.org).

Working agreements, skills, agents, and a safety hook. Use it as is, fork it, or take what you like.

## Quick start

1. [Install agnostic-ai](https://agnostic-ai.org/docs/installation/).
2. Clone this repo anywhere and link it to `~/.agnostic-ai`:

   ```bash
   git clone https://github.com/Chemaclass/agnostic-ai-home.git ~/Code/agnostic-ai-home
   ln -s ~/Code/agnostic-ai-home ~/.agnostic-ai
   ```

   Sync reads `~/.agnostic-ai`, and the hook runs from `~/.agnostic-ai/scripts/`. Edit and commit in your clone. Changes go live on the next sync.
3. List the CLIs you use in `sync.sh`.
4. Sync and install the drift check:

   ```bash
   ./sync.sh && ./sync.sh --check
   ln -sf ../../sync.sh .git/hooks/pre-commit
   ```

5. Restart open sessions.

Sync writes a managed block into `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, and `~/.cursor/AGENTS.md`, plus real files into each tool's skills, agents, and hooks folders. Text outside the managed block stays yours. If a skill folder with the same name already exists, sync stops with "unmanaged global skill collision": move the old one aside and sync again.

## What you get

```text
~/.agnostic-ai/
├── AGNOSTIC_AI.md   # agreements, loaded in every session
├── skills/          # loaded when the task matches
├── agents/          # read-only subagents
├── hooks/           # checks before shell commands
├── scripts/         # code the hooks run
├── local/           # private overrides, gitignored
└── sync.sh          # sync, or check with --check
```

**Agreements.** Finish authorized work. Slice features vertically. Validate once per change, not per edit. Keep secrets out of output. Write plainly. Comment code rarely. Short on purpose: every session pays for it.

**Skills.**

| Skill | Use it to |
|---|---|
| `gh-issue` | take one GitHub issue to a PR |
| `gh-issues` | work the ready queue, one PR per issue (manual only) |
| `pr-value-audit` | decide if a PR should exist, and cut what does not earn its place (manual only) |
| `object-design` | move decisions into the objects that own the data |
| `recovery-evidence` | prove a backup actually restores |
| `agnostic-ai-specs` | edit agnostic-ai sources without touching generated files |
| `i-have-adhd` | get output shaped for acting, not reading (manual only) |

**Agents.** All read-only, each with its own model for Claude and Codex.

| Agent | Job | Model |
|---|---|---|
| `locator` | find code, return `file:line` | cheap |
| `claim-verifier` | prove or refute a claim with evidence | mid |
| `reviewer` | report defects, one line each | strong |

**Hook.** `guard-shell` (`PreToolUse` for Claude and Codex, `beforeShellExecution` for Cursor) blocks force pushes without `--force-with-lease`, recursive `rm` with a glob, printing secret files like `.env`, and em or en dashes in commit messages and `gh` text.

## Make it yours

Start with `AGNOSTIC_AI.md`: rewrite anything you disagree with, then delete the skills, agents, or hook checks you will not use.

For things that should not be public, use `local/`. It is gitignored but still synced. A file there replaces the shared spec with the same kind and name; new names are added.

```text
local/AGNOSTIC_AI.md              # extra agreements, appended to the managed block
local/skills/work-notes/SKILL.md  # a private skill
local/agents/reviewer.md          # replaces the shared reviewer
local/hooks/my-guard.yaml         # a private hook
```

`agnostic-ai list --global` shows which layer each spec comes from. Local files never leave your machine, so back them up somewhere private.

Project rules belong in that project's `.agnostic-ai/`, not here. Skills tied to one CLI's connectors, like a Notion or Slack integration, can stay in that CLI's own skills folder.
