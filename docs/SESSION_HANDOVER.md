# Session Handover

All paths below are relative to `/workspaces/axon-mcp/axon-src` unless otherwise stated.

## Session Focus

Last updated: 2026-10-14 (housekeeping session, no code changes).

Active focus: **multi-branch / multi-developer tracking** (see [Phase 2.5 status](#phase-25-multi-branch-tracking-status)).
Language support work is paused.

Current branch:

- `javampire` (owned by us; tracked on both `origin` and `mapp` remotes)

Current HEAD:

- `6388af6` - `feat: add Python re-exports and Git tracking foundations` (2026-09-30)

Branch hygiene (verified 2026-10-14):

- All other local and remote-tracking branches, including Charlie Albietz's `origin/charlie`, are fully contained in `javampire`.
- `master` / `mapp/master` stay at `179f312`; `javampire` is ahead by the Python import/re-export work, Charlie's repo connection/registration work, and the Git tracking foundation.
- Remotes cannot be fetched from inside the dev-container (no SSH access); fetch from the host.

## What Was Completed (Previous Sessions)

### Phase 1: File Instance/Content Separation ✅ COMPLETE

All work from the `file-instance-content-separation` branch has been merged into `master`:

1. **Alembic migration baseline** - Backwards-compatible schema migrations for production
2. **Manual DB reset workflow** - `scripts/reset_db.py` for dev/test environments only
3. **DEBUG env parsing fix** - `DEBUG=release` normalized to `False`
3. **Lifecycle validation** - `tests/integration/test_file_lifecycle_transitions.py`
4. **Sync-worker lifecycle validation** - `tests/integration/test_sync_lifecycle_transitions.py`
5. **Active-instance read-path cleanup** - User-facing surfaces exclude `MISSING` instances
6. **Shared-chunk association cut** - `ChunkSymbolLink` is the association layer
7. **Legacy compatibility removal** - `File = FileInstance` alias removed, `file_id` synonyms removed
8. **Alembic baseline alignment** - Matches current instance/content schema
9. **Test DB defaults alignment** - `TEST_DATABASE_URL` distinct from `DATABASE_URL`

### Phase 2: Python Semantic Parity ✅ BASELINE COMPLETE (further work paused)

Recent commits landed Python quick wins:

1. **Python import graph** - `IMPORTS` edges for intra-repo imports
2. **Python call graph strategy** - `CALLS` edges without tree-sitter-only assumptions
3. **Python endpoint extraction** - FastAPI/Flask baseline endpoint extraction
4. **Python decorator-aware retrieval chunk slice**
5. **Call-neighbor retrieval chunk context**

Key files added/modified:

- `src/extractors/api_extractor.py` - API endpoint extraction
- `src/extractors/call_analyzer.py` - Call analysis utilities
- `src/extractors/call_graph_builder.py` - Call graph construction
- `src/extractors/import_resolver.py` - Import resolution
- `src/extractors/path_resolver.py` - Path resolution
- `src/parsers/python_parser.py` - Python parser enhancements
- `src/embeddings/symbol_chunker.py` - Symbol chunking improvements

Integration tests added:

- `tests/integration/test_python_api_endpoint_extraction.py`
- `tests/integration/test_python_call_relationships.py`
- `tests/integration/test_python_import_relationships.py`

## Current State Snapshot

`✅` done, `🚧` partial, `🧭` next.

| Area | Status | Notes |
| --- | --- | --- |
| File instance/content architecture | `✅` | Merged into master |
| Core ORM entities | `✅` | `RepositoryIndexRun`, `FileInstance`, `FileContent`, `ChunkSymbolLink` |
| Run-ID stamping through sync/discovery/parsing path | `✅` | `current_run_id` threaded through main write path |
| Successful-run missing finalization | `✅` | Older active rows become `MISSING` after successful sync |
| Failed-run no-sweep behavior | `✅` | Verified by sync-path integration test |
| Reactivation of previously missing files | `✅` | Verified by lifecycle integration test |
| TTL cleanup worker and orphan content reclamation | `✅` | Verified by lifecycle integration test |
| Alembic migration baseline | `✅` | Backwards-compatible schema migrations for production |
| Manual DB reset workflow | `✅` | Dev/test environments only via `scripts/reset_db.py` |
| Active-instance read paths | `✅` | User-facing surfaces exclude `MISSING` by default |
| Incremental git sync parity | `✅` | Lifecycle-aware instance/content handling |
| Parse/embed orchestration via `changed_content_ids` | `✅` | Content IDs as durable refresh contract |
| Shared-chunk association model | `✅` | `ChunkSymbolLink` landed |
| Python import relations | `✅` | `IMPORTS` edges for intra-repo imports |
| Python call relations | `✅` | `CALLS` edges with AST-compatible strategy |
| Python endpoint extraction | `✅` | FastAPI/Flask baseline |
| Python retrieval quality | `✅` | **Validated 2026-03-21: 6/6 checks passed** |
| Python structured imports + `__init__.py` re-exports | `✅` | Landed 2026-03-22 |
| Repo connections + easy registration/deletion (Charlie) | `✅` | In `javampire` since 2026-03-20 |
| Multi-branch baseline data (Phase 2.5.0) | `✅` | `workspace-axon-mcp` + `jverein` indexed, DB dump archived |
| Git tracking schema (commit/tree-file/branch/tag) | `🚧` | Tables, migration and backfill landed; runtime sync/indexing does not write them yet |
| User registry (Keycloak sync) | `🧭` | No `users` table yet |
| Java semantic depth | `🚧` | Paused. Not yet at target for imports/calls/endpoints/dependencies |
| Parser platform consolidation | `🧭` | Paused. Capability matrix integration, strategy interfaces |

## Python Retrieval Quality Validation Results (2026-03-21)

**Status: ✅ ALL6 CHECKS PASSED**

Validation script: `scripts/validate_python_retrieval.py`
Results file: `docs/python_retrieval_validation_results.json`

### Benchmark Details

| Check | Status | Details |
| --- | --- | --- |
| Import Relations | ✅ | 45 symbols with expected import patterns, all have context |
| Call Relations | ✅ | 268 function/method symbols with call relationships |
| Endpoint Extraction | ✅ | 53 ENDPOINT symbols, 302 potential route handlers |
| Chunk Coherence | ✅ | Results found for 4/4 semantic queries |
| Call-Neighbor Context | ✅ | 10 helper/utility functions with context available |
| Python Symbol Coverage | ✅ | 2754 Python symbols: 913 functions, 1131 methods, 323 classes |

### Symbol Distribution

| Kind | Count |
| --- | --- |
| METHOD | 1131 |
| FUNCTION | 913 |
| CLASS | 323 |
| VARIABLE | 256 |
| CONSTANT | 63 |
| ENDPOINT | 53 |
| MODULE | 15 |

## Session 2026-03-22: Docker Tooling Alignment ✅ COMPLETE

### Completed Work

1. **Multi-container fixes** (`docker/docker-compose.yml`)
   - Added `inventory` queue to worker service
   - Made `VITE_API_BASE_URL` configurable via `.env`

2. **Single-container deployment** (NEW)
   - `docker/Dockerfile.standalone` - All-in-one image with PostgreSQL, Redis, all services
   - `docker/supervisord.standalone.conf` - Process supervisor configuration
   - `docker/standalone-entrypoint.sh` - Initialization script (extracted from Dockerfile)
   - `docker/create-test-db.sh` - Optional test database creation script

3. **Database initialization** (`docker/init-db.sql`)
   - Production database initialization only
   - pgvector extension enabled
   - Test database creation moved to separate script

4. **Environment configuration** (`.env.example`)
   - Added deployment mode notes (dev-container, multi-container, single-container)
   - Added `REDIS_PASSWORD` variable
   - Added `VITE_API_BASE_URL` for UI configuration

5. **Deployment documentation** (`DEPLOY-README.md`)
   - Complete deployment guide for all three modes
   - Architecture diagrams
   - Quick start commands
   - Test database creation instructions
   - Troubleshooting section
   - Security checklist

### Files Created/Modified

| File | Change |
|------|--------|
| `docker/Dockerfile.standalone` | NEW - All-in-one single container image |
| `docker/supervisord.standalone.conf` | NEW - Supervisor config for standalone |
| `docker/standalone-entrypoint.sh` | NEW - Entrypoint script for standalone |
| `docker/create-test-db.sh` | NEW - Optional test database creation script |
| `docker/docker-compose.yml` | Fixed inventory queue, configurable UI URL, test-db script mount |
| `docker/init-db.sql` | Production DB only (test DB via script) |
| `.env.example` | Added deployment mode notes, new variables |
| `DEPLOY-README.md` | NEW - Complete deployment guide with test-db instructions |
| `docs/docker_tooling_assessment.md` | Assessment document |

### Deployment Options Summary

| Mode | Dockerfile | Use Case |
|------|------------|----------|
| Dev-container | N/A | VS Code development (primary) |
| Multi-container | `Dockerfile.optimized` | Production, scalable deployments |
| Single-container | `Dockerfile.standalone` | Demo, quick start, simple hosting |

## Session 2026-03-22: Python Import Parsing Expansion Phase 1 ✅ COMPLETE

### Completed Work

1. **Structured Import Records** (`src/parsers/base_parser.py`)
   - Added `ImportedSymbol` dataclass for symbol-level import info
   - Added `ImportRecord` dataclass with full import metadata
   - `ParseResult.import_records` field for structured data
   - `to_legacy_string()` for backward compatibility

2. **Python Parser Enhancement** (`src/parsers/python_parser.py`)
   - `_PythonAstVisitor` now produces structured `ImportRecord` objects
   - Handles: basic imports, aliased imports, from-imports, wildcards
   - Handles: relative imports (all levels)
   - Handles: conditional imports (try/except ImportError)
   - Handles: dynamic imports (importlib.import_module, __import__)
   - Maintains legacy `imports` list for backward compatibility

3. **Import Resolution Enhancement** (`src/extractors/import_resolver.py`)
   - `PythonImportExtractionStrategy` updated to use structured records
   - Added alias metadata to import relations
   - Added `is_dynamic` and `is_conditional` flags
   - Dynamic import detection via `_extract_dynamic_import()`

4. **Unit Tests** (`tests/unit/test_python_import_records.py`)
   - 25+ test cases covering all import patterns
   - Tests for edge cases (nested try/except, tuple exceptions)
   - Legacy compatibility tests

### Files Created/Modified

| File | Change |
|------|--------|
| `src/parsers/base_parser.py` | Added `ImportRecord`, `ImportedSymbol` dataclasses |
| `src/parsers/python_parser.py` | Enhanced AST visitor for structured imports |
| `src/extractors/import_resolver.py` | Updated strategy to use structured records |
| `tests/unit/test_python_import_records.py` | NEW - comprehensive unit tests |

### Import Patterns Now Supported

| Pattern | Example | Captured |
|---------|---------|----------|
| Basic import | `import os` | ✅ |
| Aliased import | `import numpy as np` | ✅ |
| From import | `from os import path` | ✅ |
| Aliased from | `from os import path as p` | ✅ |
| Wildcard | `from os import *` | ✅ |
| Relative | `from . import module` | ✅ |
| Multi-level relative | `from ..pkg import X` | ✅ |
| Conditional | `try: import X except ImportError:` | ✅ |
| Dynamic | `importlib.import_module("X")` | ✅ |

### Validation Command

```bash
cd /workspaces/axon-mcp/axon-src
source /home/vscode/.venv-dev/bin/activate
pytest tests/unit/test_python_import_records.py -v
```

---

## Session 2026-03-22: Python `__init__.py` Re-export Semantics ✅ COMPLETE

### Completed Work

1. **Re-export Resolver Module** (`src/extractors/reexport_resolver.py`)
   - `ReexportEntry` dataclass for individual re-export tracking
   - `PackageReexportMap` for per-package re-export organization
   - `ReexportResolver` class for parsing and resolving re-exports
   - Handles: basic re-exports, aliased re-exports, `__all__` filtering
   - Handles: relative imports (`.module`, `..sibling`)
   - Handles: wildcard re-exports (`from .module import *`)

2. **Import Resolution Integration** (`src/extractors/import_resolver.py`)
   - `PythonImportExtractionStrategy` now accepts optional `ReexportResolver`
   - Added `_resolve_via_reexport()` fallback method
   - `ImportRelationshipBuilder` creates and passes `ReexportResolver`
   - Resolution chain: direct lookup → re-export check

3. **Unit Tests** (`tests/unit/test_reexport_resolver.py`)
   - 20+ test cases covering all re-export patterns
   - Tests for `__all__` filtering behavior
   - Tests for nested package resolution
   - Tests for edge cases (empty files, circular references)

4. **Integration Tests** (`tests/integration/test_python_reexport_relationships.py`)
   - Basic re-export relationship validation
   - Aliased re-export relationship validation
   - Nested package re-export validation
   - `__all__` filtering validation

### Files Created/Modified

| File | Change |
|------|--------|
| `src/extractors/reexport_resolver.py` | NEW - Core re-export resolution module |
| `src/extractors/import_resolver.py` | Integrated re-export resolver |
| `tests/unit/test_reexport_resolver.py` | NEW - comprehensive unit tests |
| `tests/integration/test_python_reexport_relationships.py` | NEW - integration tests |

### Re-export Patterns Now Supported

| Pattern | Example | Captured |
|---------|---------|----------|
| Basic re-export | `from .module import Class` | ✅ |
| Aliased re-export | `from .module import Old as New` | ✅ |
| Multi-symbol | `from .module import A, B, C` | ✅ |
| Wildcard | `from .module import *` | ✅ |
| `__all__` filtering | `__all__ = ["Public"]` | ✅ |
| Relative parent | `from ..sibling import X` | ✅ |

### Validation Commands

```bash
cd /workspaces/axon-mcp/axon-src
source /home/vscode/.venv-dev/bin/activate
pytest tests/unit/test_reexport_resolver.py -v
pytest tests/integration/test_python_reexport_relationships.py -v
```

---

## Session 2026-03-22: Focus Shift to Multi-Branch and Multi-Developer Tracking 🧭 NEW FOCUS

### Direction Change

**Language support improvements are now paused.** The new focus is on:

1. **Multi-branch indexing** - Track and index symbols per branch/version
2. **Local changes tracking** - Push local changes to user's branch
3. **Multi-developer collaboration** - User registry, branch isolation, cross-version search

### Existing Foundation

| Component | Status | Notes |
|-----------|--------|-------|
| User tracking | 🚧 Partial | `AuditLog` has `user_id` but no user management |
| Git branch support | ✅ | Repositories cloned with full git history |
| Per-user isolation | 🛑 Missing | No tenant/user isolation in data model |
| Cross-version search | 🛑 Missing | Search is per-repository, not per-branch |
| Personal access tokens | ✅ | `PersonalAccessToken` table exists |
| Keycloak auth | ✅ | REST API + MCP token architecture documented |

### Reference Documentation

- Feature ideas: [`docs/feature-ideas/multi-user-mcp-collaboration.md`](../docs/feature-ideas/multi-user-mcp-collaboration.md)
- Auth architecture: [`docs/architecture/authentication_and_mcp_token_plan.md`](docs/architecture/authentication_and_mcp_token_plan.md)
- Keycloak guide: [`docs/guides/authentication_keycloak_and_mcp_tokens.md`](docs/guides/authentication_keycloak_and_mcp_tokens.md)

### Data Model Changes Needed (Superseded)

The initial `users` / `user_branches` / `branch_name` column sketch from this session was replaced by the approved commit/tree-based model in `/workspaces/axon-mcp/plans/multi_branch_brainstorm_baseline.md`. See the current status below.

---

## Sessions 2026-03-23 to 2026-09-30: Phase 2.5 Foundations

Summary of commit `6388af6` and the docs created with it:

1. **Phase 2.5.0 baseline data** ✅ - `workspace-axon-mcp` (Python, 11 files) and `jverein` (Java, 826 files) fully indexed with embeddings; dump archived at `.archive/baseline_test_data_complete_20260323.dump`. Summary: `docs/validation/phase_2.5.0_completion_summary.md`.
2. **Git tracking schema** 🚧 - `git_commits`, `tree_files`, `branches`, `tags` tables (`src/database/models/git_tracking.py`), migration `a1b2c3d4e5f1_add_git_tracking_tables.py` with backfill of commits, default branches and tree files.
3. **Models package split** ✅ - `src/database/models.py` became the `src/database/models/` package (`models_base.py` + `git_tracking.py`); legacy imports still work.
4. **Python re-exports** ✅ - committed as part of the same change (see 2026-03-22 section).
5. **Design docs** - `docs/architecture/multi_branch_tracking_implementation_plan.md`, `docs/architecture/phase_2.5.1_technical_design.md`.

Wrapper-side planning notes (in `/workspaces/axon-mcp/plans/`):

| File | Content |
| --- | --- |
| `multi_branch_brainstorm_baseline.md` | Approved data-model decisions for Phase 2.5 |
| `early-exit-safety-analysis.md` | Skipping `CallGraphStep` / `ImportResolutionStep` on unchanged reruns (~36s of ~38s) |
| `python-import-parsing-expansion-plan.md` | Python import parsing plan (implemented 2026-03-22) |

## Session 2026-10-14: Housekeeping ✅ COMPLETE

- Verified that no branch (including `origin/charlie`) has commits missing from `javampire`.
- Renumbered Phase 2.5 in `docs/architecture/multi_branch_tracking_implementation_plan.md` to match the code: **2.5.1 = commit/branch/tag/TREE_FILE schema**, **2.5.2 = user registry**. Added per-phase status markers.
- Added `jverein/` (local Java baseline clone) to the wrapper `.gitignore`.
- Refreshed this handover and `docs/axon-no-csharp-findings-and-plan.md`.

## Phase 2.5 Multi-Branch Tracking Status

`✅` done, `🚧` partial, `🧭` next/planned.

| Phase | Focus | Status |
| --- | --- | --- |
| 2.5.0 | Baseline test data | `✅` |
| 2.5.1 | Commit, branch, tag, TREE_FILE schema + backfill | `🚧` sync path does not write the new tables yet |
| 2.5.2 | User registry + Keycloak sync | `🧭` |
| 2.5.3 | FILE_INSTANCE migration onto TREE_FILE (drop legacy columns, query switch) | `🧭` |
| 2.5.4 | LOCAL_STAGE for local changes | `🧭` |
| 2.5.5 | Delta compression | `🧭` |
| 2.5.6 | Cross-version search API + MCP tools | `🧭` |

Known inconsistencies to resolve when work resumes:

- `src/database/models/git_tracking.py` comment says LOCAL_STAGE is "Phase 2.5.2"; the plan has it as 2.5.4.
- The design says COMMIT is repository-agnostic, but `git_commits.repository_id` exists (nullable) in the migration.

---

## Remaining Work

### Language Support (Paused)

1. **Java benchmark validation** - Confirm current Java breadth on shared repos
2. **Parser platform consolidation** - Capability matrix integration, strategy interfaces
3. **Corpus refresh** - Re-materialize chunks to pick up Python import/context improvements

### Active Work (Multi-Branch)

1. **Finish Phase 2.5.1** - Write commits/branches/tags/tree files from the repository sync path
2. **Phase 2.5.2** - User registry with Keycloak sync
3. **Phase 2.5.3** - Move FILE_INSTANCE reads onto TREE_FILE
4. **Optional perf item** - Early exit for unchanged reruns (`plans/early-exit-safety-analysis.md`)

---

## Recommended Next Session Plan

1. Read:
   - `/workspaces/axon-mcp/AGENTS.md`
   - `/workspaces/axon-mcp/docs/development-model.md`
   - `/workspaces/axon-mcp/docs/SESSION_HANDOVER.md`
   - `/workspaces/axon-mcp/plans/multi_branch_brainstorm_baseline.md`
   - `axon-src/docs/architecture/multi_branch_tracking_implementation_plan.md`
   - `axon-src/docs/architecture/phase_2.5.1_technical_design.md`

2. Stay on branch:
   - `javampire`

3. Before running DB-backed tests:
   ```bash
   cd /workspaces/axon-mcp/axon-src
   source /home/vscode/.venv-dev/bin/activate
   # DB env vars are already set by devcontainer
   alembic upgrade head
   pytest tests/ -v -rs
   ```

4. Decide the next increment: finish 2.5.1 sync wiring (dependency-first) or start 2.5.2 user registry.

## Useful References

- Branch: `javampire`
- HEAD: `6388af6`
- Multi-branch plan: `docs/architecture/multi_branch_tracking_implementation_plan.md`
- Phase 2.5.1 design: `docs/architecture/phase_2.5.1_technical_design.md`
- Baseline summary: `docs/validation/phase_2.5.0_completion_summary.md`
- File instance/content design: `docs/architecture/file_instance_content_dedup_proposal.md`
- Python plan: `docs/architecture/python_quick_win_and_semantic_search_plan.md`
- Alembic migrations: `alembic upgrade head` (production path)
- Manual DB reset: `scripts/reset_db.py` (dev/test environments only)
- Core model package: `src/database/models/` (`models_base.py`, `git_tracking.py`)

This handover is the canonical continuation point for the next session.
