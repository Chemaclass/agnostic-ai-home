---
name: gh-issues
description: "Work a repository's ready GitHub issues one at a time, each through gh-issue and its own PR. Run it to work the backlog or the queue."
disable-model-invocation: true
x-claude:
  argument-hint: "[--limit N] [--milestone M] [--label L] [--dry-run]"
---

# Work the queue

Process open issues that are unassigned or assigned to you, each through the `gh-issue` skill, each ending in its own PR. The repository's own rules win over this skill. Read the repo's agent instructions for its branch, gate, and merge rules. If the repo has its own queue skill with a project prefix such as `miaforo-gh-issues` (under `.agnostic-ai/skills/`, `.claude/skills/`, or `.agents/skills/`), follow it where it differs. Use the repo's issue skill the same way.

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

## 3. One at a time

For each ready issue:

1. Work it with the `gh-issue` skill.
2. When its PR merges, move to the next. When the repo requires human review, continue only with issues that neither depend on nor touch the same files as an open PR from this run.
3. **On failure, stop the whole run** and report which issue failed and why, while the context is fresh.

## 4. Report

A table of issue, PR URL, and status, plus everything skipped and why.

## Rules

- Never work a blocked issue "to get ahead": the design depends on the blocker, and guessing its interface wastes both PRs.
- Do not dispatch a workflow just to obtain a green check.
