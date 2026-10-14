# Axon Fork Status and Forward Plan (No-C# Baseline)

## Snapshot Date

- 2026-10-14 (branch `javampire`, HEAD `6388af6`)

## Objective

Build the strongest practical code indexer from this fork by combining:

- Axon's symbol/relation graph and MCP query surface
- kilocode's tree-sitter language/query breadth and fallback chunking strategy

## Current State (Confirmed)

`✅` done/available, `🚧` partial, `🛑` gap.

| Area | Status | Notes |
| --- | --- | --- |
| C# / Roslyn runtime removal | `✅` | Runtime path removed; Alembic migrations for production upgrades. |
| Runtime baseline (Py 3.11 + PG17/pgvector + Redis) | `✅` | Available in dev-container; Celery worker is manual start. |
| File instance / content separation | `✅` | **MERGED into master.** Lifecycle/query correctness, incremental git parity, content-ID-based refresh, shared-chunk association, and schema validation are complete. |
| Python discovery + symbol extraction | `✅` | `.py` is discovered, routed to `PythonParser`, and symbol extraction is active. |
| Python semantic extraction depth | `✅` | Import graph, call relations, FastAPI/Flask endpoints, structured import records, `__init__.py` re-exports. Retrieval validation passed 6/6 (2026-03-21). |
| Java discovery + parser routing | `✅` | `.java` is discovered and routed to `JavaParser`. |
| Java semantic extraction depth | `🚧` | Basic symbols present; cross-file semantics need benchmark validation. |
| Docs/config structural depth | `🚧` | Present but uneven across formats. |
| Multi-branch / multi-developer tracking | `🚧` | **Current focus.** Phase 2.5.0 baseline done; 2.5.1 git tracking schema + backfill landed, sync wiring open. |

## Capability Comparison: Axon vs kilocode (Reference)

`✅` stronger, `🚧` mixed/partial, `🛑` blocked/missing.

| Capability | Axon | kilocode | Practical takeaway |
| --- | --- | --- | --- |
| Parser coverage breadth | `🚧` | `✅` | Adopt broader registry/query-pack patterns. |
| Fallback chunking policy | `🛑` | `✅` | Add centralized fallback policy in Axon. |
| Python semantic graph edges | `✅` | `🚧` | Import/call/endpoint/re-export extraction landed; retrieval validated. |
| Java semantic graph edges | `🚧` | `🚧` | Java breadth is ahead of Python, but validation on shared benchmark repos still remains. |
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
| A. Stabilize no-C# baseline | `✅` | Frozen in docs and configs. | |
| B. File instance/content separation | `✅` | **MERGED into master.** All runtime work complete. | |
| C. Python semantic parity | `✅` | Import/call/endpoint/re-export extraction landed; retrieval validation passed 6/6. | |
| G. Multi-branch / multi-developer tracking | `🧭` | **Active.** Phase 2.5 plan in `axon-src/docs/architecture/multi_branch_tracking_implementation_plan.md`. | `🔥` FILE_INSTANCE → TREE_FILE migration touches all read paths. |
| D. Java validation + completion | `🧭` | Close benchmark-backed parity validation and any remaining precision gaps. | `🔥` shared benchmark repos may expose unresolved Java edge cases. |
| E. Unified parser platform | `🧭` | Central registry, capability flags, fallback chunking. | `🔥` refactor may cause temporary extractor regressions. |
| F. Quality and ranking | `🧭` | Relation confidence and summary quality improvements. | `🔥` quality metrics require representative real repos. |

## Immediate Next Steps

Language phases D-F are paused while Phase G (multi-branch tracking) is active. Detailed status: `/workspaces/axon-mcp/docs/SESSION_HANDOVER.md`.

1. **Finish Phase 2.5.1** - Write commits/branches/tags/tree files from the repository sync path
2. **Phase 2.5.2** - User registry with Keycloak sync
3. **Phase 2.5.3** - Move FILE_INSTANCE reads onto TREE_FILE

Paused backlog: Java benchmark validation (D), parser platform consolidation (E), quality and ranking (F).

## Reference Paths

- Axon source: `/workspaces/axon-mcp/axon-src`
- kilocode reference (read-only): `/workspaces/axon-mcp/external-inspiration/kilocode`
- Session handover: `/workspaces/axon-mcp/docs/SESSION_HANDOVER.md`
