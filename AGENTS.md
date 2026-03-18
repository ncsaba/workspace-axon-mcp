# AGENTS.md - Axon MCP Workspace (Wrapper)

This workspace is a dev-container wrapper around a mounted source repository.
Work from the mounted paths below, not from generated cache folders.

## IMPORTANT: Current Session Handover (Read First)

- Canonical handover: `/workspaces/axon-mcp/docs/SESSION_HANDOVER.md`
- Before starting implementation, read this handover after the mandatory reading list.

## IMPORTANT: Test Run Monitoring

- Do not actively monitor long-running test runs, benchmarks, or validation harnesses unless the user explicitly asks for live monitoring.
- When starting a long-running run, provide the user with commands to monitor process liveness and output themselves, then wait for the user to report completion before inspecting results.
- It is fine to inspect logs and summarize outcomes after the user says the run is done.

## Workspace layout (inside dev-container)

- Main source (editable): `/workspaces/axon-mcp/axon-src`
- External inspiration only (read-only): `/workspaces/axon-mcp/external-inspiration/kilocode`

## Main objective

This fork direction is:
- prioritize Python + Java + documentation/config indexing
- keep C# / Roslyn removed from runtime paths
- improve Java semantic indexing quality using Axon + kilocode-inspired parser patterns

## Mandatory reading order at session start

1. `/workspaces/axon-mcp/docs/development-model.md`
2. `/workspaces/axon-mcp/docs/axon-no-csharp-findings-and-plan.md`
3. `/workspaces/axon-mcp/docs/workspace-notes.md`
4. `/workspaces/axon-mcp/axon-src/README.md`

## Quick-links

### Workspace docs
- Development model: `/workspaces/axon-mcp/docs/development-model.md`
- Current status + plan: `/workspaces/axon-mcp/docs/axon-no-csharp-findings-and-plan.md`
- Workspace notes: `/workspaces/axon-mcp/docs/workspace-notes.md`

Development model section map (quick onboarding):
- Core philosophy: `/workspaces/axon-mcp/docs/development-model.md#core-philosophy`
- Core loop: `/workspaces/axon-mcp/docs/development-model.md#core-loop`
- Documentation-driven execution: `/workspaces/axon-mcp/docs/development-model.md#documentation-driven-execution`
- Documentation style standard: `/workspaces/axon-mcp/docs/development-model.md#documentation-style-standard`
- Testing and validation policy: `/workspaces/axon-mcp/docs/development-model.md#testing-and-validation-policy`
- Session contract: `/workspaces/axon-mcp/docs/development-model.md#session-contract`

### Axon source docs
- Docs entry: `/workspaces/axon-mcp/axon-src/docs/index.md`
- Analysis + roadmap: `/workspaces/axon-mcp/axon-src/docs/AXON_ANALYSIS_AND_ROADMAP.md`
- Parser capability matrix: `/workspaces/axon-mcp/axon-src/docs/architecture/parser_capability_matrix.md`
- Latest session handover: `/workspaces/axon-mcp/docs/SESSION_HANDOVER.md`

### Axon source hotspots
- Parser routing: `/workspaces/axon-mcp/axon-src/src/parsers/__init__.py`
- Language enum: `/workspaces/axon-mcp/axon-src/src/config/enums.py`
- GitLab discovery: `/workspaces/axon-mcp/axon-src/src/gitlab/repository_manager.py`
- Repository source abstraction: `/workspaces/axon-mcp/axon-src/src/repository_sources/__init__.py`
- File parse worker: `/workspaces/axon-mcp/axon-src/src/workers/file_worker.py`

### Inspiration reference (read-only)
- Code index root: `/workspaces/axon-mcp/external-inspiration/kilocode/src/services/code-index`
- Extension registry: `/workspaces/axon-mcp/external-inspiration/kilocode/src/services/code-index/shared/supported-extensions.ts`
- Tree-sitter parser loader: `/workspaces/axon-mcp/external-inspiration/kilocode/src/services/tree-sitter/languageParser.ts`

## Guardrails

- Treat `/external-inspiration/kilocode` as reference only; do not implement changes there.
- Keep wrapper/dev-container files in `/workspaces/axon-mcp`.
- Keep product code changes in `/workspaces/axon-mcp/axon-src`.
- For major reusable setup changes, update workspace docs in `/workspaces/axon-mcp/docs/` in the same task.
- For major product behavior changes, update `axon-src/docs/` in the same task.

## Development Philosophy (Required)

Use iterative, dependency-driven delivery with thin validated vertical slices:

1. Define scope at a high level first.
2. Implement the most foundational enabling piece first.
3. Validate in real runtime conditions (integration-first).
4. Capture lessons and adjust docs/architecture.
5. Repeat.

Prioritization rules:
- Build enabling infrastructure before specialization.
- Prefer the smallest change that unlocks the next capability.
- Keep interfaces explicit where future language divergence is expected.

## Documentation-Driven Delivery (Required)

Documentation is part of implementation, not a follow-up task.

Rules:
1. Before non-trivial implementation, update the relevant plan/design doc section (usually roadmap + target architecture doc).
2. Keep high-level intent in high-level docs; place implementation detail in focused docs near the subsystem.
3. Every completed increment updates documentation in the same change stream.
4. If code and docs diverge, align docs immediately before considering the increment complete.
5. Avoid duplicate docs; link to canonical sources.

## Documentation Style Standard (Required)

Optimize for one-glance comprehension.

Rules:
1. Use compact comparison tables for options, tradeoffs, and capability status.
2. Use Mermaid diagrams for non-trivial flows (sequence/state/dependency/component views as needed).
3. Use explicit status markers consistently within a doc.
4. If symbolic tags are used in an artifact, include a short local legend in that section.
5. Keep tables/diagrams synchronized with shipped behavior.

Recommended status markers:
- `✅`, `🚧`, `🛑` for capability matrices
- `✅`, `🧭`, `🔥` for execution plans

## Session Execution Contract

At start of implementation work:
1. Read the mandatory docs in order.
2. Identify the target capability and map it to the roadmap/matrix.
3. Update plan docs for the exact increment when the change is non-trivial.
4. Then implement.

At end of implementation work:
1. Update affected docs to match final behavior.
2. Record verification outcomes (integration checks preferred).
3. Ensure next-step backlog reflects newly discovered constraints.

## Exploration Policy

This project allows exploration-first increments when uncertainty is high.

Rules:
1. Early exploratory increments do not require premature performance gatekeeping.
2. Capture findings, constraints, and follow-ups in docs as actionable next steps.
3. Convert exploratory conclusions into explicit implementation contracts once stable.

## Python environment

- Use virtual environment: `/home/vscode/.venv-dev`
- Example activation: `source /home/vscode/.venv-dev/bin/activate`

## Typical local commands

Run from `/workspaces/axon-mcp/axon-src`:

- `make dev-install`
- `make test`
- `make api-dev`
- `make mcp-dev`
- `cd ui && npm run dev`

## Test Execution Policy

- Do not run `pytest` or `make test` inside the default sandbox for this workspace.
- For agent-executed validation runs, request escalation and run tests outside sandbox.
- If escalation is not desired, present the user the command line to run the tests manually and share the results.
- Before running integration tests, always set DB env vars explicitly:
  - `export DATABASE_URL='postgresql+asyncpg://indexer:indexer@localhost:5432/indexer'`
  - `export TEST_DATABASE_URL='postgresql+asyncpg://indexer:indexer@localhost:5432/indexer'`
- Mandatory pre-flight for any agent test run:
  1. Confirm command will run escalated (`sandbox_permissions=require_escalated`).
  2. Include DB env exports in the same command for integration/DB tests.
  3. Use `-rs` on pytest when checking targeted integration tests so skip reasons are visible.
