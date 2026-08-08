#!/usr/bin/env bash
# ==============================================================================
# HostelFlow Isolated Database Restore Script (Phase 7.5)
# ==============================================================================
set -euo pipefail

DUMP_GZ="${1:-}"
TARGET_DB="${2:-hostelflow_restore_test}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"

if [ -z "${DUMP_GZ}" ]; then
  echo "Error: Path to .sql.gz dump file required."
  echo "Usage: ./restore_database.sh <path_to_dump.sql.gz> [target_db_name]"
  exit 1
fi

if [ "${TARGET_DB}" == "hostelflow_db" ]; then
  echo "CRITICAL SAFETY ERROR: Cannot restore directly over active production database 'hostelflow_db'."
  exit 1
fi

echo "Starting isolated database restore into '${TARGET_DB}'..."
START_TIME=$(date +%s)

mysql --host="${DB_HOST}" --port="${DB_PORT}" --user="${DB_USER}" -e "DROP DATABASE IF EXISTS \`${TARGET_DB}\`; CREATE DATABASE \`${TARGET_DB}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

zcat "${DUMP_GZ}" | mysql --host="${DB_HOST}" --port="${DB_PORT}" --user="${DB_USER}" "${TARGET_DB}"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "[RESTORE SUCCESS] Target Database '${TARGET_DB}' successfully restored."
echo "  Duration: ${DURATION}s"
