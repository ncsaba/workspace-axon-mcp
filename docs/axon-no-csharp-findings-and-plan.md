# Axon Fork Status and Forward Plan (No-C# Baseline)

## Snapshot Date

- 2026-03-19

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
| File instance / content separation | `✅` | Lifecycle/query correctness, incremental git parity, content-ID-based refresh, shared-chunk association, and reset-schema full-suite validation are landed. Remaining cleanup is documentation/test-environment alignment, not a runtime blocker. |
| Python discovery + symbol extraction | `✅` | `.py` is discovered, routed to `PythonParser`, and symbol extraction is active. |
| Python semantic extraction depth | `🚧` | Imports are parsed, but graph relations, call edges, and endpoint extraction are still mostly absent. |
| Java discovery + parser routing | `✅` | `.java` is discovered and routed to `JavaParser`. |
| Java semantic extraction depth | `🚧` | Basic symbols present; cross-file semantics not at target fidelity. |
| Docs/config structural depth | `🚧` | Present but uneven across formats. |

## Capability Comparison: Axon vs kilocode (Reference)

`✅` stronger, `🚧` mixed/partial, `🛑` blocked/missing.

| Capability | Axon | kilocode | Practical takeaway |
| --- | --- | --- | --- |
| Parser coverage breadth | `🚧` | `✅` | Adopt broader registry/query-pack patterns. |
| Fallback chunking policy | `🛑` | `✅` | Add centralized fallback policy in Axon. |
| Python semantic graph edges | `🛑` | `🚧` | Use Python as the next parity track because parser and symbol foundations already exist. |
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
| A. Stabilize no-C# baseline | `✅` | Freeze current truth in docs and configs. | `🔥` drift if docs are not updated with code changes. |
| B. File instance/content separation | `✅` | Runtime slice is landed; only branch-doc and test-environment alignment remain. | `🔥` stale docs can hide the real branch state and cause redundant cleanup work. |
| C. Python semantic parity | `🧭` | Land Python import relations first, then Python call edges and framework endpoint extraction on the shared language-strategy seams. | `🔥` current call graph path assumes tree-sitter AST nodes, so Python call parity will need an AST-compatible strategy path instead of a JS/Java copy. |
| D. Java validation + completion | `🧭` | Close benchmark-backed parity validation and any remaining precision gaps without reopening the critical path. | `🔥` shared benchmark repos may expose unresolved Java edge cases despite the current checklist being mostly complete. |
| E. Unified parser platform | `🧭` | Central registry, capability flags, fallback chunking. | `🔥` refactor may cause temporary extractor regressions. |
| F. Quality and ranking | `🧭` | Relation confidence and summary quality improvements. | `🔥` quality metrics require representative real repos. |

## Immediate Next Steps

1. Sync canonical docs/roadmaps and handover text to the shipped state on `file-instance-content-separation`.
2. Finish the dedicated test-database default/configuration cleanup and verify the suite works with the devcontainer defaults.
3. Start Python semantic parity with the smallest vertical slice:
   - add Python import relation persistence on top of the existing `PythonParser` import output
   - add focused integration coverage for intra-repo Python imports, including `from ... import ...` and relative imports
4. Use the Python import slice to define the AST/strategy contract needed for later Python call and endpoint extraction.
5. Keep the later semantic-search overhaul separate:
   - use kilocode-inspired parser-backed chunking ideas as inspiration
   - do not block Python quick wins on a full parser-platform refactor

## Reference Paths

- Axon source: `/workspaces/axon-mcp/axon-src`
- kilocode reference (read-only): `/workspaces/axon-mcp/external-inspiration/kilocode`
