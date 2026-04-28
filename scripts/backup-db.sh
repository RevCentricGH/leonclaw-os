#!/bin/bash
# Nightly backup of claudeclaw.db
# Keeps last 7 days of backups

JARVIS_ROOT=$(cd "$(dirname "$0")/.." && git rev-parse --show-toplevel)
DB="$JARVIS_ROOT/store/claudeclaw.db"
BACKUP_DIR="$JARVIS_ROOT/store/backups"
DATE=$(date +%Y-%m-%d)

mkdir -p "$BACKUP_DIR"

# Copy DB to dated backup
cp "$DB" "$BACKUP_DIR/claudeclaw-$DATE.db"

# Delete backups older than 7 days
find "$BACKUP_DIR" -name "claudeclaw-*.db" -mtime +7 -delete

echo "Backup complete: $BACKUP_DIR/claudeclaw-$DATE.db"
