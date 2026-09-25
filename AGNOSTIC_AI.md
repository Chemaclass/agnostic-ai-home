# Global working agreements

Personal defaults across projects. Explicit task instructions and project requirements determine the authorized scope. This file is generated from `~/.agnostic-ai/`; edit the source there, not here (the `agnostic-ai-specs` skill has the workflow).

## Carry authorized work through

- Treat requests to implement, fix, or continue as instructions to do the work. Research and planning support delivery; they are not the stopping point when implementation is authorized.
- Keep authorization and constraints across turns. A status question or refinement steers the current task unless the user cancels or replaces it.
- Do useful independent work while waiting for missing information. Ask only for information or permission that is necessary and not already available or granted.
- When backlog work is requested, inspect every candidate issue and its comments, follow the current dependency graph, and process all actionable issues. Record concrete blockers and continue other independent work. Do not invent decisions or mark external prerequisites complete. For GitHub, the `gh-issues` and `gh-issue` skills have the workflow.
- Verify current repository and deployed state before repeating an old issue's findings. Refresh a stale issue body or roadmap when later comments have left it contradicting the evidence.
- Delegate independent work when useful and permitted by the active instructions. Do not force parallelism onto a trivial task. Give delegated agents distinct names and say which model each one runs on.
- Give delegates the task scope and validation budget explicitly. Coordinate expensive checks in the main thread.

## Vertical feature slicing

- Start every feature with the smallest customer-visible end-to-end outcome.
- State one acceptance scenario and explicit non-goals before implementation. Remove work that is not required for that scenario.
- Each feature PR must be independently deployable, usable, and coherent without another unmerged feature PR.
- Slice across UI, API, persistence, and runtime when the outcome needs all of them. Use stacked PRs only when each independently delivers value.
- Prefer a simple initial interface and one narrow configuration scope. Defer inheritance, multi-scope configuration, previews, rich editors, telemetry, and broad test matrices until customer evidence justifies them.
- Keep the safety and consistency rules needed for production correctness.
- Respect the issue's scope. Open a follow-up issue for unrelated work instead of expanding the PR silently.
- Green checks, tidy commits, and easy review are quality gates. The acceptance scenario proves customer value.

## Validation cadence

- Batch validation after the intended changes are complete. Do not run tests, typechecks, linters, or builds after every small edit.
- Use an earlier targeted check only to diagnose a failure or unblock implementation.
- Run expensive typechecks, full builds, and broad suites once per completed change set. Never run multiple typechecks concurrently. Budget these checks explicitly across worktrees and delegates.
- Investigate inconsistent incremental build errors before deleting build state. Remove only the known stale artifact when that is the cause.

## Secrets and recovery

- Keep credentials out of terminal output, command arguments, reports, and Git.
- Before claiming a backup works or handling recovery secrets, use the `recovery-evidence` skill.

## Writing in the user's voice

- Never use em or en dashes. Use commas, parentheses, colons, semicolons, or a regular hyphen.
- Write public GitHub comments directly in the user's voice. Do not mention AI generation, agent skills, internal workflows, or attribution boilerplate. Describe tooling normally when it is the subject of the work.
- Prefer plain language, concrete verbs, short sentences, and one idea at a time. Use fragments and bold sparingly for emphasis. Avoid corporate hype, filler adverbs, exclamation marks, and metaphor jargon.
- State uncertainty as a specific limitation instead of vague hedging.
- When restyling existing text, preserve its claims. Surface factual errors separately.
- Write GitHub Markdown prose as one long line per paragraph, separated by blank lines. Keep natural line breaks in code blocks.

## Code clarity

- Choose names that describe the domain value and follow sibling code's conventions. Avoid vague names when a more specific one explains the meaning.
- Default to no comment. Write one only when the code cannot carry the reason: a constraint, a tradeoff, a workaround, a non-obvious failure mode. Never narrate what the code already says.
- Keep it to one line wherever possible. No history, no retelling of the bug that caused it, no evidence tables, no restating an error message or a test. That context belongs in the commit, the PR, or the ticket. Cut every word that does not change what the reader does next.
- Docblocks meet the same bar: they exist for a contract the signature cannot express, not because a symbol is exported.
- Remove stale comments in code you touch. Avoid speculative notes about unbuilt work.
- Prefer runtime validation over a type assertion when it states the contract more clearly.
- Reuse shared helpers and conventional support locations. Apply an established replacement when the changed code already touches an obsolete pattern.
- In domain code, keep decisions next to the data they protect: ask an object for an answer instead of pulling its data out and deciding elsewhere. Wrap primitives and collections when they carry rules or invariants. The `object-design` skill has the full method.
- Skip that for DTOs, read models, serialization, ORM mappings, framework adapters, and performance-critical code, where exposing data is the job.

## Collections and generated files

- Search paginated or asynchronous collections lazily and return on the match. Expose asynchronous iteration from paginated wrappers so callers can stop early, and bound concurrent requests when scanning widely. Use a named helper instead of an inline async IIFE.
- Materialize every row only when the outcome requires it, such as an aggregate, and explain that choice when it is not apparent.
- Never bulk-delete generated files by glob. Check `git ls-files` and status first; generated directories may contain tracked files and unrelated work. Clean only explicitly identified, disposable artifacts, and preserve tracked changes and other worktrees.
