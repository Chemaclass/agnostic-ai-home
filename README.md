# agnostic-ai home

One global setup for AI coding agents, synced to Claude Code, Codex, Cursor, and more with [agnostic-ai](https://agnostic-ai.org). See how it works on the [project page](https://chemaclass.github.io/agnostic-ai-home/).

## Install

Paste this into any coding agent:

```text
Set up https://github.com/Chemaclass/agnostic-ai-home as my global AI config. Clone it, then follow its SETUP.md step by step.
```

Or by hand:

```bash
brew install --cask Chemaclass/tap/agnostic-ai   # or: npm install -g agnostic-ai
git clone https://github.com/Chemaclass/agnostic-ai-home.git ~/Code/agnostic-ai-home
ln -s ~/Code/agnostic-ai-home ~/.agnostic-ai
~/.agnostic-ai/sync.sh
```

Restart open sessions. In Codex, run `/hooks` once and trust `guard-shell`; Codex skips untrusted hooks. Update with `git -C ~/.agnostic-ai pull && ~/.agnostic-ai/sync.sh`.

## What you get

- **Agreements** (`AGNOSTIC_AI.md`): finish the work, slice vertically, fix root causes, validate once, write plainly.
- **Skills**: `gh-issue`, `gh-issues`, `pr-value-audit`, `object-design`, `recovery-evidence`, `agnostic-ai-specs`, `i-have-adhd`.
- **Agents**: `locator` (fast and cheap), `claim-verifier` and `reviewer` (strongest model, high effort). Their instructions forbid edits. Claude Code disables its file editing tools, and Cursor gets `readonly: true`. Codex inherits the parent session's permissions.
- **Hook** `guard-shell`: blocks unleased force pushes, recursive `rm` with a glob, printing secret files, and em or en dashes in published text.

## Make it yours

Put your changes in `~/.agnostic-ai/local/`. It is gitignored but still synced, so `git pull` never conflicts.

```text
~/.agnostic-ai/local/targets              # tools to sync, e.g. claude,codex,gemini
~/.agnostic-ai/local/AGNOSTIC_AI.md       # extra agreements
~/.agnostic-ai/local/skills/<name>/       # add a skill, or edit a shared one
~/.agnostic-ai/local/agents/<name>.md     # add an agent, or edit a shared one
```

A same-name local spec merges into the shared one: write only the fields that change, and `::parent` to extend the body. Needs agnostic-ai 0.80.x, which `sync.sh` checks.

`agnostic-ai.yaml` selects Claude Code, Codex, and Cursor for a bare `agnostic-ai sync --global`. To change that list on this machine, set `targets:` in `local/agnostic-ai.yaml`. `local/targets` overrides the list only when running `sync.sh`.

Skill argument hints live under `x-claude`; skill metadata lives under `x-claude` and `x-cursor`. Manual-only skills retain their native invocation policies. Codex agent specs omit `sandbox_mode`, which current Codex ignores. For an enforced read-only Codex session, start it with `codex --sandbox read-only`.

[SETUP.md](SETUP.md) covers collisions, switching specs off, and updates.

Working on this repo? Install the pre-commit gate (guard tests, spec lint, dashes, drift): `ln -sf ../../sync.sh .git/hooks/pre-commit`. Run it anytime with `scripts/check.sh`; the `check` workflow runs it on demand in GitHub Actions.
