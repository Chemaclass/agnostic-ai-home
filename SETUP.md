# Setup for coding agents

You are setting up this repo as the user's global AI configuration. Follow the steps in order. Stop and ask only where a step says so. macOS and Linux.

The rule behind every step: the clone stays pristine. Never edit, commit, or delete tracked files. Everything the user owns goes in `~/.agnostic-ai/local/`: a folder inside the clone that git ignores and sync still reads. That keeps `git pull` conflict-free.

## 1. Install agnostic-ai

Run `agnostic-ai --version`. If it is missing, install it with the first route that fits:

```bash
brew install --cask Chemaclass/tap/agnostic-ai   # macOS or Linux with Homebrew
npm install -g agnostic-ai                       # anywhere with Node 18+
curl -fsSL https://raw.githubusercontent.com/Chemaclass/agnostic-ai/main/scripts/install.sh | bash
```

If it is installed, run `agnostic-ai upgrade`. This repo needs 0.69.0 or later: older versions replace a local spec whole instead of merging it. Also confirm `git` and `python3` exist; the shell guard hook needs Python.

## 2. Clone and link

Check `~/.agnostic-ai` first:

- Missing: clone to `~/Code/agnostic-ai-home` (or where the user asks), then `ln -s <clone> ~/.agnostic-ai`.
- A link to a clone of this repo: run `git -C ~/.agnostic-ai pull --ff-only` and continue.
- A real directory or another repo: stop. Tell the user what is there and offer to move its specs into `local/` inside a fresh clone.

## 3. Pick the tools

Find the AI CLIs the user has: look for binaries (`claude`, `codex`, `cursor-agent`, `gemini`, ...) and config dirs (`~/.claude`, `~/.codex`, `~/.cursor`, `~/.gemini`, ...). Map each to its agnostic-ai target name, then write them comma-separated to `~/.agnostic-ai/local/targets`:

```bash
mkdir -p ~/.agnostic-ai/local && printf 'claude,codex,cursor\n' > ~/.agnostic-ai/local/targets
```

Without that file, `sync.sh` targets `claude,codex,cursor`. If sync rejects a name, its error lists the supported ones. Tell the user that the `guard-shell` hook ships for Claude Code, Codex, and Cursor only; other tools get the agreements, skills, and agents.

## 4. Preview and resolve collisions

```bash
~/.agnostic-ai/sync.sh --dry-run
```

On `unmanaged global skill collision` (or agent or rule), compare the existing folder with the one in this repo:

- Same content: move the old one to `~/.agnostic-ai/backups/` (gitignored).
- Different: ask the user which wins. To keep theirs, move it to `~/.agnostic-ai/local/skills/<name>/`. Its body and fields win; a shared field it does not set still applies, so set that field to `null` to drop it. Never delete it.

Repeat the dry run until it is clean.

## 5. Sync and verify

```bash
~/.agnostic-ai/sync.sh && ~/.agnostic-ai/sync.sh --check
agnostic-ai list --global
git -C ~/.agnostic-ai status --short   # must print nothing
```

Sync writes a managed block into each tool's global instructions file (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, ...) and real files into its skills, agents, and hooks folders. Text outside the managed block stays the user's. Tell the user to restart open sessions.

Codex runs a hook only after the user trusts it. Tell them to open Codex, run `/hooks`, and trust `guard-shell`. Until then Codex skips the guard without a warning. A sync that changes the hook needs a new review.

## Extending with local/

`~/.agnostic-ai/local/` mirrors the repo layout. A local spec with a new name is added. One with the same kind and name merges into the shared spec: write only what changes.

```text
~/.agnostic-ai/local/targets                 # tools to sync, comma-separated
~/.agnostic-ai/local/AGNOSTIC_AI.md          # appended after the shared agreements
~/.agnostic-ai/local/skills/<name>/SKILL.md  # a private skill, or edits skills/<name>/
~/.agnostic-ai/local/agents/<name>.md        # a private agent, or edits agents/<name>.md
~/.agnostic-ai/local/hooks/<name>.yaml       # a private hook, or edits hooks/<name>.yaml
```

- To change a shared spec, create the same path under `local/` with `name` and only the fields that change. Maps merge key by key, scalars and lists replace, `null` removes a key.
- The body: leave it empty to keep the shared one, put a `::parent` line where the shared body goes to extend it, or write a new body to replace it.
- To switch a shared skill, agent, or hook off, create it under `local/` with `name` and `targets-exclude: [<every synced target>]`. Nothing else to copy.
- To change a shared agreement, add the replacement to `local/AGNOSTIC_AI.md` and say it overrides the shared one.

Run `~/.agnostic-ai/sync.sh` after every change. `local/` never leaves the machine, so suggest the user back it up privately. Rules for one repo belong in that repo, not here: `local/` loads in every session.

## Updating

```bash
git -C ~/.agnostic-ai pull --ff-only && ~/.agnostic-ai/sync.sh
```

New shared files arrive with the pull, and sync applies each local spec on top of the new shared one. Only a local spec that replaces the whole body needs a manual merge. For those, show the user what changed upstream:

```bash
git -C ~/.agnostic-ai diff ORIG_HEAD HEAD -- skills/<name> agents/<name>.md hooks/<name>.yaml
```
