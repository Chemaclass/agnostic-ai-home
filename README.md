# agnostic-ai home

A personal, tool-agnostic setup for AI coding CLIs. Write your working agreements, skills, agents, and hooks once. [agnostic-ai](https://agnostic-ai.org) turns them into native config for Claude Code, Codex, and Cursor.

Use it as is, fork it, or read it for ideas.

## What is inside

```text
~/.agnostic-ai/
├── AGNOSTIC_AI.md   # working agreements, loaded in every session
├── skills/          # loaded on demand, when the task matches
├── agents/          # read-only subagents with a model tier each
├── hooks/           # guards that run before shell commands
├── scripts/         # code the hooks call
└── sync.sh          # the one command to sync and check
```

- **Agreements** (`AGNOSTIC_AI.md`): finish authorized work, slice features vertically, batch validation, keep secrets out of output, write plainly, keep code comments rare. Short on purpose: it loads in every session.
- **Skills**: `gh-issue` and `gh-issues` (work one issue or the whole queue, one PR each), `pr-value-audit` (should this PR exist, and does every part earn its place), `object-design` (move decisions to the objects that own the data), `recovery-evidence` (what proves a backup works), `agnostic-ai-specs` (how to edit this kind of repo), `i-have-adhd` (output shaped for acting, not reading).
- **Agents**: `locator` finds code, `claim-verifier` proves or refutes claims with `file:line` evidence, `reviewer` reports defects one line each. All three are read-only, and each sets a cheap or strong model for Claude and Codex in its frontmatter.
- **Hook**: `guard-shell` blocks force pushes without `--force-with-lease`, recursive `rm` with a glob, printing secret files like `.env`, and em or en dashes in commit messages and `gh` text.

## Use it

1. [Install agnostic-ai](https://agnostic-ai.org/docs/installation/).
2. Clone this repo to `~/.agnostic-ai` (or point `AGNOSTIC_AI_HOME` at your clone).
3. Edit `sync.sh` to list the CLIs you use.
4. Run `./sync.sh`, then `./sync.sh --check`.
5. Install the drift check: `ln -sf ../../sync.sh .git/hooks/pre-commit`.

Restart open sessions to load the new instructions.

Sync writes a managed block into `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, and `~/.cursor/AGENTS.md`, and real files into each tool's skills, agents, and hooks locations. Text outside the managed block is yours and stays untouched. If a skill folder with the same name already exists, sync stops with "unmanaged global skill collision": move the old folder aside, then sync again.

## Extend it without forking the shared parts

Anything named `*.local.md`, `*.local.yaml`, or `*.local/` is gitignored but still synced. Use it for what should not be public: personal quirks, employer notes, private workflows.

```text
rules/personal.local.md             # extra agreements, appended to the managed block
skills/work-notes.local/SKILL.md    # a private skill, emitted under its frontmatter name
agents/my-helper.local.md           # a private agent
hooks/my-guard.local.yaml           # a private hook
```

For example, `rules/personal.local.md` can turn "give delegated agents distinct names" into your own naming scheme. Local files never leave your machine, so back them up somewhere private.

Keep project-specific rules in that project's own `.agnostic-ai/` directory, not here. Skills that only make sense with one CLI's connectors (a Notion or Slack integration) can stay in that CLI's own skills folder.

## Known limitations

- agnostic-ai 0.68 ignores `target` on global hooks, so the one Claude-style `PreToolUse` hook also lands in Codex and Cursor. Cursor still runs it through its import of `~/.claude/settings.json` (on by default). Fixed upstream, pending release.
- Global sync copies skill files as they are, so per-tool `model` maps and `x-claude` blocks on skills are not resolved. That is why `pr-value-audit` uses a plain `model: opus`, which Codex and Cursor ignore.

## License

MIT, see `LICENSE`. `skills/i-have-adhd` is adapted from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) and keeps its own MIT notice in `skills/i-have-adhd/LICENSE`.
