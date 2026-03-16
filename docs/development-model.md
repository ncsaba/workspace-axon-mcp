# Development Model

This workspace uses iterative, dependency-driven delivery focused on small validated increments.

## Core Philosophy

1. Build enabling foundations before specialization.
2. Prefer thin vertical slices that unlock the next capability.
3. Validate in real runtime conditions early (integration-first).
4. Keep interfaces explicit where future language divergence is expected.
5. Continuously feed implementation learnings back into docs and plan.

`✅` required, `⚠️` recommended, `⛔` prohibited.

| Rule | Area | Requirement |
| --- | --- | --- |
| `✅` | Delivery slicing | Use the smallest working increment that unlocks the next dependency. |
| `✅` | Validation mode | Validate against real infrastructure when behavior depends on runtime integration. |
| `✅` | Doc sync | Keep documentation synchronized in the same change stream as code. |
| `⚠️` | Interface design | Prefer explicit language strategy interfaces where divergence is expected. |
| `⛔` | Documentation drift | Do not leave docs, tables, or diagrams stale relative to shipped behavior. |

## Core Loop

1. Define high-level scope for the next increment.
2. Select the most foundational dependency-blocking work item.
3. Update plan/design docs for the exact increment (non-trivial changes).
4. Implement the smallest working slice.
5. Validate in real conditions and capture verification evidence.
6. Update docs to match shipped behavior in the same change stream.
7. Re-prioritize based on what was learned; repeat.

## Documentation-Driven Execution

Documentation is part of implementation, not a follow-up.

`✅` required, `⚠️` recommended.

| Rule | Requirement |
| --- | --- |
| `✅` | Non-trivial work starts with a plan/design update in canonical docs. |
| `✅` | High-level intent stays in roadmap/overview docs; implementation detail stays subsystem-local. |
| `✅` | Every completed increment updates documentation in the same session. |
| `✅` | If code and docs diverge, align docs before marking complete. |
| `⚠️` | Avoid duplicate docs and link to canonical sources. |

## Documentation Style Standard

Optimize for one-glance comprehension.

`✅` required.

| Rule | Requirement |
| --- | --- |
| `✅` | Use compact tables for capability status, options, and tradeoffs. |
| `✅` | Use Mermaid diagrams for non-trivial runtime flows. |
| `✅` | Use consistent status markers within each document. |
| `✅` | If symbolic tags are used, include a short local icon key in that section. |
| `✅` | Keep diagrams/tables synchronized with actual behavior. |

Recommended status markers:
- `✅` complete
- `🚧` partial/incomplete
- `🛑` blocked/not available
- `🧭` next action
- `🔥` risk

## Testing and Validation Policy

1. Primary validation is integration behavior in real local infrastructure.
2. Unit tests are useful but not the default first gate for exploratory or infrastructure-heavy changes.
3. Run focused regression checks in impacted areas.
4. Keep test effort proportional to change risk and system criticality.

## Session Contract

At session start:
1. Read current baseline docs in the required order (`AGENTS.md`).
2. Map the target increment to roadmap/capability matrix.
3. Update plan docs first for non-trivial changes.

At session end:
1. Sync docs with final behavior.
2. Record verification outcomes.
3. Leave explicit next steps and open risks.
