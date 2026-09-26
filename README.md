# agnostic-ai home

A global setup for AI coding CLIs, written once and synced to Claude Code, Codex, Cursor, and more with [agnostic-ai](https://agnostic-ai.org).

Working agreements, skills, agents, and a safety hook. Use it as is, fork it, or take what you like.

See how it fits together on the [project page](https://chemaclass.github.io/agnostic-ai-home/). Agents can start from its [llms.txt](https://chemaclass.github.io/agnostic-ai-home/llms.txt).

## Quick start

Paste this into Claude Code, Codex, Cursor, or any coding agent:

```text
Set up https://github.com/Chemaclass/agnostic-ai-home as my global AI config. Clone it, then follow its SETUP.md step by step.
```

The agent installs agnostic-ai, links the clone, picks the tools you have, resolves conflicts with your existing skills, and verifies the sync. [SETUP.md](SETUP.md) is the full procedure.

Or by hand, on macOS or Linux:

```bash
brew install --cask Chemaclass/tap/agnostic-ai   # or: npm install -g agnostic-ai
git clone https://github.com/Chemaclass/agnostic-ai-home.git ~/Code/agnostic-ai-home
ln -s ~/Code/agnostic-ai-home ~/.agnostic-ai
~/.agnostic-ai/sync.sh
```

Restart open sessions. That syncs Claude Code, Codex, and Cursor; list other tools in `local/targets`. If sync stops on a collision with a skill you already have, [SETUP.md](SETUP.md#4-preview-and-resolve-collisions) says how to keep yours.

Update with `git -C ~/.agnostic-ai pull && ~/.agnostic-ai/sync.sh`.

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

Keep your changes in `local/`, never in tracked files. It is gitignored but still synced, so `git pull` never conflicts. A file there replaces the shared spec with the same kind and name; a new name is added.

```text
local/targets                     # tools to sync, e.g. claude,codex,gemini
local/AGNOSTIC_AI.md              # extra agreements, appended to the shared ones
local/skills/work-notes/SKILL.md  # a private skill
local/agents/reviewer.md          # replaces the shared reviewer
```

To switch off a shared skill, agent, or hook, copy it into `local/` and add `targets-exclude: [claude, codex, cursor]`. `agnostic-ai list --global` shows which layer each spec comes from. Back up `local/` somewhere private: it never leaves your machine.

Project rules belong in that project's `.agnostic-ai/`, not here. Skills tied to one CLI's connectors, like a Notion or Slack integration, can stay in that CLI's own skills folder.

Working on this repo itself? Install the drift check: `ln -sf ../../sync.sh .git/hooks/pre-commit`.
