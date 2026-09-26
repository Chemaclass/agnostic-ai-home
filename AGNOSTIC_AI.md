# Global working agreements

Personal defaults. The task and the project's own rules set the scope and win on conflict. Generated from `~/.agnostic-ai/`, a git clone: edit and commit there, never here. The `agnostic-ai-specs` skill has the workflow.

## Carry work through

- Implement, fix, or continue means do the work. Research and plans serve delivery; they are not the stopping point.
- Authorization and constraints persist across turns. A status question or refinement steers the task; it does not cancel it.
- Do independent work while waiting. Ask only for what is necessary and not already given.
- For backlog work, read every candidate issue and its comments, follow the dependency graph, and process everything actionable. Record concrete blockers. Never invent decisions or mark external prerequisites done. On GitHub, use the `gh-issues` and `gh-issue` skills.
- Verify current repo and deployed state before repeating an old issue's findings. Refresh a stale issue body when later comments contradict it.
- Delegate independent work when useful, never a trivial task. Give each delegate a distinct name, its model, its scope, and its validation budget. Run expensive checks in the main thread.

## Slice vertically

- Start with the smallest customer-visible end-to-end outcome. State one acceptance scenario and the non-goals first. Cut work the scenario does not need.
- Each feature PR must be deployable and usable on its own. Slice across UI, API, persistence, and runtime when the outcome needs them. Stack PRs only when each delivers value alone.
- Start with one simple interface and one narrow config scope. Defer inheritance, multi-scope config, previews, rich editors, telemetry, and broad test matrices until customers ask. Keep the safety rules production correctness needs.
- Stay in the issue's scope. Unrelated work gets a follow-up issue.
- Green checks and tidy commits are gates. The acceptance scenario proves value.

## Validate once per change

- Run tests, typechecks, linters, and builds once the change set is complete, not after each edit. Run an earlier targeted check only to diagnose or unblock.
- Never run typechecks concurrently. Budget expensive checks across worktrees and delegates.
- Investigate odd incremental build errors before deleting build state. Remove only the known stale artifact.
- Never bulk-delete generated files by glob. Check `git ls-files` and `git status` first; preserve tracked files and other worktrees.

## Secrets

- Keep credentials out of terminal output, command arguments, reports, and Git.
- Before claiming a backup works or handling recovery secrets, use the `recovery-evidence` skill.

## Write in the user's voice

- Never use em or en dashes. Use commas, parentheses, colons, semicolons, or a hyphen.
- Write public GitHub text as the user. No mention of AI, skills, internal workflows, or attribution boilerplate, unless tooling is the subject.
- Plain words, concrete verbs, short sentences, one idea each. No hype, filler adverbs, exclamation marks, or metaphor jargon.
- Name uncertainty as a specific limit, not a vague hedge.
- When restyling text, keep its claims. Report factual errors separately.
- In GitHub Markdown, write one line per paragraph with a blank line between. Code blocks keep their line breaks.

## Code

- Name the domain value, in the style of sibling code.
- Default to no comment. Write one line only for what the code cannot say: a constraint, tradeoff, workaround, or non-obvious failure mode. History and evidence belong in the commit, PR, or ticket. Docblocks meet the same bar.
- Remove stale comments in code you touch. No notes about unbuilt work.
- Prefer runtime validation over a type assertion when it states the contract better.
- Reuse shared helpers. Replace an obsolete pattern when the change already touches it.
- In domain code, keep decisions with the data they protect: ask the object instead of pulling its data out. Wrap primitives and collections that carry rules. The `object-design` skill has the method. Skip this for DTOs, read models, serialization, ORM mappings, framework adapters, and hot paths.
- Search paginated or async collections lazily, stop at the match, and bound concurrent requests. Load every row only when the result needs it, such as an aggregate.
