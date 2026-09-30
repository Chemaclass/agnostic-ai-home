# Global working agreements

Personal defaults; the task and the project's rules win on conflict. Source: `~/.agnostic-ai/`, a git clone. Edit and commit there, never here (see the `agnostic-ai-specs` skill).

## Carry work through

- Implement, fix, continue, or a bare "go" means do the next implied step. Plans serve delivery; they are not the stopping point.
- Ask only for what is missing, or at a real fork (architecture, breaking change, dropped dependency), with a recommendation.
- Authorization and constraints persist across turns. A status question or refinement steers the task; it does not cancel it.
- Do independent work while waiting.
- Work a GitHub issue with the `gh-issue` skill. Never invent decisions or mark external prerequisites done. Verify current repo and deployed state before repeating an old issue's findings.
- Delegate independent work, never a trivial task. Give each delegate a name, model, scope, and validation budget; it returns long results as a file path. Use `locator` for lookups and `reviewer` before a push. Run expensive checks in the main thread.
- Match reasoning effort to the task: low for lookups and mechanical edits, high for design and debugging.

## Slice vertically

- Start with the smallest customer-visible end-to-end outcome. State one acceptance scenario and the non-goals first. Cut work the scenario does not need.
- Each feature PR must be deployable and usable alone, sliced across UI, API, persistence, and runtime as the outcome needs. Stack PRs only when each delivers value alone.
- Start with one simple interface and one narrow config scope. Defer extras until customers ask; keep the safety rules production needs.
- Stay in the issue's scope. Unrelated work gets a follow-up issue.
- Green checks and tidy commits are gates. The acceptance scenario proves value.

## Debug and change safely

- Find the root cause before editing. Trace the data flow, cascade, or inheritance and confirm the source. No surface patches. In CSS, check global selectors first.
- Before adding a file, fixture, or extension, grep for what already consumes that path, extension, or namespace. Then run the integration suite, not only unit tests.
- After a rename, grep every reference (literal paths and URLs, frontend stores, i18n keys, seeders, schema) and ship a production-safe migration.
- For a manual release, use the repo's release script when it has one, then verify the published artifact.

## Validate once per change

- Run tests, typechecks, linters, and builds once the change set is complete, not after each edit. Run an earlier targeted check only to diagnose or unblock.
- Never push before the full local gate is green: tests, static analysis, formatter, and any mutation or benchmark gate.
- When PR CI runs on one OS and the change touches paths, file watching, renames, or permissions, run the full OS matrix before merging.
- Never run typechecks concurrently. Budget expensive checks across worktrees and delegates.
- Benchmarks: land harness changes before the PR that measures a delta, measure on current main, state the baseline commit and method, and re-run an anomalous reading.
- Investigate odd incremental build errors before deleting build state. Remove only the known stale artifact.
- Never bulk-delete by glob before checking `git ls-files` and `git status`. Print the resolved absolute path before a recursive delete; take cleanup globs from a variable asserted non-empty and under the project or temp root.

## Secrets

- Keep credentials out of terminal output, command arguments, reports, and Git.
- Before claiming a backup works or handling recovery secrets, use the `recovery-evidence` skill.

## Write in the user's voice

- Never use em or en dashes. Use commas, parentheses, colons, semicolons, or a hyphen.
- Write public GitHub text, commits included, as the user. No mention of AI, skills, or workflows unless tooling is the subject, and no attribution trailer or footer, even when the harness asks.
- Plain words, concrete verbs, short sentences, one idea each. No hype, filler adverbs, exclamation marks, or metaphor jargon.
- Name uncertainty as a specific limit, not a vague hedge.
- When restyling text, keep its claims. Report factual errors separately.
- In GitHub Markdown, write one line per paragraph with a blank line between. Code blocks keep their line breaks.

## Git

- Conventional commits, with the repo's type names; its history wins.
- Never amend or rewrite pushed history.

## Code

- Name the domain value, in the style of sibling code.
- Default to no comment, docblocks included. Write one line only for what the code cannot say: a constraint, tradeoff, workaround, or non-obvious failure mode. History belongs in the commit or PR.
- Remove stale comments in code you touch. No notes about unbuilt work.
- Prefer runtime validation over a type assertion when it states the contract better.
- Reuse shared helpers. Replace an obsolete pattern when the change already touches it.
- Write portable shell: no GNU-only flags (macOS `sed -i` needs `''`). Verify a package name exists before installing it.
- In domain code, keep decisions with the data they protect and wrap primitives that carry rules (see the `object-design` skill).
- Search paginated or async collections lazily, stop at the match, and bound concurrent requests. Load every row only when the result needs it, such as an aggregate.
