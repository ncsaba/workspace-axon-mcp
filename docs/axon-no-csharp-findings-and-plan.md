# Axon Fork Status and Forward Plan (No-C# Baseline)

## Snapshot Date

- 2026-03-20

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
| File instance / content separation | `✅` | **MERGED into master.** Lifecycle/query correctness, incremental git parity, content-ID-based refresh, shared-chunk association, and reset-schema full-suite validation are complete. |
| Python discovery + symbol extraction | `✅` | `.py` is discovered, routed to `PythonParser`, and symbol extraction is active. |
| Python semantic extraction depth | `🚧` | Import graph, call relations, and FastAPI/Flask endpoint extraction landed. Remaining: retrieval quality, import parsing expansion. |
| Java discovery + parser routing | `✅` | `.java` is discovered and routed to `JavaParser`. |
| Java semantic extraction depth | `🚧` | Basic symbols present; cross-file semantics need benchmark validation. |
| Docs/config structural depth | `🚧` | Present but uneven across formats. |

## Capability Comparison: Axon vs kilocode (Reference)

`✅` stronger, `🚧` mixed/partial, `🛑` blocked/missing.

| Capability | Axon | kilocode | Practical takeaway |
| --- | --- | --- | --- |
| Parser coverage breadth | `🚧` | `✅` | Adopt broader registry/query-pack patterns. |
| Fallback chunking policy | `🛑` | `✅` | Add centralized fallback policy in Axon. |
| Python semantic graph edges | `🚧` | `🚧` | Import/call/endpoint extraction landed; retrieval quality ongoing. |
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
| C. Python semantic parity | `🚧` | Import/call/endpoint extraction landed. Retrieval quality and benchmark validation ongoing. | `🔥` retrieval quality metrics require representative real repos. |
| D. Java validation + completion | `🧭` | Close benchmark-backed parity validation and any remaining precision gaps. | `🔥` shared benchmark repos may expose unresolved Java edge cases. |
| E. Unified parser platform | `🧭` | Central registry, capability flags, fallback chunking. | `🔥` refactor may cause temporary extractor regressions. |
| F. Quality and ranking | `🧭` | Relation confidence and summary quality improvements. | `🔥` quality metrics require representative real repos. |

## Immediate Next Steps

1. **Python retrieval quality validation**
   - Semantic chunk coherence
   - Corpus discipline
   - Benchmark evidence versus kilocode-style chunking

2. **Python import parsing expansion** (optional enhancement)
   - Aliases, structured import records
   - Wildcard typing, dynamic imports
   - `__init__.py` re-export semantics

3. **Java benchmark validation**
   - Confirm current Java breadth on shared repos
   - Close any exposed edge cases

4. **Parser platform consolidation** (Phase E)
   - Central registry, capability flags
   - Fallback chunking policy

## Reference Paths

- Axon source: `/workspaces/axon-mcp/axon-src`
- kilocode reference (read-only): `/workspaces/axon-mcp/external-inspiration/kilocode`
- Session handover: `/workspaces/axon-mcp/docs/SESSION_HANDOVER.md`
