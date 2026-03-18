# Axon Fork Status and Forward Plan (No-C# Baseline)

## Snapshot Date

- 2026-03-18

## Objective

Build the strongest practical code indexer from this fork by combining:

- Axon's symbol/relation graph and MCP query surface
- kilocode's tree-sitter language/query breadth and fallback chunking strategy

## Current State (Confirmed)

`✅` done/available, `🚧` partial, `🛑` gap.

| Area | Status | Notes |
| --- | --- | --- |
| C# / Roslyn runtime removal | `✅` | Runtime path removed; no backward-compat migration constraints. |
| Runtime baseline (Py 3.11 + PG17/pgvector + Redis) | `✅` | Available in dev-container; Celery worker is manual start. |
| File instance / content separation | `🧭` | Lifecycle/query correctness, incremental git parity, content-ID-based refresh, shared-chunk association, and reset-schema full-suite validation are landed; remaining work is primarily branch-doc closure. |
| Java discovery + parser routing | `✅` | `.java` is discovered and routed to `JavaParser`. |
| Java semantic extraction depth | `🚧` | Basic symbols present; cross-file semantics not at target fidelity. |
| Docs/config structural depth | `🚧` | Present but uneven across formats. |

## Capability Comparison: Axon vs kilocode (Reference)

`✅` stronger, `🚧` mixed/partial, `🛑` blocked/missing.

| Capability | Axon | kilocode | Practical takeaway |
| --- | --- | --- | --- |
| Parser coverage breadth | `🚧` | `✅` | Adopt broader registry/query-pack patterns. |
| Fallback chunking policy | `🛑` | `✅` | Add centralized fallback policy in Axon. |
| Java semantic graph edges | `🛑` | `🚧` | Axon should add Java-specific extractors and keep graph-first model. |
| Graph-native relations for MCP tools | `✅` | `🚧` | Keep Axon graph core as differentiator. |

## What "Best of Both" Means

Keep Axon's graph-centric architecture as the core and import these patterns from kilocode:

1. Centralized extension registry and parser capability matrix.
2. Language query packs with consistent capture naming.
3. First-class fallback chunking policy when parser/query quality is insufficient.
4. Broader integration coverage for language parser/query behavior.

## Roadmap

`✅` completed, `🧭` next action, `🔥` risk.

| Phase | Status | Focus | Risk |
| --- | --- | --- | --- |
| A. Stabilize no-C# baseline | `✅` | Freeze current truth in docs and configs. | `🔥` drift if docs are not updated with code changes. |
| B. File instance/content separation | `🧭` | Close the branch docs and explicitly mark the shipped state now that the shared-chunk association cut and full reset-schema validation are landed. | `🔥` stale docs can hide the real branch state and cause redundant cleanup work. |
| C. Java semantic parity | `🧭` | Imports/calls/endpoints/dependencies via language strategies after lifecycle/query correctness is stabilized. | `🔥` parser metadata may be insufficient for high precision at first pass. |
| D. Unified parser platform | `🧭` | Central registry, capability flags, fallback chunking. | `🔥` refactor may cause temporary extractor regressions. |
| E. Quality and ranking | `🧭` | Relation confidence and summary quality improvements. | `🔥` quality metrics require representative real repos. |

## Immediate Next Steps

1. Sync canonical docs/roadmaps to the shipped state and record that reset-schema validation plus the full suite are green on the current branch worktree.
2. Decide whether to explicitly close the lifecycle/content branch phase now that the schema/runtime cut is landed.
3. Resume Java semantic parity work once Phase B is marked complete.

## Reference Paths

- Axon source: `/workspaces/axon-mcp/axon-src`
- kilocode reference (read-only): `/workspaces/axon-mcp/external-inspiration/kilocode`
