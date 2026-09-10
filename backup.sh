#!/usr/bin/env bash
# Simple backup for the label-manager data directory.
# Usage: ./backup.sh [backup_root]
set -euo pipefail

DATA_DIR="${DATA_DIR:-./data}"
BACKUP_ROOT="${1:-./backups}"
STAMP="$(date +%Y-%m-%d_%H-%M)"
DEST="$BACKUP_ROOT/$STAMP"

mkdir -p "$DEST"

if [ -f "$DATA_DIR/places.db" ]; then
  sqlite3 "$DATA_DIR/places.db" ".backup '$DEST/places.db'"
  echo "DB  -> $DEST/places.db"
fi

if [ -d "$DATA_DIR/uploads" ]; then
  rsync -a "$DATA_DIR/uploads/" "$DEST/uploads/"
  echo "IMG -> $DEST/uploads/"
fi

echo "Done: $DEST"