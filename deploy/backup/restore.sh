#!/usr/bin/env bash
# Khôi phục từ một thư mục sao lưu: `deploy/backup/restore.sh /var/backups/cwd/20261201-010000` (T-603).
# Dừng api và worker, nạp lại CSDL và kho tệp, khởi động lại; in thời gian từng bước.
set -euo pipefail
export MSYS_NO_PATHCONV=1

SRC="${1:?cách dùng: restore.sh <thư mục bản sao lưu>}"
COMPOSE="${COMPOSE:-docker compose -p cwd -f deploy/compose.prod.yml --env-file deploy/.env}"
[ -s "$SRC/db.dump" ] && [ -s "$SRC/storage.tar" ] || { echo "Thiếu db.dump hoặc storage.tar trong $SRC" >&2; exit 1; }

step() { local name="$1"; shift; local t=$(date +%s); "$@"; echo "[$(( $(date +%s) - t ))s] $name"; }
total=$(date +%s)

# shellcheck disable=SC2086
step "dừng api, worker" $COMPOSE stop api worker web

# shellcheck disable=SC2086
step "khôi phục CSDL (pg_restore --clean)" bash -c \
  "$COMPOSE exec -T db sh -c 'pg_restore --clean --if-exists --no-owner -U \"\$POSTGRES_USER\" -d \"\$POSTGRES_DB\"' < '$SRC/db.dump'"

# shellcheck disable=SC2086
step "khôi phục kho tệp" bash -c \
  "$COMPOSE run --rm --no-deps -T --entrypoint sh api -c 'rm -rf /srv/storage/* /srv/storage/.[!.]* 2>/dev/null; tar -C /srv/storage -xf -' < '$SRC/storage.tar'"

# shellcheck disable=SC2086
step "khởi động lại" $COMPOSE up -d api worker web

echo "[$(( $(date +%s) - total ))s] TỔNG; tuổi dữ liệu: bản sao lưu $(basename "$SRC")"
