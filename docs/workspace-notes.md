# Workspace Notes

## Rationale

- Keep devcontainer and editor setup outside the source repository.
- Mount source as `axon-src` so project files remain clean.
- Persist dev tooling state across rebuilds via named volumes and bind mounts.
- Follow the iterative delivery model documented in `docs/development-model.md`.

## Important Paths

- Wrapper root: `/workspaces/axon-mcp`
- Project source: `/workspaces/axon-mcp/axon-src`
- External inspiration only (read-only): `/workspaces/axon-mcp/external-inspiration/kilocode`

## Current Fork Status (2026-03-11)

`✅` active/ready, `🚧` incomplete/partial.

| Area | Status | Notes |
| --- | --- | --- |
| C# / Roslyn runtime removal | `✅` | Removed from current runtime path. |
| Language focus alignment | `✅` | Python, Java, JS/TS/Vue, docs/config. |
| Java semantic depth | `🚧` | Baseline parsing works; semantic edges are ongoing work. |

## Dev Environment Baseline

`✅` available/running, `🧭` manual action required.

| Component | Status | Details |
| --- | --- | --- |
| Python venv | `✅` | `/home/vscode/.venv-dev` |
| PostgreSQL 17 + pgvector | `✅` | DB/user/password `indexer`, port `5432` |
| Redis | `✅` | Auto-start with dev-container |
| Celery worker | `🧭` | Installed; start manually when needed |

## PostgreSQL Readiness

Workspace scripts under `.devcontainer/scripts/`:

- `init_postgres.sh`
- `start_postgres.sh`

Configured defaults (via `.devcontainer/devcontainer.json` `remoteEnv`):

- `PGUSER=indexer`
- `POSTGRES_DB_PASSWORD=indexer`
- `PGDATABASE=indexer`
- `PGPORT=5432`
- `PGHOST=/tmp/pgsocket`

Data/log persistence:

- `.devcontainer/services` -> `/home/vscode/services`

## Redis Readiness

Workspace scripts under `.devcontainer/scripts/`:

- `init_redis.sh`
- `start_redis.sh`

Configured defaults:

- `REDIS_PORT=6379`
- `REDIS_BIND_ADDRESS=0.0.0.0`

Data/log persistence:

- `.devcontainer/services` -> `/home/vscode/services`

## Documentation Status

Primary current-state + plan doc:

- `/workspaces/axon-mcp/docs/axon-no-csharp-findings-and-plan.md`

Axon product roadmap view:

- `/workspaces/axon-mcp/axon-src/docs/AXON_ANALYSIS_AND_ROADMAP.md`

If there is any mismatch between docs, treat the wrapper doc above as the operational baseline for this workspace.

## Session Handoff (2026-03-11)

`✅` done, `🧭` next action, `🔥` risk.

| Topic | Status | Details |
| --- | --- | --- |
| Documentation style convergence | `✅` | Wrapper + Axon docs now use icon-key style with meaningful icons and no legend labels. |
| Axon docs commit | `✅` | `axon-src` commit: `959e95a` (`docs: add parser capability matrix and align roadmap/docs style`). |
| Parser capability matrix | `✅` | Added at `/workspaces/axon-mcp/axon-src/docs/architecture/parser_capability_matrix.md`. |
| Next implementation step | `🧭` | Start code work on language strategy interfaces (import/call/dependency extraction). |
| Main delivery risk | `🔥` | Java semantic precision may require parser metadata expansion before high-confidence relation extraction. |

Next session startup order:
1. Read `/workspaces/axon-mcp/AGENTS.md`.
2. Read `/workspaces/axon-mcp/docs/axon-no-csharp-findings-and-plan.md`.
3. Read `/workspaces/axon-mcp/axon-src/docs/AXON_ANALYSIS_AND_ROADMAP.md`.
4. Read `/workspaces/axon-mcp/axon-src/docs/architecture/parser_capability_matrix.md`.

## Common Commands

Run from `axon-src`:

- `make dev-install`
- `make test`
- `make api-dev`
- `make mcp-dev`
- `cd ui && npm run dev`

## Test Run Pre-Flight

Use this for integration/DB-backed tests:

```bash
source /home/vscode/.venv-dev/bin/activate
export DATABASE_URL='postgresql+asyncpg://indexer:indexer@localhost:5432/indexer'
export TEST_DATABASE_URL='postgresql+asyncpg://indexer:indexer@localhost:5432/indexer'
```

Agent policy reminder:
- Run tests only outside the default sandbox (escalated mode).

## Local Database DSN

- `postgresql+asyncpg://indexer:indexer@localhost:5432/indexer`
