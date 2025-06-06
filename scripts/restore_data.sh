#!/bin/bash

# NiveshakAI Data Restore Script
# Restores data from backup archives created by backup_data.sh

set -e

# Configuration
BACKUP_DIR="$HOME/niveshak-ai-backups"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESTORE_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Help function
show_help() {
    echo "NiveshakAI Data Restore Script"
    echo ""
    echo "Usage: $0 <backup_file> [options]"
    echo ""
    echo "Arguments:"
    echo "  backup_file   Path to backup file (e.g., niveshak_backup_20241201_143022.tar.gz)"
    echo "                Can be full path or just filename (will search in backup directory)"
    echo ""
    echo "Options:"
    echo "  --dry-run     Show what would be restored without actually restoring"
    echo "  --force       Skip confirmation prompts"
    echo "  --selective   Choose specific components to restore"
    echo "  --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 niveshak_backup_20241201_143022.tar.gz"
    echo "  $0 /path/to/backup.tar.gz --dry-run"
    echo "  $0 latest --selective"
    echo ""
    echo "Backup directory: $BACKUP_DIR"
}

# Find backup file
find_backup_file() {
    local backup_arg="$1"

    # If it's "latest", find the most recent backup
    if [ "$backup_arg" = "latest" ]; then
        backup_file=$(ls -1t "$BACKUP_DIR"/niveshak_backup_*.tar.gz 2>/dev/null | head -1)
        if [ -z "$backup_file" ]; then
            error "No backups found in $BACKUP_DIR"
            exit 1
        fi
        return
    fi

    # If it's a full path, use it directly
    if [ -f "$backup_arg" ]; then
        backup_file="$backup_arg"
        return
    fi

    # If it's just a filename, look in backup directory
    if [ -f "$BACKUP_DIR/$backup_arg" ]; then
        backup_file="$BACKUP_DIR/$backup_arg"
        return
    fi

    error "Backup file not found: $backup_arg"
    error "Searched in: $BACKUP_DIR"
    exit 1
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"

    log "🔍 Verifying backup integrity..."

    # Check if checksum file exists
    if [ -f "${backup_file}.sha256" ]; then
        info "Verifying SHA256 checksum..."
        if cd "$(dirname "$backup_file")" && shasum -a 256 -c "$(basename "${backup_file}.sha256")" >/dev/null 2>&1; then
            log "✅ Backup integrity verified"
        else
            error "Backup integrity check failed!"
            exit 1
        fi
    else
        warning "No checksum file found, skipping integrity verification"
    fi
}

# Extract and examine backup
extract_backup() {
    local backup_file="$1"

    log "📦 Extracting backup archive..."

    # Create temporary extraction directory
    temp_dir="/tmp/niveshak_restore_${RESTORE_TIMESTAMP}"
    mkdir -p "$temp_dir"

    # Extract backup
    tar -xzf "$backup_file" -C "$temp_dir"

    # Find the backup directory (should be only one)
    backup_content_dir=$(find "$temp_dir" -maxdepth 1 -type d -name "niveshak_backup_*" | head -1)

    if [ -z "$backup_content_dir" ]; then
        error "Could not find backup content directory in archive"
        exit 1
    fi

    log "✅ Backup extracted to: $backup_content_dir"
    echo "$backup_content_dir"
}

# Show backup contents
show_backup_info() {
    local backup_dir="$1"

    echo ""
    echo -e "${BLUE}📋 Backup Information${NC}"
    echo "===================="

    if [ -f "$backup_dir/backup_info.json" ]; then
        echo "Backup Date: $(grep 'backup_date' "$backup_dir/backup_info.json" | cut -d'"' -f4)"
        echo "Backup Version: $(grep 'backup_version' "$backup_dir/backup_info.json" | cut -d'"' -f4)"
        echo ""
        echo "Contents:"

        # Parse JSON to show what's included
        if command -v jq >/dev/null 2>&1; then
            jq -r '.contents | to_entries[] | "  • \(.key): \(.value)"' "$backup_dir/backup_info.json"
        else
            grep -E '"(qdrant_storage|weaviate_data|books|embeddings|config|env_file)":' "$backup_dir/backup_info.json" |
                sed 's/.*"\([^"]*\)": *\([^,]*\).*/  • \1: \2/'
        fi
    else
        warning "No backup metadata found"
        echo "Archive contents:"
        ls -la "$backup_dir" | grep -v "^total" | awk '{print "  • " $9 " (" $5 " bytes)"}'
    fi
    echo ""
}

# Create backup of current data before restore
backup_current_data() {
    log "💾 Creating backup of current data before restore..."

    if [ -d "$PROJECT_DIR/data" ]; then
        backup_current_dir="$PROJECT_DIR/data_backup_before_restore_${RESTORE_TIMESTAMP}"
        cp -r "$PROJECT_DIR/data" "$backup_current_dir"
        log "✅ Current data backed up to: $backup_current_dir"
        echo "$backup_current_dir"
    else
        log "ℹ️ No existing data directory to backup"
        echo ""
    fi
}

# Restore vector databases
restore_vector_db() {
    local backup_dir="$1"

    log "📊 Restoring vector databases..."

    # Restore Qdrant
    if [ -f "$backup_dir/qdrant_storage.tar.gz" ]; then
        if [ -d "$PROJECT_DIR/data/qdrant_storage" ]; then
            rm -rf "$PROJECT_DIR/data/qdrant_storage"
        fi
        tar -xzf "$backup_dir/qdrant_storage.tar.gz" -C "$PROJECT_DIR/data/"
        log "✅ Qdrant database restored"
    fi

    # Restore Weaviate
    if [ -f "$backup_dir/weaviate_data.tar.gz" ]; then
        if [ -d "$PROJECT_DIR/data/weaviate_data" ]; then
            rm -rf "$PROJECT_DIR/data/weaviate_data"
        fi
        tar -xzf "$backup_dir/weaviate_data.tar.gz" -C "$PROJECT_DIR/data/"
        log "✅ Weaviate database restored"
    fi
}

# Restore books
restore_books() {
    local backup_dir="$1"

    log "📚 Restoring knowledge base (books)..."

    if [ -f "$backup_dir/books.tar.gz" ]; then
        if [ -d "$PROJECT_DIR/data/books" ]; then
            rm -rf "$PROJECT_DIR/data/books"
        fi
        tar -xzf "$backup_dir/books.tar.gz" -C "$PROJECT_DIR/data/"
        log "✅ Books restored"
    fi
}

# Restore embeddings
restore_embeddings() {
    local backup_dir="$1"

    log "🧠 Restoring embeddings cache..."

    if [ -f "$backup_dir/embeddings.tar.gz" ]; then
        if [ -d "$PROJECT_DIR/data/embeddings" ]; then
            rm -rf "$PROJECT_DIR/data/embeddings"
        fi
        tar -xzf "$backup_dir/embeddings.tar.gz" -C "$PROJECT_DIR/data/"
        log "✅ Embeddings cache restored"
    fi
}

# Restore configuration
restore_config() {
    local backup_dir="$1"

    log "⚙️ Restoring configuration files..."

    if [ -d "$backup_dir/config" ]; then
        if [ -d "$PROJECT_DIR/config" ]; then
            cp -r "$PROJECT_DIR/config" "$PROJECT_DIR/config_backup_${RESTORE_TIMESTAMP}"
            warning "Existing config backed up to: config_backup_${RESTORE_TIMESTAMP}"
        fi
        cp -r "$backup_dir/config" "$PROJECT_DIR/"
        log "✅ Configuration files restored"
    fi

    if [ -f "$backup_dir/.env" ]; then
        if [ -f "$PROJECT_DIR/.env" ]; then
            cp "$PROJECT_DIR/.env" "$PROJECT_DIR/.env_backup_${RESTORE_TIMESTAMP}"
            warning "Existing .env backed up to: .env_backup_${RESTORE_TIMESTAMP}"
        fi
        cp "$backup_dir/.env" "$PROJECT_DIR/"
        log "✅ Environment file restored"
    fi
}

# Selective restore
selective_restore() {
    local backup_dir="$1"

    echo ""
    echo -e "${BLUE}🎯 Selective Restore${NC}"
    echo "=================="
    echo "Choose components to restore:"
    echo ""

    components=()
    [ -f "$backup_dir/qdrant_storage.tar.gz" ] && components+=("vector_db:Qdrant Vector Database")
    [ -f "$backup_dir/weaviate_data.tar.gz" ] && components+=("weaviate:Weaviate Database")
    [ -f "$backup_dir/books.tar.gz" ] && components+=("books:Knowledge Base (Books)")
    [ -f "$backup_dir/embeddings.tar.gz" ] && components+=("embeddings:Embeddings Cache")
    [ -d "$backup_dir/config" ] && components+=("config:Configuration Files")
    [ -f "$backup_dir/.env" ] && components+=("env:Environment File")

    for i in "${!components[@]}"; do
        echo "$((i + 1)). ${components[$i]#*:}"
    done
    echo "a. All components"
    echo "q. Quit"
    echo ""

    read -p "Enter your choice (numbers separated by spaces, 'a' for all, 'q' to quit): " choice

    case "$choice" in
    "q" | "quit" | "exit")
        echo "Restore cancelled."
        exit 0
        ;;
    "a" | "all")
        restore_vector_db "$backup_dir"
        restore_books "$backup_dir"
        restore_embeddings "$backup_dir"
        restore_config "$backup_dir"
        ;;
    *)
        for num in $choice; do
            if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le "${#components[@]}" ]; then
                component_key="${components[$((num - 1))]%:*}"
                case "$component_key" in
                "vector_db") restore_vector_db "$backup_dir" ;;
                "weaviate") restore_vector_db "$backup_dir" ;;
                "books") restore_books "$backup_dir" ;;
                "embeddings") restore_embeddings "$backup_dir" ;;
                "config") restore_config "$backup_dir" ;;
                "env") restore_config "$backup_dir" ;;
                esac
            else
                warning "Invalid choice: $num"
            fi
        done
        ;;
    esac
}

# Full restore
full_restore() {
    local backup_dir="$1"

    log "🔄 Starting full restore..."

    # Ensure data directory exists
    mkdir -p "$PROJECT_DIR/data"

    restore_vector_db "$backup_dir"
    restore_books "$backup_dir"
    restore_embeddings "$backup_dir"
    restore_config "$backup_dir"
}

# Cleanup
cleanup() {
    local temp_dir="$1"

    if [ -n "$temp_dir" ] && [ -d "$temp_dir" ]; then
        rm -rf "$temp_dir"
        log "🧹 Temporary files cleaned up"
    fi
}

# Main restore function
main() {
    local backup_arg="$1"
    local dry_run="$2"
    local force="$3"
    local selective="$4"

    if [ -z "$backup_arg" ]; then
        error "No backup file specified"
        show_help
        exit 1
    fi

    echo -e "${BLUE}🔄 NiveshakAI Data Restore Starting...${NC}"
    echo "======================================"
    echo "Timestamp: $(date)"
    echo "Project: $PROJECT_DIR"
    echo ""

    # Find and verify backup
    find_backup_file "$backup_arg"
    verify_backup "$backup_file"

    echo "Backup file: $backup_file"
    echo "Backup size: $(du -sh "$backup_file" | cut -f1)"
    echo ""

    # Extract backup
    backup_content_dir=$(extract_backup "$backup_file")

    # Show backup information
    show_backup_info "$backup_content_dir"

    # Dry run mode
    if [ "$dry_run" = "true" ]; then
        echo -e "${YELLOW}🔍 DRY RUN MODE - No changes will be made${NC}"
        echo ""
        echo "Would restore the following components:"
        [ -f "$backup_content_dir/qdrant_storage.tar.gz" ] && echo "  ✓ Qdrant Vector Database"
        [ -f "$backup_content_dir/weaviate_data.tar.gz" ] && echo "  ✓ Weaviate Database"
        [ -f "$backup_content_dir/books.tar.gz" ] && echo "  ✓ Knowledge Base (Books)"
        [ -f "$backup_content_dir/embeddings.tar.gz" ] && echo "  ✓ Embeddings Cache"
        [ -d "$backup_content_dir/config" ] && echo "  ✓ Configuration Files"
        [ -f "$backup_content_dir/.env" ] && echo "  ✓ Environment File"
        cleanup "$backup_content_dir"
        exit 0
    fi

    # Confirmation prompt (unless forced)
    if [ "$force" != "true" ]; then
        echo -e "${YELLOW}⚠️  WARNING: This will replace your current NiveshakAI data!${NC}"
        echo ""
        read -p "Are you sure you want to continue? (yes/no): " confirm
        if [ "$confirm" != "yes" ] && [ "$confirm" != "y" ]; then
            echo "Restore cancelled."
            cleanup "$backup_content_dir"
            exit 0
        fi
    fi

    # Backup current data
    current_backup_dir=$(backup_current_data)

    # Perform restore
    if [ "$selective" = "true" ]; then
        selective_restore "$backup_content_dir"
    else
        full_restore "$backup_content_dir"
    fi

    # Cleanup
    cleanup "$backup_content_dir"

    echo ""
    echo -e "${GREEN}🎉 Restore completed successfully!${NC}"
    echo "======================================"
    echo "Restored from: $backup_file"
    echo "Project directory: $PROJECT_DIR"
    if [ -n "$current_backup_dir" ]; then
        echo "Previous data backed up to: $current_backup_dir"
    fi
    echo ""
    echo -e "${BLUE}💡 Next steps:${NC}"
    echo "1. Verify that your NiveshakAI system is working correctly"
    echo "2. Test vector database connectivity"
    echo "3. Check that all your books and embeddings are accessible"
}

# Parse command line arguments
backup_file=""
dry_run=false
force=false
selective=false

while [[ $# -gt 0 ]]; do
    case $1 in
    --dry-run)
        dry_run=true
        shift
        ;;
    --force)
        force=true
        shift
        ;;
    --selective)
        selective=true
        shift
        ;;
    --help | -h | help)
        show_help
        exit 0
        ;;
    *)
        if [ -z "$backup_file" ]; then
            backup_file="$1"
        else
            error "Unknown option: $1"
            exit 1
        fi
        shift
        ;;
    esac
done

# Run main function
main "$backup_file" "$dry_run" "$force" "$selective"
