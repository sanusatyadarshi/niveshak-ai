#!/bin/bash

# Script to run local vector databases for NiveshakAI
# Supports Qdrant and Weaviate using Docker containers

set -e

# Configuration
QDRANT_PORT=6333
WEAVIATE_PORT=8080
NETWORK_NAME="niveshak_network"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &>/dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! docker info &>/dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi

    print_success "Docker is available and running"
}

# Create Docker network
create_network() {
    print_status "Creating Docker network..."

    if docker network ls | grep -q "${NETWORK_NAME}"; then
        print_warning "Network ${NETWORK_NAME} already exists"
    else
        docker network create "${NETWORK_NAME}"
        print_success "Created Docker network: ${NETWORK_NAME}"
    fi
}

# Start Qdrant vector database
start_qdrant() {
    print_status "Starting Qdrant vector database..."

    # Check if Qdrant container is already running
    if docker ps | grep -q "qdrant-niveshak"; then
        print_warning "Qdrant container is already running"
        return
    fi

    # Stop existing container if it exists but is not running
    if docker ps -a | grep -q "qdrant-niveshak"; then
        print_status "Removing existing Qdrant container..."
        docker rm -f qdrant-niveshak
    fi

    # Create data directory for persistence
    mkdir -p "$(pwd)/data/qdrant_storage"

    # Start Qdrant container
    docker run -d \
        --name qdrant-niveshak \
        --network "${NETWORK_NAME}" \
        -p ${QDRANT_PORT}:6333 \
        -v "$(pwd)/data/qdrant_storage:/qdrant/storage" \
        qdrant/qdrant:latest

    print_success "Qdrant started on port ${QDRANT_PORT}"
    print_status "Qdrant UI available at: http://localhost:${QDRANT_PORT}/dashboard"
}

# Start Weaviate vector database
start_weaviate() {
    print_status "Starting Weaviate vector database..."

    # Check if Weaviate container is already running
    if docker ps | grep -q "weaviate-niveshak"; then
        print_warning "Weaviate container is already running"
        return
    fi

    # Stop existing container if it exists but is not running
    if docker ps -a | grep -q "weaviate-niveshak"; then
        print_status "Removing existing Weaviate container..."
        docker rm -f weaviate-niveshak
    fi

    # Create data directory for persistence
    mkdir -p "$(pwd)/data/weaviate_data"

    # Start Weaviate container
    docker run -d \
        --name weaviate-niveshak \
        --network "${NETWORK_NAME}" \
        -p ${WEAVIATE_PORT}:8080 \
        -e QUERY_DEFAULTS_LIMIT=25 \
        -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
        -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
        -e DEFAULT_VECTORIZER_MODULE='none' \
        -e ENABLE_MODULES='text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai' \
        -e CLUSTER_HOSTNAME='node1' \
        -v "$(pwd)/data/weaviate_data:/var/lib/weaviate" \
        semitechnologies/weaviate:latest

    print_success "Weaviate started on port ${WEAVIATE_PORT}"
    print_status "Weaviate API available at: http://localhost:${WEAVIATE_PORT}"
}

# Start both databases
start_all() {
    print_status "Starting all vector databases..."
    create_network
    start_qdrant
    start_weaviate

    echo ""
    print_success "All vector databases are running!"
    echo ""
    echo "📊 Database Status:"
    echo "  Qdrant:   http://localhost:${QDRANT_PORT}/dashboard"
    echo "  Weaviate: http://localhost:${WEAVIATE_PORT}"
    echo ""
    echo "🔧 To stop all databases:"
    echo "  $0 stop"
    echo ""
    echo "💡 To check status:"
    echo "  $0 status"
}

# Stop all databases
stop_all() {
    print_status "Stopping vector databases..."

    # Stop Qdrant
    if docker ps | grep -q "qdrant-niveshak"; then
        docker stop qdrant-niveshak
        docker rm qdrant-niveshak
        print_success "Qdrant stopped"
    else
        print_warning "Qdrant container is not running"
    fi

    # Stop Weaviate
    if docker ps | grep -q "weaviate-niveshak"; then
        docker stop weaviate-niveshak
        docker rm weaviate-niveshak
        print_success "Weaviate stopped"
    else
        print_warning "Weaviate container is not running"
    fi

    # Remove network
    if docker network ls | grep -q "${NETWORK_NAME}"; then
        docker network rm "${NETWORK_NAME}" 2>/dev/null || true
        print_success "Docker network removed"
    fi

    print_success "All vector databases stopped"
}

# Check status of databases
check_status() {
    echo "🔍 Vector Database Status:"
    echo "=========================="
    echo ""

    # Check Qdrant
    if docker ps | grep -q "qdrant-niveshak"; then
        print_success "Qdrant: Running on port ${QDRANT_PORT}"

        # Test connection
        if curl -s "http://localhost:${QDRANT_PORT}/health" >/dev/null; then
            print_success "  ✓ Qdrant API is responding"
        else
            print_warning "  ⚠ Qdrant API is not responding"
        fi
    else
        print_error "Qdrant: Not running"
    fi

    echo ""

    # Check Weaviate
    if docker ps | grep -q "weaviate-niveshak"; then
        print_success "Weaviate: Running on port ${WEAVIATE_PORT}"

        # Test connection
        if curl -s "http://localhost:${WEAVIATE_PORT}/v1/meta" >/dev/null; then
            print_success "  ✓ Weaviate API is responding"
        else
            print_warning "  ⚠ Weaviate API is not responding"
        fi
    else
        print_error "Weaviate: Not running"
    fi

    echo ""

    # Show container details
    echo "🐳 Container Details:"
    echo "===================="
    docker ps --filter "name=qdrant-niveshak" --filter "name=weaviate-niveshak" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Restart all databases
restart_all() {
    print_status "Restarting vector databases..."
    stop_all
    sleep 2
    start_all
}

# Show logs for databases
show_logs() {
    local service=${1:-"all"}

    case $service in
    "qdrant")
        print_status "Showing Qdrant logs..."
        docker logs -f qdrant-niveshak
        ;;
    "weaviate")
        print_status "Showing Weaviate logs..."
        docker logs -f weaviate-niveshak
        ;;
    "all" | *)
        print_status "Showing logs for all databases (press Ctrl+C to exit)..."
        echo "Select a database to view logs:"
        echo "1) Qdrant"
        echo "2) Weaviate"
        read -p "Enter choice (1-2): " choice

        case $choice in
        1) show_logs "qdrant" ;;
        2) show_logs "weaviate" ;;
        *) print_error "Invalid choice" ;;
        esac
        ;;
    esac
}

# Setup function - create docker-compose file for easier management
setup_compose() {
    print_status "Creating docker-compose.yml for vector databases..."

    cat >docker-compose.vector-db.yml <<EOF
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant-niveshak
    ports:
      - "${QDRANT_PORT}:6333"
    volumes:
      - ./data/qdrant_storage:/qdrant/storage
    networks:
      - niveshak_network
    restart: unless-stopped

  weaviate:
    image: semitechnologies/weaviate:latest
    container_name: weaviate-niveshak
    ports:
      - "${WEAVIATE_PORT}:8080"
    environment:
      - QUERY_DEFAULTS_LIMIT=25
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
      - DEFAULT_VECTORIZER_MODULE=none
      - ENABLE_MODULES=text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai
      - CLUSTER_HOSTNAME=node1
    volumes:
      - ./data/weaviate_data:/var/lib/weaviate
    networks:
      - niveshak_network
    restart: unless-stopped

networks:
  niveshak_network:
    driver: bridge
EOF

    print_success "docker-compose.vector-db.yml created"
    print_status "You can now use: docker-compose -f docker-compose.vector-db.yml up -d"
}

# Main function
main() {
    case "${1:-start}" in
    "start")
        check_docker
        start_all
        ;;
    "stop")
        stop_all
        ;;
    "restart")
        check_docker
        restart_all
        ;;
    "status")
        check_status
        ;;
    "logs")
        show_logs "${2}"
        ;;
    "qdrant")
        check_docker
        create_network
        start_qdrant
        ;;
    "weaviate")
        check_docker
        create_network
        start_weaviate
        ;;
    "setup-compose")
        setup_compose
        ;;
    "help" | "-h" | "--help")
        echo "🤖 NiveshakAI Vector Database Manager"
        echo "====================================="
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  start          Start all vector databases (default)"
        echo "  stop           Stop all vector databases"
        echo "  restart        Restart all vector databases"
        echo "  status         Check status of all databases"
        echo "  logs [db]      Show logs (qdrant, weaviate, or all)"
        echo "  qdrant         Start only Qdrant"
        echo "  weaviate       Start only Weaviate"
        echo "  setup-compose  Create docker-compose file"
        echo "  help           Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start       # Start all databases"
        echo "  $0 qdrant      # Start only Qdrant"
        echo "  $0 logs qdrant # Show Qdrant logs"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
    esac
}

# Run main function with all arguments
main "$@"
