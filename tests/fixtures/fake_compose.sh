#!/usr/bin/env bash
# Giả `docker compose` cho test của backup.sh: không cần Docker.
case "$*" in
  *"exec -T db"*) [ -n "${FAKE_FAIL_DB:-}" ] && exit 1; printf 'PGDMP-fake-dump' ;;
  *"exec -T api tar"*) tar -cf - -C "$(dirname "$0")" fake_compose.sh ;;
  *) exit 0 ;;
esac
