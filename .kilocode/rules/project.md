# Axon MCP Project Rules

This workspace is a dev-container wrapper around a mounted source repository.
Work from the mounted paths below, not from generated cache folders.

## Workspace Layout

| Path | Purpose | Editable |
|------|---------|----------|
| `/workspaces/axon-mcp/axon-src` | Main source code | ✅ Yes |
| `/workspaces/axon-mcp/external-inspiration/kilocode` | Reference implementation | ❌ Read-only |
| `/workspaces/axon-mcp/docs` | Workspace documentation | ✅ Yes |

## Main Objective

This fork direction is:
- Prioritize Python + Java + documentation/config indexing
- Keep C# / Roslyn removed from runtime paths
- Improve Java semantic indexing quality using Axon + kilocode-inspired parser patterns

## Mandatory Reading Order at Session Start

1. `/workspaces/axon-mcp/docs/development-model.md`
2. `/workspaces/axon-mcp/docs/axon-no-csharp-findings-and-plan.md`
3. `/workspaces/axon-mcp/docs/workspace-notes.md`
4. `/workspaces/axon-mcp/axon-src/README.md`

## Quick-Links

### Workspace Docs
- Development model: [`development-model.md`](docs/development-model.md)
- Current status + plan: [`axon-no-csharp-findings-and-plan.md`](docs/axon-no-csharp-findings-and-plan.md)
- Workspace notes: [`workspace-notes.md`](docs/workspace-notes.md)

### Axon Source Docs
- Docs entry: [`axon-src/docs/index.md`](axon-src/docs/index.md)
- Analysis + roadmap: [`axon-src/docs/AXON_ANALYSIS_AND_ROADMAP.md`](axon-src/docs/AXON_ANALYSIS_AND_ROADMAP.md)
- Parser capability matrix: [`axon-src/docs/architecture/parser_capability_matrix.md`](axon-src/docs/architecture/parser_capability_matrix.md)

### Axon Source Hotspots
- Parser routing: [`axon-src/src/parsers/__init__.py`](axon-src/src/parsers/__init__.py)
- Language enum: [`axon-src/src/config/enums.py`](axon-src/src/config/enums.py)
- GitLab discovery: [`axon-src/src/gitlab/repository_manager.py`](axon-src/src/gitlab/repository_manager.py)
- Repository source abstraction: [`axon-src/src/repository_sources/__init__.py`](axon-src/src/repository_sources/__init__.py)
- File parse worker: [`axon-src/src/workers/file_worker.py`](axon-src/src/workers/file_worker.py)

### Inspiration Reference (Read-Only)
- Code index root: `external-inspiration/kilocode/src/services/code-index`
- Extension registry: `external-inspiration/kilocode/src/services/code-index/shared/supported-extensions.ts`
- Tree-sitter parser loader: `external-inspiration/kilocode/src/services/tree-sitter/languageParser.ts`

## Guardrails

- Treat `/external-inspiration/kilocode` as reference only; do not implement changes there.
- Keep wrapper/dev-container files in `/workspaces/axon-mcp`.
- Keep product code changes in `/workspaces/axon-mcp/axon-src`.
- For major reusable setup changes, update workspace docs in `/workspaces/axon-mcp/docs/` in the same task.
- For major product behavior changes, update `axon-src/docs/` in the same task.

## Development Philosophy

Use iterative, dependency-driven delivery with thin validated vertical slices:

1. Define scope at a high level first.
2. Implement the most foundational enabling piece first.
3. Validate in real runtime conditions (integration-first).
4. Capture lessons and adjust docs/architecture.
5. Repeat.

### Prioritization Rules

- Build enabling infrastructure before specialization.
- Prefer the smallest change that unlocks the next capability.
- Keep interfaces explicit where future language divergence is expected.

## Documentation-Driven Delivery

Documentation is part of implementation, not a follow-up task.

### Rules

1. Before non-trivial implementation, update the relevant plan/design doc section.
2. Keep high-level intent in high-level docs; place implementation detail in focused docs near the subsystem.
3. Every completed increment updates documentation in the same change stream.
4. If code and docs diverge, align docs immediately before considering the increment complete.
5. Avoid duplicate docs; link to canonical sources.

## Documentation Style Standard

Optimize for one-glance comprehension.

### Rules

1. Use compact comparison tables for options, tradeoffs, and capability status.
2. Use Mermaid diagrams for non-trivial flows (sequence/state/dependency/component views as needed).
3. Use explicit status markers consistently within a doc.
4. If symbolic tags are used in an artifact, include a short local legend in that section.
5. Keep tables/diagrams synchronized with shipped behavior.

### Recommended Status Markers

| Context | Markers |
|---------|---------|
| Capability matrices | `✅`, `🚧`, `🛑` |
| Execution plans | `✅`, `🧭`, `🔥` |

## Session Execution Contract

### At Start of Implementation Work

1. Read the mandatory docs in order.
2. Identify the target capability and map it to the roadmap/matrix.
3. Update plan docs for the exact increment when the change is non-trivial.
4. Then implement.

### At End of Implementation Work

1. Update affected docs to match final behavior.
2. Record verification outcomes (integration checks preferred).
3. Ensure next-step backlog reflects newly discovered constraints.

## Exploration Policy

This project allows exploration-first increments when uncertainty is high.

### Rules

1. Early exploratory increments do not require premature performance gatekeeping.
2. Capture findings, constraints, and follow-ups in docs as actionable next steps.
3. Convert exploratory conclusions into explicit implementation contracts once stable.

## Test Run Monitoring

- Do not actively monitor long-running test runs, benchmarks, or validation harnesses unless explicitly asked.
- When starting a long-running run, provide commands to monitor process liveness and output.
- Wait for user to report completion before inspecting results.
- It is fine to inspect logs and summarize outcomes after the user says the run is done.

## Python Environment

- Virtual environment: `/home/vscode/.venv-dev`
- Activation: `source /home/vscode/.venv-dev/bin/activate`

## Typical Commands

Run from `/workspaces/axon-mcp/axon-src`:

| Command | Purpose |
|---------|---------|
| `make dev-install` | Install development dependencies |
| `make test` | Run test suite |
| `make api-dev` | Start API development server |
| `make mcp-dev` | Start MCP development server |
| `cd ui && npm run dev` | Start UI development server |

## Test Execution Policy

- Do not run `pytest` or `make test` inside the default sandbox for this workspace.
- For agent-executed validation runs, request escalation and run tests outside sandbox.
- If escalation is not desired, present the command line to run the tests manually.
- Before running integration tests, always set DB env vars explicitly:
  - `export DATABASE_URL='postgresql+asyncpg://indexer:indexer@localhost:5432/indexer'`
  - `export TEST_DATABASE_URL='postgresql+asyncpg://indexer:indexer@localhost:5432/indexer'`

### Pre-flight Checklist for Agent Test Runs

1. Confirm command will run escalated (`sandbox_permissions=require_escalated`).
2. Include DB env exports in the same command for integration/DB tests.
3. Use `-rs` on pytest when checking targeted integration tests so skip reasons are visible.
