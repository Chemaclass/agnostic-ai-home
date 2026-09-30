---
name: pr-value-audit
disable-model-invocation: true
description: "Audit whether a PR should ship and whether each part earns its place: verify premises on the base branch, hunt duplication and YAGNI, label units, propose cuts. Takes a PR number, URL, or branch; defaults to the current branch."
model: {claude: opus}
effort: {claude: xhigh}
x-codex:
  policy:
    allow_implicit_invocation: false
---

# PR Value Audit

The `high-level-pr-review` skill asks "is this PR done in the right way?".
This skill asks a different question: **"should this PR exist, and does every part of it earn its place?"**

Three sub-questions, in this order:

1. **Is the problem real?** Verified from the base branch's code, not from the PR description.
2. **Is every piece needed?** Which parts are essential, which are defensive, which are speculative.
3. **Can it be smaller?** Same value, less code, less risk.

Valid outcomes include **shelve it** and **ship a fifth of it**. Do not treat "improve the PR" as the only acceptable answer.

Defer to the repo's `high-level-pr-review` skill for coherent intent and PR sizing, and to its `prove-it` skill for how to prove a claim. Where a repo has neither, apply the rules in this file directly. Do not review CI, formatting, or general architecture, absorb unrelated bugs, or post to GitHub unless asked.

Before classifying units, state:

- **Acceptance scenario**: one sentence naming the actor, trigger, and customer-visible or operational outcome.
- **Non-goals**: behavior deliberately excluded from this change.

Reconstruct missing intent from linked issues, discussion, commits, and the diff. Mark what stays unclear as unknown rather than inventing it.

## Step 1: Resolve the target

Argument is a PR number, a GitHub URL, a branch name, or empty.

- Empty: the PR for the current branch. Fetch `number,title,body,url,state,isDraft,baseRefName,baseRefOid,headRefName,headRefOid,commits,labels`.
- Number or URL: same command with the number.
- **Pin `baseRefOid` and `headRefOid` as immutable refs.** Diff with `...`, but evaluate premises and duplication against `baseRefOid`, never the merge result.
- Branch with no PR: say up front that PR metadata and discussion are unavailable, then resolve the base as user-supplied, `git town config get-parent <branch>`, then `refs/remotes/origin/HEAD`. Never assume the default branch for a stacked branch. Diff from the merge base.
- A **merged** PR still audits: the verdict becomes keep, follow-up, or revert, and every cut becomes a follow-up PR.
- Already audited this session and the head SHA is unchanged: keep the earlier findings, run only the step whose inputs changed, and say which.

Always fetch these too, because the answer often lives here and not in the diff:

- `gh pr view <n> --json comments,reviews` and `gh api repos/<o>/<r>/pulls/<n>/comments`, paginated. A reviewer saying "not the priority right now" is a primary input, not noise. A bot finding that contradicts the PR's own rule is a value signal, not a nit.
- `gh pr diff <n>` and `gh pr diff <n> --name-only`.
- `git log origin/<base> --oneline --grep=<feature keyword>`. What already shipped around this PR. A stale PR is often partly superseded by its own stack.
- `git log --oneline <baseRefOid> ^<headRefOid> -- <touched dirs>`. Has the base moved under it.

Open full changed files at the relevant refs, including base versions.

## Step 2: Verify the claims against the base branch

Write down, one line each, every factual claim the PR rests on: "X is broken today", "X is reachable by a user today", "this value wins over that one", "this race can happen". These are hypotheses. The PR body is the author's belief, written from inside the change.

**Never accept a premise from the PR body.** Read the code as it exists on `baseRefOid` and prove or break each claim, following the `prove-it` skill when the repo has one. Map its labels onto:

| Verdict       | Meaning                                                                     |
| ------------- | --------------------------------------------------------------------------- |
| **VERIFIED**  | Proven from code, a test, real data, or a log. Cite `file:line`.            |
| **PLAUSIBLE** | The mechanism exists, nobody has observed it. Say so.                       |
| **UNKNOWN**   | Evidence unavailable or inconclusive. Name the check that would resolve it. |
| **REFUTED**   | The claim does not hold. It becomes the first TL;DR bullet.                 |

REFUTED is the verdict `prove-it` lacks, and the one that most often changes the outcome. Cite code as revision plus `file:line`; cite the exact test, log, query, ticket, or provider document otherwise. Never turn missing non-code evidence into a fake file citation.

Delegate this. Verification is read-only and fans out well: group related claims, at most three clusters, one `claim-verifier` subagent each (or a general read-only one where that agent is unavailable), all spawned in a single message so they run concurrently. Tell each to return `file:line` evidence and to say plainly when the claim does **not** hold. Give any agent that runs git commands worktree isolation and forbid checkout/stash/commit. Audit small PRs directly.

**Three checks decide most verifications. Run them first:**

1. **The exposure chain.** For "this is live and unprotected", find the setting or flag, its **default**, and **who can flip it**. A `z.boolean().default(false)` behind a staff-only permission is a controlled beta, not a production incident. Then write the full AND-chain of conditions a real user must satisfy to hit the bug. A four-term AND-chain is a rare bug, however severe each term reads on its own.
2. **Who wins at runtime.** For "the wrong value ships", trace the actual write order to the stored field. If the correct value overwrites the wrong one later in the pipeline, the PR is hardening, and the residue (a stale row, a leaked passthrough field) is the real damage. Price it as residue, not as data corruption. A test on the base branch asserting the precedence is the strongest possible evidence, look for it.
3. **Capability is not exposure.** A nullable scope column, a schema-supported layer, an unused parameter: check for the **write path**. When only a test fixture or raw SQL can create the state, everything guarding that state is SPECULATIVE in step 3.

For a race claim, name both operations, the ordering window, and the reproduction or runtime observation. For external behavior, use captured samples or provider documentation, never the PR description.

## Step 3: Cut the diff into units of value

Ignore file boundaries. Group the diff into the smallest independent things that could each ship or be dropped alone. For each:

- **Who is the actor?** An engineer, the paying customer, their end customer, a background sync. A guard that only stops an internal engineer is worth much less than one that stops an end customer with no way forward.
- **What breaks if this piece is deleted?** Concretely. "A stale row exists" and "the end customer cannot finish setup" are different orders of magnitude.
- **Has the trigger been observed?** An incident, a ticket, a log line, a failing test. Or reasoning from code alone.
- **Is it already handled elsewhere?** Check sibling surfaces: the UI, a REST twin, an earlier merged PR in the same stack. Note when two surfaces resolve the same conflict differently, and either justify the difference by actor or unify them.

Label each unit, recording its approximate hand-written lines:

- **ESSENTIAL**: verified problem, real actor, deleting it brings the problem back. Backed by observed demand or a binding incident, ticket, production signal, provider change, contract, compliance, security, or launch requirement.
- **DEFENSIVE**: closes a real but unobserved window. **No default verdict.** Every defensive unit gets its own keep-or-cut ruling, argued through the three questions below.
- **SPECULATIVE**: guards a state nobody can reach, or belongs to a later phase. **Default is remove.** The burden of proof sits on the code: it stays only if validation shows near-certain value. "Might be useful later" never meets that bar. Later can add it back with the phase that needs it.
- **FREE**: drive-by cleanup that costs nothing. Keep only when trivial, inseparable, and harmless to the PR's intent; otherwise separate it.

**Interrogating a DEFENSIVE unit**: answer all three, then rule:

1. **Is the window real?** Demand evidence: a test that reproduces it, a real-data sample, a documented precedent, a log line. Reasoning-from-code alone downgrades the unit to SPECULATIVE.
2. **What does it cost?** Not just lines. Extra queries per request, a new failure mode (a timeout, a throw on a happy path), API surface, a second place the same rule now lives. A guard whose failure mode is worse than the window it closes is a cut.
3. **What is the residue if the window is hit without the guard?** A stale row that self-heals next sync is cheap residue; wrong data reaching a customer is not. Price the guard against the residue, and say plainly when the guard only _mitigates_ rather than removes it.

**Validating a SPECULATIVE unit before cutting it**: cutting is also a claim, so verify it: hunt for the write path, the trigger, the caller that would make the state reachable. If the hunt finds one, relabel to DEFENSIVE or ESSENTIAL with the evidence. If it finds only a test fixture, raw SQL, or a roadmap item, cut the unit **and its cascade**: the tests proving it, the parameters threading it, the types imported for it.

## Step 4: Duplication and YAGNI sweep, mandatory, never skipped

This step always runs, and the report always says what was searched, even when nothing is found. "No duplication found" is only allowed after naming the searches that came back empty. Delegate it as its own subagent alongside the claim verifiers: it needs the base branch, not the conversation.

**Duplication hunt**: for every new symbol the diff introduces, ask the base branch if it already exists:

- **New helper or function**: grep the base for an existing equivalent by behavior, not by name (the house convention often names the same concept differently). A thin wrapper over an existing shared helper is a duplicate.
- **New test**: grep the base's specs for the behavior it asserts. A new spec that re-tests a shared helper through a wrapper duplicates the helper's own spec. Cite the existing coverage `file:line` when cutting.
- **New type, constant, or scope object**: search for the shape it mirrors. Two definitions of the same concept drift apart; the finding is the second definition, not the style.
- **Same rule, second home**: when the diff enforces a rule that another surface already enforces, either the actors differ (say how) or it is duplication.

**Deleted-test ruling**: when the diff removes or collapses test cases, rule each one:

- **MOVED**: cite the `file:line` that covers the behavior now. The _same_ behavior. An output-literal case does not cover an input-boundary case, and an integer through a boundary does not prove a fraction survives it.
- **LOST**: name the regression that now ships unnoticed.

Collapsing several inputs into one is fine only when no content-dependent branch existed to lose.

**Extra-complexity hunt**: complexity beyond what the PR's verified problem needs:

- **Test-only API surface.** An optional parameter or injectable dependency whose only non-production caller is the spec. Make it required, fix the spec.
- **The same lookup run several times.** Count the queries one request now makes. Two in the same function usually merge into one.
- **A widened blast radius bought with a narrow guarantee.** The classic: a batch `$transaction([...])` becomes interactive `$transaction(async tx => ...)` to make a check atomic. In Prisma that **adds a 5s timeout ceiling the batch form does not have**, on a customer-facing path. Ask what the residue is if the race is lost. Check-then-write outside the transaction is usually the better trade.
- **Plumbing that only one dropped feature needed.** After cutting a unit, re-check what parameters, helper functions, and type imports become dead. Cuts cascade.
- **One caller, one abstraction.** A helper or scope object with a single call site stays inlined until the second caller appears.
- **Guards on states an earlier guard or the type system already excludes.**

**Assumption ledger**: every assumption in the code or its tests ends the audit as exactly one of two things:

- **A fact**, with the evidence cited (`file:line`, a test, real data, a documented precedent), or
- **A cut**, because it only exists for an imagined future. That is YAGNI: code carried for a capability nobody reached, a phase not started, a caller that does not exist. Name the assumption, name what deleting it removes (usually nothing), and cut it with its cascade.

An assumption never survives as an assumption. "Probably fine" and "might need it later" are both spelled _delete_.

For every simplification, say what value is lost. "None" is valid, common, and the strongest thing you can write, but only after checking the delete-consequence.

## Step 5: Slicing check, vertical, never horizontal

A shrink recommendation is only as good as its slice. Judge the shape before naming one.

**Vertical** means one end-to-end change someone outside the team can notice: the actor hits the fixed behavior on merge. **Horizontal** means a layer, shipped in the hope the layers above arrive later.

- A PR whose value depends on a later PR is a layer. Name it as a finding.
- A stack where the customer-visible PR sits several merges deep is sliced wrong, whatever its total size.
- Layers written and then abandoned cost more to unwind than the vertical slice costs to build. Unshipped code is the most expensive kind.
- The test: **can you state the slice as one sentence about what an actor can now do?** If the sentence needs "so that later we can", it is horizontal.
- Cutting the other way is also wrong: do not manufacture a stack to make a PR look smaller. If the narrowest useful end-to-end slice is still big, that is the honest answer.

## Step 6: Report

Open with **TL;DR**: the proposed changes as bullets, and nothing else. One line each, verb first, naming the file or the PR it lands in. No preamble, no restating what the PR does, no "this audit found". Order by what you would do first, and a REFUTED claim always comes first. Nothing to change is one line saying so.

    **TL;DR**
    - Cut the tenant-scope tests, no write path exists (`ownership.spec.ts`)
    - Keep `$transaction([...])`, check ownership before it (`mappings.ts`)
    - Rewrite the PR body, two claims are false

Then the verdict:

- **Ship**: problem verified, scope right, units proportionate.
- **Shrink**: name the smallest **vertical** slice that still fixes the verified problem, with a line estimate, and list what moves out and which later slice it joins.
- **Shelve**: the premise did not hold, or the trigger is unreachable until a later phase. Say what would make it worth reopening.

A central UNKNOWN blocks a confident Ship but does not prove demand absent. Never recommend reverting merged work solely because a source is inaccessible; require a refuted premise or demonstrated harm.

Then, in order. Sections 4 to 6 are never omitted; an empty one states what was searched and found clean:

1. **Importance**, in terms of consequence and actor, plus the AND-chain from step 2's exposure check.
2. **The claim table** with verdicts.
3. **Units of value**, labelled, each with its delete-consequence.
4. **Duplications**, each with the existing `file:line` it duplicates, or the searches that came back empty.
5. **Extra complexity and YAGNI cuts**, each with its value-lost line, plus the assumption ledger: every assumption resolved to a cited fact or a cut.
6. **Simplifications** that are neither of the above, each with its value-lost line.
7. **Confidence**, 1 to 5, plus the one thing that would raise it. When that thing is a production query, name the query.

If the PR body contains a claim you proved false, say so explicitly and say the description needs rewriting. A wrong premise in the body makes every reviewer after you agree with it.

## Rules

- The audit must not be slop either. Never call a piece unnecessary without opening the code that would break. Never call a bug real without tracing the write order on the base branch.
- A reviewer's prioritisation call outranks your read of the code's elegance. If a teammate already said "not now", produce evidence that beats that call or agree with it. Bot findings (Greptile, Cursor Bugbot) are signals to verify, not to accept. Treat team decisions as constraints, not proof.
- Judge size by hand-written lines per the `high-level-pr-review` skill when present, also excluding generated code, captured samples, and coverage reports.
- Test count is not value. A large spec proving a speculative guard is speculative code.
- Findings bigger than the PR (a missing permission, an unrelated data leak) get named separately as their own ticket, never folded into the verdict on this PR. Recommend them, do not create them.
- Do not post anything to GitHub unless asked. This is an audit for the author.

For repo-specific shortcuts (permission model, pipeline order, how to run specs, where production evidence lives), load the repo's own audit notes skill when one exists.
