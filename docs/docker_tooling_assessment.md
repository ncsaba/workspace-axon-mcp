# Docker Tooling Assessment

**Date**: 2026-03-22  
**Purpose**: Compare dev-container setup vs axon-src Docker tooling and define alignment plan

---

## Executive Summary

The project has two Docker/deployment setups that need alignment:

| Setup | Purpose | Priority |
|-------|---------|----------|
| **Dev-container** (`.devcontainer/`) | VS Code local development | Primary |
| **axon-src Docker** (`axon-src/docker/`) | Non-VS-Code development & production | Secondary |

**Goal**: Align axon-src Docker tooling to support:
1. Non-VS-Code development environments (may differ slightly from dev-container)
2. Single-container deployment (all tools baked in)
3. Multi-container deployment (production-style separation)

---

## Current State Analysis

### Deployment Model Gap Analysis

| Deployment Model | Current Support | Gap |
|------------------|-----------------|-----|
| Dev-container (VS Code) | ✅ Complete | None |
| Multi-container (prod) | ⚠️ Partial | Missing `inventory` queue, health checks |
| Single-container (all-in-one) | ❌ Missing | No Dockerfile variant exists |

**Key Finding**: The current Dockerfile variants are all **application-only** images. They do not bundle PostgreSQL, Redis, or other infrastructure services. There is no single-container option.

### Dockerfile Variants Analysis

The `axon-src/docker/` directory contains 4 Dockerfile variants:

| Dockerfile | Purpose | Build Time | Image Size | Contains |
|------------|---------|------------|------------|----------|
| `Dockerfile` | Standard multi-stage build | ~5min | ~800MB | App only |
| `Dockerfile.base` | Pre-built dependencies | ~8min | ~2GB | App deps only |
| `Dockerfile.fast` | Uses pre-built base | ~30s | ~800MB | App only |
| `Dockerfile.optimized` | Layer-optimized | ~5min | ~800MB | App only |

**All variants are application-only** - none include:
- PostgreSQL / pgvector
- Redis
- Ollama
- Prometheus/Grafana

#### Dockerfile (Standard)

```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder
# Installs: build-essential, git, curl, libcurl4, ca-certificates
# Creates: /opt/venv with all dependencies

FROM python:3.11-slim
# Runtime only: git, curl, libcurl4, ca-certificates
# Copies: /opt/venv from builder
# Creates: axon user (uid 1000)
# Exposes: 8001, 8080
```

**Characteristics**:
- Full dependency build every time
- Good for CI/CD where cache isn't available
- Includes NTLM support via libcurl4-gnutls-dev
- Tree-sitter grammars compile during pip install ✅

#### Dockerfile.base (Base Image)

```dockerfile
FROM python:3.11-slim
# Installs: build-essential, git, curl, wget, libcurl4, ca-certificates
# Creates: /opt/venv with all dependencies
# Includes: pip cache mount for faster rebuilds
```

**Characteristics**:
- Must be built first: `docker build -f docker/Dockerfile.base -t axon-base:latest .`
- Rebuild when `requirements.txt` changes
- Tag and push to registry for team use
- Includes wget (not in other variants)

#### Dockerfile.fast (Development)

```dockerfile
FROM axon-base:latest as builder
FROM python:3.11-slim
# Copies: /opt/venv from axon-base
# Skips: dependency installation entirely
```

**Characteristics**:
- Requires `axon-base:latest` to exist
- Fastest iteration for code-only changes
- Used by `docker-compose.yml` by default
- Will fail if base image doesn't exist

#### Dockerfile.optimized (Production)

```dockerfile
# Same structure as Dockerfile but with:
# - Explicit layer ordering comment
# - Cache directory created BEFORE code copy
# - Better layer caching for code changes
```

**Characteristics**:
- Same build time as standard
- Better cache utilization
- Code changes only rebuild final layer
- Recommended for production builds

---

## Architecture Comparison

### Base Images

| Aspect | Dev-container | axon-src Docker |
|--------|---------------|-----------------|
| Base image | `mcr.microsoft.com/devcontainers/python:3.11-trixie` | `python:3.11-slim` |
| Python version | 3.11 | 3.11 ✅ |
| Debian version | Trixie (testing) | Bookworm (stable) |
| Image size | ~2GB (dev tools included) | ~400MB base |
| User | `vscode` | `axon` (uid 1000) |

### Service Model

| Service | Dev-container | axon-src Docker (multi-container) |
|---------|---------------|-----------------------------------|
| **PostgreSQL** | Native process via `pg_ctl` | Container `pgvector/pgvector:pg17` |
| **Redis** | Native process | Container `redis:7-alpine` |
| **Prometheus** | Native process | Container `prom/prometheus:latest` |
| **Grafana** | Not included | Container `grafana/grafana:latest` |
| **API** | Manual start (`make api-dev`) | Container (uvicorn) |
| **MCP Server** | Manual start (`make mcp-dev`) | Container |
| **Celery Workers** | Manual start | Containers (2 worker types) |
| **UI** | Manual start (`npm run dev`) | Container (nginx) |

### Network Configuration

| Aspect | Dev-container | axon-src Docker |
|--------|---------------|-----------------|
| Network mode | Host (localhost) | Bridge network `axon-network` |
| PostgreSQL | Unix socket `/tmp/pgsocket` | TCP port 5432 |
| Service discovery | localhost | Container names |
| DATABASE_URL | `localhost:5432` | `postgres:5432` |

---

## Detailed Differences

### 1. Celery Queue Configuration

**Dev-container** (manual start):
```bash
celery -A src.workers.celery_app worker \
    --loglevel=info \
    -Q repository_sync,file_parsing,embeddings,inventory,ai_enrichment,repository_aggregation \
    --concurrency=2
```

**axon-src Docker** (`docker-compose.yml`):
```yaml
# worker service (line 124)
--queues=repository_sync,file_parsing,embeddings,default

# enrichment-worker service (line 155)
--queues=ai_enrichment,repository_aggregation
```

**Gap**: The `worker` service is missing `inventory` queue.

### 2. Environment Variables

| Variable | Dev-container | axon-src Docker |
|----------|---------------|-----------------|
| `DATABASE_URL` | Set in `devcontainer.json` | From `.env` file |
| `REDIS_URL` | `redis://localhost:6379/0` | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Same as REDIS_URL | From `.env` file |
| `PGHOST` | `/tmp/pgsocket` | N/A (container) |
| `PROMETHEUS_MULTIPROC_DIR` | `/home/vscode/services/prometheus/multiproc` | N/A |

### 3. Health Checks

| Service | Dev-container | axon-src Docker |
|---------|---------------|-----------------|
| PostgreSQL | `pg_isready` | `pg_isready` ✅ |
| Redis | `redis-cli ping` | `redis-cli ping` ✅ |
| API | None (manual) | `curl /api/v1/health` ✅ |
| MCP Server | None (manual) | `curl /api/v1/health` ⚠️ (wrong endpoint) |
| Workers | None (manual) | None ❌ |

### 4. Volume Mounts

| Path | Dev-container | axon-src Docker |
|------|---------------|-----------------|
| Source code | Bind mount (host) | Bind mount (dev) / Copy (prod) |
| Python venv | Named volume `axon-mcp-venv` | In-image `/opt/venv` |
| Cache | Named volume `axon-mcp-cache` | Bind mount `./cache` |
| PostgreSQL data | Host directory | Named volume `postgres_data` |
| Redis data | Host directory | Named volume `redis_data` |

### 5. Missing Components in axon-src Docker

| Component | Status | Impact |
|-----------|--------|--------|
| Ollama container | ❌ Missing | LLM features require external Ollama |
| Test database | ❌ Not configured | No `TEST_DATABASE_URL` equivalent |
| UI build arg | ⚠️ Hardcoded IP | `VITE_API_BASE_URL=http://10.30.81.101/` |
| Inventory queue | ❌ Missing from worker | Repository sync incomplete |
| Single-container image | ❌ Missing | No all-in-one deployment option |

---

## Alignment Plan

### Target Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT OPTIONS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Dev-container (VS Code)                                     │
│     └── .devcontainer/ → Current setup (unchanged)             │
│                                                                 │
│  2. Multi-container (Production)                                │
│     └── docker-compose.yml → Separate service containers       │
│         ├── api (port 8080)                                    │
│         ├── mcp-server (port 8001)                             │
│         ├── worker (Celery)                                    │
│         ├── enrichment-worker (Celery)                         │
│         ├── beat (Celery scheduler)                            │
│         ├── postgres (pgvector)                                │
│         ├── redis                                              │
│         ├── prometheus (optional)                              │
│         ├── grafana (optional)                                 │
│         └── ui (nginx)                                         │
│                                                                 │
│  3. Single-container (All-in-one)                               │
│     └── Dockerfile.standalone → Everything in one image        │
│         ├── PostgreSQL (internal)                              │
│         ├── Redis (internal)                                   │
│         ├── API (port 8080)                                    │
│         ├── MCP Server (port 8001)                             │
│         ├── Celery workers (internal)                          │
│         └── Process supervisor (s6-overlay)                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### New Dockerfile Variant: `Dockerfile.standalone`

Create a new all-in-one image for single-container deployment:

```dockerfile
# Dockerfile.standalone - All-in-one image
FROM python:3.11-slim

# Install all runtime dependencies including PostgreSQL and Redis
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    wget \
    libcurl4 \
    libcurl4-gnutls-dev \
    ca-certificates \
    postgresql-17 \
    postgresql-17-pgvector \
    redis-server \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install Python deps
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /tmp/
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# Copy application
WORKDIR /app
COPY . /app/

# Copy supervisor config for process management
COPY docker/supervisord.conf /etc/supervisor/conf.d/axon.conf

# Create non-root user
RUN useradd -m -u 1000 axon && \
    chown -R axon:axon /app

# Expose ports
EXPOSE 8001 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# Start supervisor (manages all processes)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/axon.conf"]
```

### Supervisor Configuration

```ini
; docker/supervisord.conf
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:postgresql]
command=/usr/lib/postgresql/17/bin/postgres -D /var/lib/postgresql/17/main
user=postgres
autostart=true
autorestart=true
stdout_logfile=/var/log/postgresql.log
stderr_logfile=/var/log/postgresql.err

[program:redis]
command=/usr/bin/redis-server
autostart=true
autorestart=true
stdout_logfile=/var/log/redis.log
stderr_logfile=/var/log/redis.err

[program:api]
command=/opt/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8080
directory=/app
user=axon
autostart=true
autorestart=true
stdout_logfile=/var/log/api.log
stderr_logfile=/var/log/api.err

[program:mcp-server]
command=/opt/venv/bin/python -m src.mcp_server.main
directory=/app
user=axon
autostart=true
autorestart=true
stdout_logfile=/var/log/mcp.log
stderr_logfile=/var/log/mcp.err

[program:worker]
command=/opt/venv/bin/celery -A src.workers.celery_app:celery_app worker --loglevel=info --concurrency=2 --queues=repository_sync,file_parsing,embeddings,inventory,default
directory=/app
user=axon
autostart=true
autorestart=true
stdout_logfile=/var/log/worker.log
stderr_logfile=/var/log/worker.err

[program:enrichment-worker]
command=/opt/venv/bin/celery -A src.workers.celery_app:celery_app worker --loglevel=info --concurrency=4 --queues=ai_enrichment,repository_aggregation
directory=/app
user=axon
autostart=true
autorestart=true
stdout_logfile=/var/log/enrichment.log
stderr_logfile=/var/log/enrichment.err

[program:beat]
command=/opt/venv/bin/celery -A src.workers.celery_app:celery_app beat --loglevel=info
directory=/app
user=axon
autostart=true
autorestart=true
stdout_logfile=/var/log/beat.log
stderr_logfile=/var/log/beat.err
```

---

## Dockerfile Selection Guide

| Scenario | Recommended Dockerfile | Command |
|----------|----------------------|---------|
| VS Code development | N/A (use dev-container) | - |
| Non-VS-Code development | `Dockerfile.fast` | `docker compose up` |
| CI/CD pipeline | `Dockerfile.optimized` | Set in compose |
| Production multi-container | `Dockerfile.optimized` | `docker compose -f docker-compose.yml up` |
| Production single-container | `Dockerfile.standalone` | `docker run axon-standalone` |
| Demo / Quick start | `Dockerfile.standalone` | Single `docker run` |
| Requirements changed | Rebuild base first | `./rebuild-base.sh` |

### Build Workflow

```bash
# Multi-container development
./rebuild-base.sh  # First time or after requirements.txt change
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d

# Single-container deployment
docker build -f docker/Dockerfile.standalone -t axon-standalone:latest .
docker run -d -p 8080:8080 -p 8001:8001 axon-standalone:latest
```

---

## Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `axon-src/docker/Dockerfile.standalone` | All-in-one image with PostgreSQL, Redis, workers |
| `axon-src/docker/supervisord.conf` | Process supervisor configuration |
| `axon-src/docker/docker-compose.standalone.yml` | Optional: compose wrapper for standalone |

### Modified Files

| File | Change |
|------|--------|
| `axon-src/docker/docker-compose.yml` | Add `inventory` queue, fix health check, make UI URL configurable |
| `axon-src/docker/init-db.sql` | Add test database creation |
| `axon-src/.env.example` | Add Docker-specific comments, document both modes |
| `axon-src/DEPLOY-README.md` | Document deployment options |
| `axon-src/Makefile` | Add Docker targets for both modes |

---

## Environment Variable Mapping

### Multi-container Deployment

```bash
# Database - use container service name
DATABASE_URL=postgresql+asyncpg://indexer:indexer@postgres:5432/indexer
TEST_DATABASE_URL=postgresql+asyncpg://indexer:indexer@postgres:5432/indexer_test

# Redis - use container service name
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Ollama - use container service name (if using Ollama container)
OLLAMA_BASE_URL=http://ollama:11434/v1

# API - for inter-container communication
API_BASE_URL=http://api:8080
```

### Single-container Deployment

```bash
# Database - localhost (internal to container)
DATABASE_URL=postgresql+asyncpg://indexer:indexer@localhost:5432/indexer
TEST_DATABASE_URL=postgresql+asyncpg://indexer:indexer@localhost:5432/indexer_test

# Redis - localhost (internal to container)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Ollama - external (not included in standalone)
OLLAMA_BASE_URL=http://host.docker.internal:11434/v1

# API - localhost
API_BASE_URL=http://localhost:8080
```

### Dev-container (Reference)

```bash
# Database - use localhost with Unix socket
DATABASE_URL=postgresql+asyncpg://indexer:indexer@localhost:5432/indexer
TEST_DATABASE_URL=postgresql+asyncpg://indexer:indexer@localhost:5432/indexer_test
PGHOST=/tmp/pgsocket

# Redis - use localhost
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# Ollama - use localhost (external service)
OLLAMA_BASE_URL=http://localhost:11434/v1
```

---

## Implementation Checklist

### Multi-container Fixes

- [ ] Add `inventory` queue to worker service in `docker-compose.yml`
- [ ] Fix MCP server health check endpoint
- [ ] Make `VITE_API_BASE_URL` configurable via `.env`
- [ ] Add test database to `init-db.sql`
- [ ] Add optional Ollama service with profile
- [ ] Add worker health checks

### Single-container Implementation

- [ ] Create `Dockerfile.standalone`
- [ ] Create `supervisord.conf`
- [ ] Create initialization script for PostgreSQL (create DB, run migrations)
- [ ] Test single-container startup
- [ ] Document single-container deployment

### Documentation

- [ ] Update `DEPLOY-README.md` with deployment options
- [ ] Add Makefile targets for both deployment modes
- [ ] Create environment variable quick reference

---

## Summary

| Deployment Mode | Dockerfile | Use Case | Status |
|-----------------|------------|----------|--------|
| Dev-container | N/A | VS Code development | ✅ Complete |
| Multi-container | `Dockerfile.optimized` | Production | ⚠️ Needs fixes |
| Single-container | `Dockerfile.standalone` | Demo, simple deploy | ❌ To create |

The current Dockerfile variants (`Dockerfile`, `Dockerfile.base`, `Dockerfile.fast`, `Dockerfile.optimized`) are all **application-only** images. A new `Dockerfile.standalone` is needed for single-container deployment with all services bundled.
