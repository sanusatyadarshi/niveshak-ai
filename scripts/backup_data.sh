#!/bin/bash

# NiveshakAI Data Backup Script
# Backs up all critical data including vector databases, books, and configurations

set -e

# Configuration
BACKUP_DIR="$HOME/niveshak-ai-backups"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="niveshak_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 NiveshakAI Data Backup Starting...${NC}"
echo "======================================"
echo "Timestamp: $(date)"
echo "Project: $PROJECT_DIR"
echo "Backup to: $BACKUP_PATH"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_PATH"

# Function to log with timestamp
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Check if source directories exist
check_source() {
    if [ ! -d "$PROJECT_DIR" ]; then
        error "Project directory not found: $PROJECT_DIR"
        exit 1
    fi

    if [ ! -d "$PROJECT_DIR/data" ]; then
        error "Data directory not found: $PROJECT_DIR/data"
        exit 1
    fi
}

# Backup vector database (Qdrant)
backup_vector_db() {
    log "📊 Backing up Qdrant vector database..."

    if [ -d "$PROJECT_DIR/data/qdrant_storage" ]; then
        tar -czf "$BACKUP_PATH/qdrant_storage.tar.gz" -C "$PROJECT_DIR/data" qdrant_storage/
        log "✅ Qdrant database backed up ($(du -sh "$PROJECT_DIR/data/qdrant_storage" | cut -f1))"
    else
        warning "Qdrant storage directory not found"
    fi

    # Also backup Weaviate if exists
    if [ -d "$PROJECT_DIR/data/weaviate_data" ]; then
        tar -czf "$BACKUP_PATH/weaviate_data.tar.gz" -C "$PROJECT_DIR/data" weaviate_data/
        log "✅ Weaviate database backed up ($(du -sh "$PROJECT_DIR/data/weaviate_data" | cut -f1))"
    fi
}

# Backup knowledge base (books)
backup_books() {
    log "📚 Backing up knowledge base (books)..."

    if [ -d "$PROJECT_DIR/data/books" ]; then
        tar -czf "$BACKUP_PATH/books.tar.gz" -C "$PROJECT_DIR/data" books/
        log "✅ Books backed up ($(du -sh "$PROJECT_DIR/data/books" | cut -f1))"
    else
        warning "Books directory not found"
    fi
}

# Backup embeddings cache
backup_embeddings() {
    log "🧠 Backing up embeddings cache..."

    if [ -d "$PROJECT_DIR/data/embeddings" ]; then
        tar -czf "$BACKUP_PATH/embeddings.tar.gz" -C "$PROJECT_DIR/data" embeddings/
        log "✅ Embeddings cache backed up"
    fi
}

# Backup configuration files
backup_config() {
    log "⚙️ Backing up configuration files..."

    if [ -d "$PROJECT_DIR/config" ]; then
        cp -r "$PROJECT_DIR/config" "$BACKUP_PATH/"
        log "✅ Configuration files backed up"
    fi

    # Backup .env if exists
    if [ -f "$PROJECT_DIR/.env" ]; then
        cp "$PROJECT_DIR/.env" "$BACKUP_PATH/"
        log "✅ Environment file backed up"
    fi
}

# Backup logs (recent only)
backup_logs() {
    log "📝 Backing up recent logs..."

    if [ -d "$PROJECT_DIR/logs" ]; then
        # Only backup logs from last 30 days
        find "$PROJECT_DIR/logs" -name "*.log" -mtime -30 -exec cp {} "$BACKUP_PATH/" \; 2>/dev/null || true
        log "✅ Recent logs backed up"
    fi
}

# Create backup metadata
create_metadata() {
    log "📋 Creating backup metadata..."

    cat >"$BACKUP_PATH/backup_info.json" <<EOF
{
  "backup_timestamp": "${TIMESTAMP}",
  "backup_date": "$(date -Iseconds)",
  "project_dir": "${PROJECT_DIR}",
  "backup_version": "1.0",
  "niveshak_version": "$(grep version $PROJECT_DIR/config/settings.yaml | head -1 | cut -d':' -f2 | tr -d ' ')",
  "contents": {
    "qdrant_storage": $([ -f "$BACKUP_PATH/qdrant_storage.tar.gz" ] && echo "true" || echo "false"),
    "weaviate_data": $([ -f "$BACKUP_PATH/weaviate_data.tar.gz" ] && echo "true" || echo "false"),
    "books": $([ -f "$BACKUP_PATH/books.tar.gz" ] && echo "true" || echo "false"),
    "embeddings": $([ -f "$BACKUP_PATH/embeddings.tar.gz" ] && echo "true" || echo "false"),
    "config": $([ -d "$BACKUP_PATH/config" ] && echo "true" || echo "false"),
    "env_file": $([ -f "$BACKUP_PATH/.env" ] && echo "true" || echo "false")
  },
  "file_counts": {
    "books": $(find "$PROJECT_DIR/data/books" -name "*.pdf" 2>/dev/null | wc -l || echo 0),
    "config_files": $(find "$PROJECT_DIR/config" -name "*.yaml" 2>/dev/null | wc -l || echo 0)
  },
  "sizes": {
    "qdrant_mb": $(du -sm "$PROJECT_DIR/data/qdrant_storage" 2>/dev/null | cut -f1 || echo 0),
    "books_mb": $(du -sm "$PROJECT_DIR/data/books" 2>/dev/null | cut -f1 || echo 0),
    "total_backup_mb": $(du -sm "$BACKUP_PATH" | cut -f1)
  }
}
EOF

    log "✅ Backup metadata created"
}

# Create backup archive
create_archive() {
    log "📦 Creating final backup archive..."

    cd "$BACKUP_DIR"
    tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME/"

    # Calculate checksums
    shasum -a 256 "${BACKUP_NAME}.tar.gz" >"${BACKUP_NAME}.tar.gz.sha256"

    # Remove uncompressed backup directory
    rm -rf "$BACKUP_NAME"

    ARCHIVE_SIZE=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)
    log "✅ Final archive created: ${BACKUP_NAME}.tar.gz (${ARCHIVE_SIZE})"
}

# Cleanup old backups (keep last 5)
cleanup_old_backups() {
    log "🧹 Cleaning up old backups (keeping last 5)..."

    cd "$BACKUP_DIR"
    ls -1t niveshak_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f || true
    ls -1t niveshak_backup_*.tar.gz.sha256 2>/dev/null | tail -n +6 | xargs rm -f || true

    REMAINING=$(ls -1 niveshak_backup_*.tar.gz 2>/dev/null | wc -l || echo 0)
    log "✅ Cleanup complete. ${REMAINING} backups retained."
}

# Main backup process
main() {
    check_source
    backup_vector_db
    backup_books
    backup_embeddings
    backup_config
    backup_logs
    create_metadata
    create_archive
    cleanup_old_backups

    echo ""
    echo -e "${GREEN}🎉 Backup completed successfully!${NC}"
    echo "======================================"
    echo "Backup location: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    echo "Archive size: $(du -sh "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" 2>/dev/null | cut -f1 || echo "Unknown")"
    echo "Checksum file: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz.sha256"
    echo ""
    echo -e "${BLUE}To restore this backup later, run:${NC}"
    echo "./scripts/restore_data.sh ${BACKUP_NAME}.tar.gz"
    echo ""
    echo -e "${BLUE}To list all backups, run:${NC}"
    echo "./scripts/manage_backups.sh list"
}

# Handle command line arguments
case "${1:-backup}" in
"backup" | "")
    main
    ;;
"help" | "-h" | "--help")
    echo "NiveshakAI Data Backup Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  backup    Create a new backup (default)"
    echo "  help      Show this help message"
    echo ""
    echo "The backup includes:"
    echo "  • Vector database (Qdrant/Weaviate)"
    echo "  • Knowledge base (PDF books)"
    echo "  • Embeddings cache"
    echo "  • Configuration files"
    echo "  • Recent logs"
    echo ""
    echo "Backups are stored in: $BACKUP_DIR"
    ;;
*)
    error "Unknown command: $1"
    echo "Use '$0 help' for usage information."
    exit 1
    ;;
esac
