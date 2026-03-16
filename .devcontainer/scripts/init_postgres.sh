#!/usr/bin/env bash
set -euo pipefail

SERVICES_DIR="/home/vscode/services"
PGDATA_DEFAULT="${SERVICES_DIR}/postgres/17/main"
PGDATA="${PGDATA:-$PGDATA_DEFAULT}"
PGSOCKET_DIR="${PGSOCKET_DIR:-/tmp/pgsocket}"

PROPS_FILE="${POSTGRES_PROPS_FILE:-}"
if [[ -z "${PROPS_FILE}" || ! -f "${PROPS_FILE}" ]]; then
  PROPS_FILE="/dev/null"
fi

get_prop() {
  local key="$1"
  local fallback="$2"
  local value
  value=$(grep -E "^\s*${key}=" "${PROPS_FILE}" | tail -n1 | cut -d= -f2- | tr -d '\r' || true)
  if [[ -z "${value}" ]]; then
    echo "${fallback}"
  else
    echo "${value}"
  fi
}

DB_PORT="${PGPORT:-$(get_prop 'domeus.dbport' '5432')}"
DB_NAME="${PGDATABASE:-$(get_prop 'domeus.database' 'postgres')}"
DB_USER="${PGUSER:-$(get_prop 'domeus.username' 'postgres')}"
DB_PASSWORD="${POSTGRES_DB_PASSWORD:-$(get_prop 'domeus.password' 'postgres')}"

init_needed=false
if [[ -s "${PGDATA}/PG_VERSION" ]]; then
  echo "PostgreSQL already initialized at ${PGDATA}"
else
  init_needed=true
fi

install -d -m 0755 "${PGSOCKET_DIR}"

if [[ "${init_needed}" == "true" ]]; then
  install -d -m 0700 "${PGDATA}"

  pwfile="$(mktemp)"
  trap 'rm -f "${pwfile}"' EXIT
  printf '%s\n' "${DB_PASSWORD}" > "${pwfile}"
  chmod 0600 "${pwfile}"

  /usr/lib/postgresql/17/bin/initdb \
    -D "${PGDATA}" \
    --username="${DB_USER}" \
    --pwfile="${pwfile}" \
    --auth-host=md5 \
    --auth-local=md5
fi

append_if_missing() {
  local line="$1"
  local file="$2"
  bash -c "grep -qxF \"${line}\" \"${file}\" || printf '%s\\n' \"${line}\" >> \"${file}\""
}

append_if_missing "listen_addresses='*'" "${PGDATA}/postgresql.conf"
append_if_missing "port=${DB_PORT}" "${PGDATA}/postgresql.conf"
append_if_missing "unix_socket_directories='${PGSOCKET_DIR}'" "${PGDATA}/postgresql.conf"
append_if_missing "host all all 0.0.0.0/0 md5" "${PGDATA}/pg_hba.conf"
append_if_missing "host all all ::/0 md5" "${PGDATA}/pg_hba.conf"

PGPASSFILE="/home/vscode/.pgpass"
if [[ ! -f "${PGPASSFILE}" ]]; then
  install -m 0600 /dev/null "${PGPASSFILE}"
fi
pgpass_line="${PGSOCKET_DIR}:${DB_PORT}:*:${DB_USER}:${DB_PASSWORD}"
grep -qxF "${pgpass_line}" "${PGPASSFILE}" || printf '%s\n' "${pgpass_line}" >> "${PGPASSFILE}"

started_by_script=false
if /usr/lib/postgresql/17/bin/pg_ctl -D "${PGDATA}" status >/dev/null 2>&1; then
  echo "PostgreSQL already running for ${PGDATA}"
else
  /usr/lib/postgresql/17/bin/pg_ctl -D "${PGDATA}" -o "-p ${DB_PORT} -k ${PGSOCKET_DIR}" -w start
  started_by_script=true
fi

PGPASSWORD="${DB_PASSWORD}" /usr/lib/postgresql/17/bin/psql -U "${DB_USER}" -p "${DB_PORT}" -h "${PGSOCKET_DIR}" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1 \
  || PGPASSWORD="${DB_PASSWORD}" /usr/lib/postgresql/17/bin/psql -U "${DB_USER}" -p "${DB_PORT}" -h "${PGSOCKET_DIR}" -d postgres -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"

if [[ "${started_by_script}" == "true" ]]; then
  /usr/lib/postgresql/17/bin/pg_ctl -D "${PGDATA}" -m fast -w stop
fi

echo "PostgreSQL initialized (db=${DB_NAME}, user=${DB_USER}, port=${DB_PORT})."

