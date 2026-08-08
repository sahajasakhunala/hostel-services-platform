#!/usr/bin/env bash
# ==============================================================================
# HostelFlow Automated Logical Database Backup Script (Phase 7.5)
# ==============================================================================
set -euo pipefail

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_NAME="${DB_NAME:-hostelflow_db}"
OUTPUT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/dumps"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

SQL_FILE="${OUTPUT_DIR}/${DB_NAME}_${TIMESTAMP}.sql"
GZ_FILE="${SQL_FILE}.gz"
CHECKSUM_FILE="${GZ_FILE}.sha256"

mkdir -p "${OUTPUT_DIR}"

echo "Starting logical database backup for ${DB_NAME} at $(date)..."
START_TIME=$(date +%s)

mysqldump \
  --host="${DB_HOST}" \
  --port="${DB_PORT}" \
  --user="${DB_USER}" \
  --routines \
  --triggers \
  --events \
  --single-transaction \
  --quick \
  "${DB_NAME}" > "${SQL_FILE}"

gzip -f "${SQL_FILE}"
sha256sum "${GZ_FILE}" > "${CHECKSUM_FILE}"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
SIZE_BYTES=$(wc -c < "${GZ_FILE}")

echo "[BACKUP SUCCESS] Compressed Dump: ${GZ_FILE}"
echo "  Size: ${SIZE_BYTES} bytes"
echo "  Duration: ${DURATION}s"
echo "  SHA-256 Checksum: $(cat "${CHECKSUM_FILE}")"
