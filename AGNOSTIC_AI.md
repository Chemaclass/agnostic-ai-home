# Global working agreements

These are personal defaults across projects. Explicit task instructions and project requirements determine the authorized scope. Keep shared preferences here and run `agnostic-ai sync --global --only claude,codex`; edit a project's `.agnostic-ai/` for its domain rules. Generated native instructions are outputs, not another source to maintain.

## Carry authorized work through

- Treat requests to implement, fix, or continue as instructions to do the work. Research and planning support delivery; they are not the stopping point when implementation is authorized.
- Keep authorization and constraints across turns. A status question or refinement steers the current task unless the user cancels or replaces it.
- Do useful independent work while waiting for missing information. Ask only for information or permission that is necessary and not already available or granted.
- When backlog work is requested, inspect every candidate issue and its comments, follow the current dependency graph, and process all actionable issues. Record concrete blockers and continue other independent work. Do not invent decisions or mark external prerequisites complete.
- Verify current repository and deployed state before repeating an old issue's findings. Refresh a stale issue body or roadmap when later comments have left it contradicting the evidence.
- Delegate independent work when useful and permitted by the active instructions. Do not force parallelism onto a trivial task. Give delegated agents distinct Lord of the Rings names and start descriptions with `Name (model):` where supported.
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

## Test business behavior

- Test observable behavior, domain rules, and outcomes. Avoid tests coupled to private functions, source text, incidental markup, or a particular implementation when those are not the contract.
- Prioritize money movement, payment provider integration, tenant isolation, authorization, booking access, capacity, allowances, and the product's core differentiators.
- Choose inputs that distinguish correct behavior from a plausible defect. Exercise boundaries, failure paths, replay, concurrency, and state transitions where the domain requires them. Remove assertions that cannot catch a regression.
- Use a real database when locks, constraints, transactions, or query scoping are the subject. Use integration and end-to-end journeys to connect business-critical boundaries.
- Keep ordinary tests deterministic. Use controlled provider boundaries there, and run real provider sandbox checks separately when authorized and configured.
- For payment verification, check both sides of the transaction and the resulting entitlement or debt. A checkout redirect alone is not proof of settlement. Distinguish actual provider webhooks from locally signed fixtures.
- Reuse existing fixture builders and test helpers. Do not add redundant coverage or broad matrices to inflate a count.
- Support claims about external APIs, retries, buffers, and other defensive behavior with documentation, a discriminating test, or an observed response. State remaining uncertainty precisely.

## Validate the final change locally

- Do not dispatch GitHub Actions unless explicitly requested. Follow the project's local CI or release gate and record the result and validated revision.
- Batch validation after the intended changes are complete. Do not run tests, typechecks, linters, or builds after every small edit.
- Use an earlier targeted check only to diagnose a failure or unblock implementation.
- Run expensive typechecks, full builds, and broad suites once per completed change set. Never run multiple typechecks concurrently. Budget these checks explicitly across worktrees and delegates.
- Validate the tree that will ship. Incorporate pending changes from main before the final gate where possible. Rerun affected checks after refactoring, resolving conflicts, or changing the validated tree.
- Investigate inconsistent incremental build errors before deleting build state. Remove only the known stale artifact when that is the cause.
- Report skips, failures, and unverified external steps. Do not turn a partial pass into a claim that the whole flow works.
- Execute runbook commands exactly as documented, including startup, configuration selection, and shutdown where relevant. A working private launcher does not prove a different published command works.
- Before an authorized release, compare local deployment settings with current production when another machine may have changed them. Inspect names and equality without exposing values, preserve intentional production changes, and keep any necessary rollback copy private. Verify registry access with the credential the release actually uses; a working local Docker login may use a different one.

## Handle recovery evidence carefully

- When access is authorized, inspect only what the task needs and keep credentials out of terminal output, command arguments, reports, and Git. Copy necessary recovery secrets directly between private files rather than printing them.
- A backup claim needs a restore of the actual remote object, decrypted away from the machine it protects, with meaningful data and integrity checks. Listing files or restoring the local source dump proves less.
- Keep encryption passwords, salts, referenced private keys, and other required recovery state together in the approved durable destination. A private local copy is useful progress, not proof that password-manager storage is complete.

## Review, refactor, and merge

- Use a focused PR per issue or independently valuable slice. Prefer getting coherent value to main promptly over stacking dependent fragments.
- Fetch current main, incorporate concurrent changes safely, and inspect the full diff before pushing. Preserve changes made from another machine or worktree. Use the project's safeguards against reverting already merged work.
- Never use `git reset --soft origin/main` to squash a branch. Rebase or use the repository's supported merge strategy.
- After opening a PR, review the complete change for correctness, domain behavior, clarity, duplication, and maintainability. Look for a useful refactor before merging.
- Add a separate refactor commit when it makes the change clearer or safer within scope. Consider it deliberately; do not manufacture churn just to produce a refactor commit.
- Add new commits to an open PR. Do not amend existing commits or force push unless explicitly requested.
- Merge only when merging is authorized, the final diff has been reviewed, relevant local gates pass, and no material correctness concern remains. Treat the user's "5/5 confidence" standard as this evidence gate, not a subjective score or a guarantee that no bug exists.
- When merge authorization is already given, finish the review and merge without asking again. Update local main, then proceed to the next ready issue.
- Describe what changed, why, meaningful verification, and material limitations in the PR. Keep public prose concise and factual.

## Writing in the user's voice

- Never use em or en dashes. Use commas, parentheses, colons, semicolons, or a regular hyphen.
- Write public GitHub comments directly in the user's voice. Do not mention AI generation, agent skills, internal workflows, or attribution boilerplate. Describe tooling normally when it is the subject of the work.
- Before drafting messages, PR prose, review comments, or work documents in the user's name, consult the current voice guide at `https://raw.githubusercontent.com/Chemaclass/chemaclass.com/main/.claude/skills/writing-style/SKILL.md`. If unavailable, use these local defaults and report the limitation when material.
- Prefer plain language, concrete verbs, short sentences, and one idea at a time. Use fragments and bold sparingly for emphasis. Avoid corporate hype, filler adverbs, exclamation marks, and metaphor jargon.
- State uncertainty as a specific limitation instead of vague hedging.
- When restyling existing text, preserve its claims. Surface factual errors separately.
- Write GitHub Markdown prose as one long line per paragraph, separated by blank lines. Keep natural line breaks in code blocks.

## Code clarity

- Choose names that describe the domain value and follow sibling code's conventions. Avoid vague names when a more specific one explains the meaning.
- Comments explain a non-obvious reason, constraint, workaround, or tradeoff. Do not narrate the code or repeat an error message. Keep comments brief, current, and next to the line they explain.
- Remove stale comments in code you touch. Avoid speculative notes about unbuilt work.
- Prefer runtime validation over a type assertion when it states the contract more clearly.
- Reuse shared helpers and conventional support locations. Apply an established replacement when the changed code already touches an obsolete pattern.

## Collections and generated files

- Search paginated or asynchronous collections lazily and return on the match. Use a named helper instead of an inline async IIFE.
- Expose asynchronous iteration from paginated wrappers so callers can stop without draining every page. Bound concurrent requests when scanning widely.
- Materialize every row only when the outcome requires it, such as an aggregate, and explain that choice when it is not apparent.
- Never bulk-delete generated files by glob. Check `git ls-files` and status first; generated directories may contain tracked files and unrelated work.
- Clean only explicitly identified, disposable artifacts. Preserve tracked changes and other worktrees. Keep generated agnostic-ai output ignored where the project uses canonical specs.
- Verify that shared instructions remain usable after generation, including referenced files. When one body is emitted at different directory depths, use explicit repository-root paths and state that convention; a clean sync alone does not prove the references work.
