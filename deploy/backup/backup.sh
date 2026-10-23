#!/usr/bin/env bash
# Sao lưu CSDL (pg_dump -Fc) và kho tệp (tar) vào thư mục có ngày giờ; giữ KEEP bản gần nhất (T-603).
# Chạy 01:00 hằng ngày: `0 1 * * * cd /opt/cwd && deploy/backup/backup.sh`
# Thất bại: mã thoát khác 0, tệp `last_failure`, và (nếu có TEXTFILE_DIR) chỉ số cho cảnh báo SaoLuuThatBai.
set -uo pipefail
export MSYS_NO_PATHCONV=1  # Git Bash trên Windows tự đổi /srv/... thành đường dẫn Windows

BACKUP_DIR="${BACKUP_DIR:-/var/backups/cwd}"
KEEP="${KEEP:-7}"
STAMP="${BACKUP_STAMP:-$(date +%Y%m%d-%H%M%S)}"
COMPOSE="${COMPOSE:-docker compose -p cwd -f deploy/compose.prod.yml --env-file deploy/.env}"
TEXTFILE_DIR="${TEXTFILE_DIR:-}"

metric() { # $1 = giá trị (0 nếu ổn, epoch nếu lỗi)
  [ -n "$TEXTFILE_DIR" ] && printf 'cwd_backup_last_failure_timestamp_seconds %s\n' "$1" > "$TEXTFILE_DIR/cwd_backup.prom"
  return 0
}

log() { echo "$(date -Is) $*" | tee -a "$BACKUP_DIR/backup.log" 2>/dev/null || echo "$(date -Is) $*"; }

fail() {
  log "BACKUP FAILED: $1"
  echo "$(date -Is) $1" > "$BACKUP_DIR/last_failure" 2>/dev/null || echo "$(date -Is) $1" > "./last_failure"
  metric "$(date +%s)"
  exit 1
}

mkdir -p "$BACKUP_DIR" 2>/dev/null
[ -w "$BACKUP_DIR" ] || fail "thư mục sao lưu không ghi được: $BACKUP_DIR"

target="$BACKUP_DIR/$STAMP"
mkdir "$target" 2>/dev/null || fail "không tạo được $target"

start=$(date +%s)
# shellcheck disable=SC2086
$COMPOSE exec -T db sh -c 'pg_dump -Fc -U "$POSTGRES_USER" "$POSTGRES_DB"' > "$target/db.dump" \
  || fail "pg_dump lỗi"
[ -s "$target/db.dump" ] || fail "db.dump rỗng"

# shellcheck disable=SC2086
$COMPOSE exec -T api tar -C /srv/storage -cf - . > "$target/storage.tar" || fail "tar kho tệp lỗi"
[ -s "$target/storage.tar" ] || fail "storage.tar rỗng"

# Giữ KEEP bản gần nhất (tên thư mục sắp xếp theo thời gian)
ls -1d "$BACKUP_DIR"/*/ 2>/dev/null | sort | head -n -"$KEEP" | while read -r old; do rm -rf "$old"; done

rm -f "$BACKUP_DIR/last_failure"
metric 0
log "BACKUP OK $STAMP ($(( $(date +%s) - start ))s, db=$(wc -c < "$target/db.dump")B, storage=$(wc -c < "$target/storage.tar")B)"
