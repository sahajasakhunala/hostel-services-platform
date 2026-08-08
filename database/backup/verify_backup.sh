#!/usr/bin/env bash
# ==============================================================================
# HostelFlow Backup Integrity & Content Inspection Script (Phase 7.5)
# ==============================================================================
set -euo pipefail

DUMP_GZ="${1:-}"

if [ -z "${DUMP_GZ}" ]; then
  echo "Error: Path to .sql.gz dump file required."
  exit 1
fi

if [ ! -f "${DUMP_GZ}" ]; then
  echo "Error: Dump file '${DUMP_GZ}' does not exist."
  exit 1
fi

CHECKSUM_FILE="${DUMP_GZ}.sha256"
if [ -f "${CHECKSUM_FILE}" ]; then
  echo "Verifying SHA-256 Checksum..."
  sha256sum -c "${CHECKSUM_FILE}"
fi

echo "Inspecting dump contents for mandatory database objects..."
CONTENT=$(zcat "${DUMP_GZ}")

check_object() {
  local pattern="$1"
  local name="$2"
  if echo "${CONTENT}" | grep -iq "${pattern}"; then
    echo "  [FOUND] ${name}"
  else
    echo "  [MISSING] ${name}"
  fi
}

echo "--- Table Verification ---"
check_object "CREATE TABLE.*students" "students table"
check_object "CREATE TABLE.*beds" "beds table"
check_object "CREATE TABLE.*bed_allocations" "bed_allocations table"
check_object "CREATE TABLE.*invoices" "invoices table"

echo "--- Stored Procedure Verification ---"
check_object "PROCEDURE.*sp_allocate_bed" "sp_allocate_bed procedure"
check_object "PROCEDURE.*sp_process_payment" "sp_process_payment procedure"

echo "--- Trigger & View Verification ---"
check_object "TRIGGER.*trg_allocations_prevent_double_booking" "trg_allocations_prevent_double_booking trigger"
check_object "VIEW.*v_current_occupancy" "v_current_occupancy view"

echo "[VERIFICATION COMPLETE]"
