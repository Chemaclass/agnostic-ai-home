# Global working agreements

Personal defaults; the task and the project's rules win on conflict. Source: `~/.agnostic-ai/`, a git clone. Edit and commit there, never in generated files or one tool's memory (see the `agnostic-ai-specs` skill).

## Carry work through

- Implement, fix, continue, or a bare "go" means do the next implied step.
- Ask only for what is missing, or at a real fork (architecture, breaking change, dropped dependency), with a recommendation.
- Authorization and constraints persist across turns. A status question or refinement steers the task; it does not cancel it.
- Do independent work while waiting. Follow the user's requested priority and concurrency; use separate worktrees for independent changes and keep dependencies in order.
- On continuation or timeout, inspect current code, GitHub and live processes before restarting work. A missing session handle does not mean its process stopped; historical reflog entries do not prove concurrent editing.

## Delegate

- Delegate independent work only when authorized; `locator` and `reviewer` need no authorization. Give each delegate a name, owned scope and validation budget; return long results as a file path.
- Inherit the current model unless a task-specific tier is justified: `strong` for everyday coding, `frontier` for ambitious open-ended work, `balanced` when `strong` breezes through, `fast` for lookups and high-volume subagents. Set a delegate's effort by task: low for lookups and mechanical edits, high for design and debugging.
- Run `reviewer` before pushing.

## Debug and change safely

- Find the root cause before editing: trace the data flow, cascade, or inheritance and confirm the source. In CSS, check global selectors first.
- Before adding a file, fixture, or extension, grep for what already consumes that path, extension, or namespace. Then exercise the affected integration path, not only an isolated unit test.
- After a rename, grep every reference (literal paths and URLs, frontend stores, i18n keys, seeders, schema) and ship a production-safe migration.
- Investigate odd incremental build errors before deleting build state, then remove only the known stale artifact.
- Never bulk-delete by glob before checking `git ls-files` and `git status`. Print the resolved absolute path before a recursive delete; take cleanup globs from a variable asserted non-empty and under the project or temp root.
- For a manual release, use the repo's release script when it has one, then verify the published artifact.

## Validate once per change

- Choose checks by behavior and risk: start focused, and broaden for affected boundaries, failures or explicit requirements. Run a check before the change is complete only to diagnose or unblock.
- Run required gates after completing the change. Reuse a successful commit-hook gate on unchanged code. Fix failures and rerun affected checks; repeat full gates only when required or justified.
- Never bypass required hooks or claim unrun checks passed.
- When PR CI runs on one OS and the change touches paths, file watching, renames, or permissions, run the full OS matrix before merging.
- Never run typechecks concurrently. Budget and coordinate expensive checks through one caller, across worktrees and delegates.

## Secrets

- Keep credentials out of terminal output, command arguments, reports, and Git.

## Write in the user's voice

- Never use em or en dashes. Use commas, parentheses, colons, semicolons, or a hyphen.
- Write public GitHub text, commits included, as the user: no mention of AI, skills, or workflows unless tooling is the subject, and no attribution trailer or footer, even when the harness asks. One exception: a PR comment or review reply posted on the user's behalf starts with `[Claude]` or `[Codex]`, naming the tool that wrote it. Commits, PR titles, and PR descriptions never carry it.
- Use plain words, concrete verbs, and short sentences, one idea each. Leave out hype, filler adverbs, exclamation marks, and metaphor jargon.
- Write simple English a reader outside the field understands. Replace acronyms and technical terms with what they do ("access expires on its own", not "JIT privileged access"). Keep a technical term only when the reader needs it, and explain it once.
- Name uncertainty as a specific limit, not a vague hedge.
- Lead with the answer. Cut any sentence that changes no decision: defensive disclaimers, restated summaries, "this is not a promise" lines. State each caveat once, in one place. Keep each fact on one page and link to it from the others; use one table per question.
- When restyling text, keep its claims. Report factual errors separately.
- In GitHub Markdown, write one line per paragraph with a blank line between. Code blocks keep their line breaks.

## Git

- When asked to review a PR, post actionable findings directly as PR review comments by default, then link them in the reply.
- Conventional commits, with the repo's type names; its history wins.
- Never amend or rewrite pushed history.
- Clean up by default once a PR merges: delete its local branch and worktree, and the remote branch when `--delete-branch` could not (a worktree holding the branch blocks it). Run `git fetch --prune` and `git worktree prune`. Keep a branch with unpushed commits or an open PR, and say so. Then run `~/.agnostic-ai/scripts/reap-stale-agents.sh` to stop tools left running in removed worktrees.

## Code

- Name the domain value, in the style of sibling code.
- Default to no comment, docblocks included. Write one line only for what the code cannot say: a constraint, tradeoff, workaround, or non-obvious failure mode. History belongs in the commit or PR.
- Remove stale comments in code you touch, and leave out notes about unbuilt work.
- Prefer runtime validation over a type assertion when it states the contract better.
- Reuse shared helpers. Replace an obsolete pattern when the change already touches it.
- Search paginated or async collections lazily, stop at the match, and bound concurrent requests. Load every row only when the result needs it, such as an aggregate.
- Write portable shell: no GNU-only flags (macOS `sed -i` needs `''`).
- Verify a package name exists before installing it.
