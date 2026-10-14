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

## Git Remotes (`axon-src`)

| Remote | URL | Role | Fetch from dev-container |
| --- | --- | --- | --- |
| `origin` | `git@github.com:ncsaba/Axon.MCP.Server.git` | Our fork (`javampire`, `charlie`, `public-release`) | No (SSH), fetch from host |
| `mapp` | `git@github.com:Mapp-Labs/mapp-axon-mcp.git` | Mapp-Labs mirror (`master`, `javampire`) | No (SSH), fetch from host |
| `upstream` | `https://github.com/ali-kamali/Axon.MCP.Server.git` | Original project, read-only (default branch `public-release`) | Yes (HTTPS) |

- Fork point from `upstream/public-release`: `523db87` (2026-03-05).
- As of 2026-10-14, upstream has only Dependabot version bumps since the fork (`black`, `pyjwt`, `flatted`, `axios` merged; 14 Dependabot branches open). No feature work to absorb.
- Re-add on a fresh clone: `git remote add upstream https://github.com/ali-kamali/Axon.MCP.Server.git`
- Check upstream drift: `git fetch upstream && git log --oneline $(git merge-base javampire upstream/public-release)..upstream/public-release`

## Current Fork Status (2026-03-20)

`✅` active/ready, `🚧` incomplete/partial.

| Area | Status | Notes |
| --- | --- | --- |
| C# / Roslyn runtime removal | `✅` | Removed from current runtime path. |
| Language focus alignment | `✅` | Python, Java, JS/TS/Vue, docs/config. |
| File instance/content separation | `✅` | Merged into master. All Phase 1 work complete. |
| Python semantic depth | `🚧` | Import/call/endpoint extraction landed; retrieval quality ongoing. |
| Java semantic depth | `🚧` | Baseline parsing works; semantic edges need benchmark validation. |

## Dev Environment Baseline

`✅` available/running, `🧭` manual action required.

| Component | Status | Details |
| --- | --- | --- |
| Python venv | `✅` | `/home/vscode/.venv-dev` |
| PostgreSQL 17 + pgvector | `✅` | DB/user/password `indexer`, port `5432`, databases `indexer` and `indexer_test` are initialized by the devcontainer bootstrap |
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
- `TEST_PGDATABASE=indexer_test`
- `PGPORT=5432`
- `PGHOST=/tmp/pgsocket`
- `DATABASE_URL=postgresql+asyncpg://indexer:indexer@localhost:5432/indexer`
- `TEST_DATABASE_URL=postgresql+asyncpg://indexer:indexer@localhost:5432/indexer_test`

After a devcontainer rebuild/reopen, those env vars are already present in normal shells and tool runs.

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

Session handover:

- `/workspaces/axon-mcp/docs/SESSION_HANDOVER.md`

If there is any mismatch between docs, treat the wrapper doc above as the operational baseline for this workspace.

## Session Handoff (2026-03-20)

`✅` done, `🧭` next action, `🔥` risk.

| Topic | Status | Details |
| --- | --- | --- |
| File instance/content separation | `✅` | Merged into master. All Phase 1 work complete. |
| Python import/call/endpoint extraction | `✅` | Quick wins landed in `179f312`. |
| Python retrieval quality | `🧭` | Chunk coherence and benchmark validation. |
| Java benchmark validation | `🧭` | Confirm breadth on shared repos. |
| Parser platform consolidation | `🧭` | Capability matrix integration, strategy interfaces. |
| Main delivery risk | `🔥` | Java semantic precision may require parser metadata expansion. |

Next session startup order:
1. Read `/workspaces/axon-mcp/AGENTS.md`.
2. Read `/workspaces/axon-mcp/docs/SESSION_HANDOVER.md`.
3. Read `/workspaces/axon-mcp/docs/axon-no-csharp-findings-and-plan.md`.
4. Read `/workspaces/axon-mcp/axon-src/docs/AXON_ANALYSIS_AND_ROADMAP.md`.
5. Read `/workspaces/axon-mcp/axon-src/docs/architecture/parser_capability_matrix.md`.

## Common Commands

Run from `axon-src`:

- `make dev-install`
- `make test`
- `make api-dev`
- `make mcp-dev`
- `cd ui && npm run dev`

## Test Run Pre-Flight

The devcontainer now exports these by default for integration/DB-backed tests:

```bash
export DATABASE_URL='postgresql+asyncpg://indexer:indexer@localhost:5432/indexer'
export TEST_DATABASE_URL='postgresql+asyncpg://indexer:indexer@localhost:5432/indexer_test'
```

In a normal devcontainer shell you usually only need:

```bash
source /home/vscode/.venv-dev/bin/activate
```

Schema management:

```bash
cd /workspaces/axon-mcp/axon-src
source /home/vscode/.venv-dev/bin/activate

# Production path (backwards-compatible migrations):
alembic upgrade head

# Dev/test environments only (fresh schema reset):
python scripts/reset_db.py --yes --use-test-db
```

**Production deployments must use Alembic migrations.** The reset script is for dev/test environments only. The test harness creates and drops schema in `TEST_DATABASE_URL`, so it must remain separate from `DATABASE_URL`.

Agent policy reminder:
- Run tests only outside the default sandbox (escalated mode).

## Local Database DSN

- `postgresql+asyncpg://indexer:indexer@localhost:5432/indexer`
- `postgresql+asyncpg://indexer:indexer@localhost:5432/indexer_test`
