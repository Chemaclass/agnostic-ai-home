---
name: gh-issue
description: "Take one GitHub issue to a PR: read every comment, branch, implement, verify each acceptance criterion. Use when asked to work, fix, or pick up an issue by number or URL."
x-claude:
  argument-hint: "[issue-number or URL]"
---

# Work one issue

The repository's own rules win over this skill. Before starting, read its agent instructions (`AGENTS.md`, `CLAUDE.md`, `.agnostic-ai/`) and `CONTRIBUTING.md` for branch naming, validation gates, commit and PR conventions, and merge rules. If the repo has its own issue skill, named `gh-issue` or with a project prefix such as `phel-gh-issue` (under `.agnostic-ai/skills/`, `.claude/skills/`, or `.agents/skills/`), read it and follow it where it differs. A project copy named `gh-issue` is hidden in Claude Code by this personal one, so projects use the prefix. This skill is the order of operations when the repo is silent.

## Context

Read the issue body **and every comment**. Later comments override the body: they are usually the maintainer narrowing scope.

```bash
gh issue view <n> --json number,url,title,body,labels,milestone,assignees,state,comments
git status --short
gh repo view --json defaultBranchRef -q .defaultBranchRef.name
```

## 1. Setup

1. Refuse to start on a dirty working tree; say what is uncommitted.
2. Confirm the issue is ready: no open blocker (a blocker is done when its PR is merged, not when it is open), no unresolved product decision, no missing external prerequisite. Check the repo's roadmap issue when it has one. If it is not ready, say why and stop.
3. Assign yourself only now, as work starts: `gh issue edit <n> --add-assignee @me`.
4. Branch from the remote default branch, never the local one (local commits ahead of origin get swallowed by a squash merge). Name it `<n>-<slug>` unless the repo has its own convention:

   ```bash
   git fetch origin && git checkout -b <n>-<slug> origin/<default-branch>
   ```

## 2. Understand before writing

5. Treat the issue's scope and out-of-scope sections as a contract. State the acceptance scenario and non-goals. Work outside them gets a new issue, not this PR.
6. Read decisions already made in the issue, linked issues, and linked designs, so the PR does not relitigate them.
7. Explore the code the issue names before designing.

## 3. Implement

8. For behavioral acceptance criteria (concurrency, boundaries, money, permissions), **write the failing test first**. Those cases cannot be checked by hand.
9. Use the repo's own skills for specialized steps (migrations, schema changes, audits) when it has them.

## 4. Verify

10. Verify every acceptance criterion with the command the issue gives, or the narrowest command that proves it. Not "looks right".
11. After the complete change, run the repo's pre-push gate once (from its instructions, `CONTRIBUTING.md`, package scripts, Makefile, or CI config).

## 5. Ship

12. Commit and open the PR with the repo's `commit` and `pr` skills when it has them. Otherwise: a conventional commit subject that says what the change does, `git push -u origin HEAD`, and `gh pr create --assignee @me --label <type>` (bug, enhancement, ...) with a body covering what and why, decisions worth challenging, how each criterion was verified, and `Closes #<n>`.
13. Merge only when the repo's rules let you merge your own PR and its required checks are green on the head commit. Otherwise leave it open for review. When another PR is stacked on this one, run `gh pr edit <stacked> --base <default>` before merging with `--delete-branch`, or GitHub closes the stacked PR. After the merge, sync the default branch and remove the PR's worktree and local branch, and its remote branch if it survived.
14. Report the PR URL, which acceptance criteria you verified, and plainly which you could not.

## Rules

- One issue, one PR, one branch. Never widen scope silently: out-of-scope work gets its own issue, and the PR mentions it.
- Never mark an acceptance criterion done without running its verification.
- If work pauses while the issue stays open, unassign yourself: `gh issue edit <n> --remove-assignee @me`.
- If the issue is wrong or impossible, say so in an issue comment and stop. Do not invent a different feature.
