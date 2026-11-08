---
name: vertical-slice
description: "Use when planning a feature or splitting it into PRs: smallest end-to-end outcome, acceptance scenario, deployable slices."
---

# Slice vertically

- Start with the smallest customer-visible end-to-end outcome. State one acceptance scenario and the non-goals first, and cut work the scenario does not need.
- Make each feature PR deployable and usable alone, sliced across UI, API, persistence, and runtime as the outcome needs. Stack PRs only when each delivers value alone.
- Start with one simple interface and one narrow config scope. Defer extras until customers ask; keep the safety rules production needs.
- Stay in the issue's scope. Unrelated work gets a follow-up issue.
- Green checks and tidy commits are gates. The acceptance scenario proves value.
