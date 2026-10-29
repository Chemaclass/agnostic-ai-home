---
name: gh-issues
description: "Work a repository's ready GitHub issues, each through gh-issue and its own PR. Run it to work the backlog or the queue."
disable-model-invocation: true
x-claude:
  argument-hint: "[--limit N] [--milestone M] [--label L] [--dry-run]"
---

# Work the queue

Process open issues that are unassigned or assigned to you, each through the `gh-issue` skill, each ending in its own PR. The repository's own rules win over this skill. Read the repo's agent instructions for its branch, gate, and merge rules. If the repo has its own queue skill with a project prefix such as `miaforo-gh-issues` (under `.agnostic-ai/skills/`, `.claude/skills/`, or `.agents/skills/`), follow it where it differs. Use the repo's issue skill the same way. The user's explicit priority, parallelism and continuation instructions take precedence over workflow defaults; keep dependency and verification requirements.

## Args

- `--limit N`: at most N this run
- `--milestone M`, `--label L`: only matching issues
- `--dry-run`: print the queue and stop

## 1. Refuse to start on a dirty tree

```bash
git status --porcelain      # must be empty
git fetch origin
```

## 2. Build the queue

```bash
gh api --paginate 'repos/{owner}/{repo}/issues?state=open&per_page=100' --jq '.[] | select(has("pull_request") | not) | {number,title,labels: [.labels[].name],milestone: .milestone.title,assignees: [.assignees[].login],createdAt: .created_at}'
gh api user -q .login
```

1. Keep issues unassigned or assigned to you; drop the rest. Apply the filters.
2. Order by the repo's roadmap when it has one (a pinned or labeled roadmap issue, or one named in its agent instructions), reading its body and every comment. Otherwise by priority label, then oldest first.
3. Read each candidate and its comments before marking it ready. Skip open blockers, unresolved product decisions, and external account prerequisites, with the specific reason. Skip roadmaps and epics whose child issues own the deliverables. A blocker is done when its PR is merged, not when it is open.
4. Building or printing the queue assigns nothing; `gh-issue` assigns the issue whose work starts.

Print one line per issue: `#<n> <title> - ready | blocked by #<m> | skipped: <reason>`. If nothing is ready, say so and stop.

## 3. Deliver the queue

1. Work each ready issue with the `gh-issue` skill. Recheck assignment, current code and related PRs immediately before starting it.
2. Work sequentially by default. When parallel work is authorized, use isolated worktrees, one owner per issue and the requested concurrency limit. Start higher-priority ready issues first; never start a dependent issue before its blocker merges.
3. Keep one PR per issue. Merge only when its required checks are green on its current head and the repo permits it. When another PR lands, update affected branches, resolve conflicts and repeat the checks affected by that update.
4. Coordinate expensive checks across worktrees; never run typechecks concurrently. Reuse a successful gate on unchanged code instead of running it in the worker, commit hook and main thread again.
5. Fix routine test, style and CI failures within the issue. If it cannot proceed, report the exact failure and preserve its branch. Stop the run by default; when the user explicitly asked to keep going, continue only with independent ready issues.
6. On continuation, inspect the current issue, PR and worktree state and any live validation process before restarting work. A tool observation timeout is not a failed check.

## 4. Report

A table of issue, PR URL, and status, plus everything skipped and why.

## Rules

- Never work a blocked issue "to get ahead": the design depends on the blocker, and guessing its interface wastes both PRs.
- Do not dispatch a workflow just to obtain a green check.
