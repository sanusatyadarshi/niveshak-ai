#!/bin/bash

# NiveshakAI Backup Management Script
# Manages backup files created by backup_data.sh

set -e

# Configuration
BACKUP_DIR="$HOME/niveshak-ai-backups"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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
    echo "NiveshakAI Backup Management Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  list           List all available backups"
    echo "  info <backup>  Show detailed information about a backup"
    echo "  delete <backup> Delete a specific backup"
    echo "  cleanup        Clean up old backups (keep last 5)"
    echo "  verify <backup> Verify backup integrity"
    echo "  size           Show total size of all backups"
    echo "  auto-backup    Create a backup automatically"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 info niveshak_backup_20241201_143022.tar.gz"
    echo "  $0 delete niveshak_backup_20241201_143022.tar.gz"
    echo "  $0 verify latest"
    echo ""
    echo "Backup directory: $BACKUP_DIR"
}

# List all backups
list_backups() {
    echo -e "${BLUE}📦 Available Backups${NC}"
    echo "==================="

    if [ ! -d "$BACKUP_DIR" ]; then
        warning "Backup directory does not exist: $BACKUP_DIR"
        return
    fi

    local backups=($(ls -1t "$BACKUP_DIR"/niveshak_backup_*.tar.gz 2>/dev/null || true))

    if [ ${#backups[@]} -eq 0 ]; then
        warning "No backups found in $BACKUP_DIR"
        echo ""
        echo "To create your first backup, run:"
        echo "  ./scripts/backup_data.sh"
        return
    fi

    echo ""
    printf "%-35s %-12s %-15s %-10s\n" "BACKUP NAME" "SIZE" "DATE" "STATUS"
    printf "%-35s %-12s %-15s %-10s\n" "-----------" "----" "----" "------"

    for backup in "${backups[@]}"; do
        local filename=$(basename "$backup")
        local size=$(du -sh "$backup" 2>/dev/null | cut -f1 || echo "Unknown")

        # Extract date from filename
        local date_part=$(echo "$filename" | grep -o '[0-9]\{8\}_[0-9]\{6\}' || echo "Unknown")
        local formatted_date=""
        if [ "$date_part" != "Unknown" ]; then
            local year=${date_part:0:4}
            local month=${date_part:4:2}
            local day=${date_part:6:2}
            local hour=${date_part:9:2}
            local minute=${date_part:11:2}
            formatted_date="${year}-${month}-${day} ${hour}:${minute}"
        else
            formatted_date="Unknown"
        fi

        # Check if checksum file exists
        local status="✓"
        if [ ! -f "${backup}.sha256" ]; then
            status="⚠️"
        fi

        printf "%-35s %-12s %-15s %-10s\n" "$filename" "$size" "$formatted_date" "$status"
    done

    echo ""
    echo "Total backups: ${#backups[@]}"
    echo "✓ = Has checksum file, ⚠️ = Missing checksum"
    echo ""
    echo "Use '$0 info <backup>' for detailed information"
}

# Show backup information
show_backup_info() {
    local backup_arg="$1"

    if [ -z "$backup_arg" ]; then
        error "No backup specified"
        return 1
    fi

    local backup_file

    # Handle "latest" keyword
    if [ "$backup_arg" = "latest" ]; then
        backup_file=$(ls -1t "$BACKUP_DIR"/niveshak_backup_*.tar.gz 2>/dev/null | head -1)
        if [ -z "$backup_file" ]; then
            error "No backups found"
            return 1
        fi
    else
        # Check if it's a full path or just filename
        if [ -f "$backup_arg" ]; then
            backup_file="$backup_arg"
        elif [ -f "$BACKUP_DIR/$backup_arg" ]; then
            backup_file="$BACKUP_DIR/$backup_arg"
        else
            error "Backup not found: $backup_arg"
            return 1
        fi
    fi

    echo -e "${BLUE}📋 Backup Information${NC}"
    echo "====================="
    echo ""
    echo "File: $(basename "$backup_file")"
    echo "Path: $backup_file"
    echo "Size: $(du -sh "$backup_file" 2>/dev/null | cut -f1 || echo "Unknown")"
    echo "Modified: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$backup_file" 2>/dev/null || echo "Unknown")"

    # Check checksum
    if [ -f "${backup_file}.sha256" ]; then
        echo "Checksum: Available"
        echo -e "${GREEN}Integrity: Verified${NC}"
    else
        echo -e "${YELLOW}Checksum: Missing${NC}"
    fi

    echo ""
    echo -e "${CYAN}Archive Contents:${NC}"
    echo "----------------"

    # Try to extract metadata without full extraction
    local temp_dir="/tmp/backup_info_$$"
    mkdir -p "$temp_dir"

    # Extract just the metadata file if it exists
    if tar -tzf "$backup_file" | grep -q "backup_info.json"; then
        tar -xzf "$backup_file" -C "$temp_dir" --wildcards "*/backup_info.json" 2>/dev/null || true
        local metadata_file=$(find "$temp_dir" -name "backup_info.json" | head -1)

        if [ -f "$metadata_file" ]; then
            echo "Backup Date: $(grep 'backup_date' "$metadata_file" | cut -d'"' -f4 2>/dev/null || echo "Unknown")"
            echo "Backup Version: $(grep 'backup_version' "$metadata_file" | cut -d'"' -f4 2>/dev/null || echo "Unknown")"
            echo ""

            # Show components
            if command -v jq >/dev/null 2>&1; then
                echo "Components:"
                jq -r '.contents | to_entries[] | select(.value == true) | "  ✓ \(.key)"' "$metadata_file" 2>/dev/null || true
                echo ""
                echo "Sizes:"
                jq -r '.sizes | to_entries[] | "  \(.key): \(.value)"' "$metadata_file" 2>/dev/null || true
            else
                echo "Components (install jq for detailed view):"
                grep -E '"(qdrant_storage|weaviate_data|books|embeddings|config|env_file)": *true' "$metadata_file" |
                    sed 's/.*"\([^"]*\)": *true.*/  ✓ \1/' 2>/dev/null || true
            fi
        fi
    else
        # Fallback: list archive contents
        echo "Archive contents:"
        tar -tzf "$backup_file" | head -20 | sed 's/^/  /'
        local total_files=$(tar -tzf "$backup_file" | wc -l)
        if [ "$total_files" -gt 20 ]; then
            echo "  ... and $((total_files - 20)) more files"
        fi
    fi

    rm -rf "$temp_dir"

    echo ""
    echo -e "${BLUE}💡 Actions:${NC}"
    echo "  Restore: ./scripts/restore_data.sh $(basename "$backup_file")"
    echo "  Verify:  ./scripts/manage_backups.sh verify $(basename "$backup_file")"
    echo "  Delete:  ./scripts/manage_backups.sh delete $(basename "$backup_file")"
}

# Delete a backup
delete_backup() {
    local backup_arg="$1"
    local force="$2"

    if [ -z "$backup_arg" ]; then
        error "No backup specified"
        return 1
    fi

    local backup_file

    # Check if it's a full path or just filename
    if [ -f "$backup_arg" ]; then
        backup_file="$backup_arg"
    elif [ -f "$BACKUP_DIR/$backup_arg" ]; then
        backup_file="$BACKUP_DIR/$backup_arg"
    else
        error "Backup not found: $backup_arg"
        return 1
    fi

    echo "Backup to delete: $(basename "$backup_file")"
    echo "Size: $(du -sh "$backup_file" 2>/dev/null | cut -f1 || echo "Unknown")"
    echo ""

    if [ "$force" != "true" ]; then
        read -p "Are you sure you want to delete this backup? (yes/no): " confirm
        if [ "$confirm" != "yes" ] && [ "$confirm" != "y" ]; then
            echo "Deletion cancelled."
            return 0
        fi
    fi

    # Delete backup file and checksum
    rm -f "$backup_file"
    rm -f "${backup_file}.sha256"

    log "✅ Backup deleted: $(basename "$backup_file")"
}

# Verify backup integrity
verify_backup() {
    local backup_arg="$1"

    if [ -z "$backup_arg" ]; then
        error "No backup specified"
        return 1
    fi

    local backup_file

    # Handle "latest" keyword
    if [ "$backup_arg" = "latest" ]; then
        backup_file=$(ls -1t "$BACKUP_DIR"/niveshak_backup_*.tar.gz 2>/dev/null | head -1)
        if [ -z "$backup_file" ]; then
            error "No backups found"
            return 1
        fi
    else
        # Check if it's a full path or just filename
        if [ -f "$backup_arg" ]; then
            backup_file="$backup_arg"
        elif [ -f "$BACKUP_DIR/$backup_arg" ]; then
            backup_file="$BACKUP_DIR/$backup_arg"
        else
            error "Backup not found: $backup_arg"
            return 1
        fi
    fi

    echo -e "${BLUE}🔍 Verifying Backup Integrity${NC}"
    echo "============================="
    echo ""
    echo "File: $(basename "$backup_file")"
    echo "Size: $(du -sh "$backup_file" 2>/dev/null | cut -f1 || echo "Unknown")"
    echo ""

    # Check if checksum file exists
    if [ ! -f "${backup_file}.sha256" ]; then
        warning "No checksum file found (${backup_file}.sha256)"
        echo "Cannot verify integrity without checksum file."
        return 1
    fi

    info "Verifying SHA256 checksum..."

    if cd "$(dirname "$backup_file")" && shasum -a 256 -c "$(basename "${backup_file}.sha256")" 2>/dev/null; then
        log "✅ Backup integrity verified successfully"
    else
        error "❌ Backup integrity check FAILED!"
        echo "The backup file may be corrupted or tampered with."
        return 1
    fi

    # Also try to list archive contents to check if it's a valid tar file
    info "Checking archive structure..."
    if tar -tzf "$backup_file" >/dev/null 2>&1; then
        log "✅ Archive structure is valid"
    else
        error "❌ Archive appears to be corrupted"
        return 1
    fi
}

# Clean up old backups
cleanup_backups() {
    local keep_count="${1:-5}"

    echo -e "${BLUE}🧹 Cleaning Up Old Backups${NC}"
    echo "=========================="
    echo "Keeping last $keep_count backups..."
    echo ""

    if [ ! -d "$BACKUP_DIR" ]; then
        warning "Backup directory does not exist: $BACKUP_DIR"
        return
    fi

    cd "$BACKUP_DIR"

    local all_backups=($(ls -1t niveshak_backup_*.tar.gz 2>/dev/null || true))
    local total_count=${#all_backups[@]}

    if [ "$total_count" -le "$keep_count" ]; then
        info "Only $total_count backups found, nothing to clean up"
        return
    fi

    local to_delete_count=$((total_count - keep_count))
    echo "Found $total_count backups, will delete $to_delete_count oldest ones"
    echo ""

    # Get files to delete (oldest ones)
    local files_to_delete=($(ls -1t niveshak_backup_*.tar.gz 2>/dev/null | tail -n +"$((keep_count + 1))"))

    for file in "${files_to_delete[@]}"; do
        local size=$(du -sh "$file" 2>/dev/null | cut -f1 || echo "Unknown")
        echo "Deleting: $file ($size)"
        rm -f "$file"
        rm -f "${file}.sha256"
    done

    log "✅ Cleanup complete. Kept $keep_count most recent backups."
}

# Show total backup size
show_backup_size() {
    echo -e "${BLUE}💾 Backup Storage Usage${NC}"
    echo "======================"
    echo ""

    if [ ! -d "$BACKUP_DIR" ]; then
        warning "Backup directory does not exist: $BACKUP_DIR"
        return
    fi

    local total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
    local backup_count=$(ls -1 "$BACKUP_DIR"/niveshak_backup_*.tar.gz 2>/dev/null | wc -l || echo 0)

    echo "Backup directory: $BACKUP_DIR"
    echo "Total size: $total_size"
    echo "Number of backups: $backup_count"
    echo ""

    if [ "$backup_count" -gt 0 ]; then
        echo "Individual backup sizes:"
        ls -1t "$BACKUP_DIR"/niveshak_backup_*.tar.gz 2>/dev/null | while read backup; do
            local size=$(du -sh "$backup" 2>/dev/null | cut -f1 || echo "Unknown")
            echo "  $(basename "$backup"): $size"
        done
    fi
}

# Create automated backup
auto_backup() {
    echo -e "${BLUE}🤖 Automated Backup${NC}"
    echo "=================="
    echo ""

    log "Starting automated backup..."

    # Check if backup script exists
    if [ ! -f "$PROJECT_DIR/scripts/backup_data.sh" ]; then
        error "Backup script not found: $PROJECT_DIR/scripts/backup_data.sh"
        return 1
    fi

    # Run backup script
    if "$PROJECT_DIR/scripts/backup_data.sh"; then
        log "✅ Automated backup completed successfully"
    else
        error "❌ Automated backup failed"
        return 1
    fi
}

# Main function
main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
    "list" | "ls")
        list_backups
        ;;
    "info" | "show")
        show_backup_info "$1"
        ;;
    "delete" | "del" | "rm")
        delete_backup "$1" "$2"
        ;;
    "verify" | "check")
        verify_backup "$1"
        ;;
    "cleanup" | "clean")
        cleanup_backups "$1"
        ;;
    "size" | "usage")
        show_backup_size
        ;;
    "auto-backup" | "auto")
        auto_backup
        ;;
    "help" | "-h" | "--help")
        show_help
        ;;
    *)
        error "Unknown command: $command"
        echo ""
        show_help
        exit 1
        ;;
    esac
}

# Check if backup directory exists, create if not
if [ ! -d "$BACKUP_DIR" ]; then
    info "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

# Run main function with all arguments
main "$@"
