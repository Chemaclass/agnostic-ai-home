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

Restart open sessions. Update with `git -C ~/.agnostic-ai pull && ~/.agnostic-ai/sync.sh`.

## What you get

- **Agreements** (`AGNOSTIC_AI.md`): finish the work, slice vertically, validate once, write plainly.
- **Skills**: `gh-issue`, `gh-issues`, `pr-value-audit`, `object-design`, `recovery-evidence`, `agnostic-ai-specs`, `i-have-adhd`.
- **Agents**, all read-only: `locator` (cheap), `claim-verifier` (mid), `reviewer` (strong).
- **Hook** `guard-shell`: blocks unleased force pushes, recursive `rm` with a glob, printing secret files, and em or en dashes in published text.

## Make it yours

Put your changes in `~/.agnostic-ai/local/`. It is gitignored but still synced, so `git pull` never conflicts.

```text
~/.agnostic-ai/local/targets              # tools to sync, e.g. claude,codex,gemini
~/.agnostic-ai/local/AGNOSTIC_AI.md       # extra agreements
~/.agnostic-ai/local/skills/<name>/       # add a skill, or edit a shared one
~/.agnostic-ai/local/agents/<name>.md     # add an agent, or edit a shared one
```

A same-name local spec merges into the shared one: write only the fields that change, and `::parent` to extend the body. Needs agnostic-ai 0.69.0 or later.

[SETUP.md](SETUP.md) covers collisions, switching specs off, and updates.

Working on this repo? Install the drift check: `ln -sf ../../sync.sh .git/hooks/pre-commit`.
