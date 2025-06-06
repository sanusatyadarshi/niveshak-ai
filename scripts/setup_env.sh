#!/bin/bash

# Setup script for NiveshakAI environment
# This script sets up the development environment including:
# - Python virtual environment
# - Dependencies installation
# - Directory structure creation
# - Configuration file setup
# - Vector database initialization

set -e # Exit on any error

echo "🚀 Setting up NiveshakAI development environment..."

# Configuration
PYTHON_VERSION="3.9"
VENV_NAME="niveshak_env"
PROJECT_ROOT="$(pwd)"

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

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."

    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
        PYTHON_ACTUAL_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        print_success "Python ${PYTHON_ACTUAL_VERSION} found"

        # Check if version is compatible
        if [[ $(echo "${PYTHON_ACTUAL_VERSION} >= 3.8" | bc -l) -eq 1 ]]; then
            print_success "Python version is compatible"
        else
            print_error "Python 3.8 or higher is required. Found: ${PYTHON_ACTUAL_VERSION}"
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."

    if command -v pip3 &>/dev/null; then
        PIP_CMD="pip3"
        print_success "pip3 found"
    elif command -v pip &>/dev/null; then
        PIP_CMD="pip"
        print_success "pip found"
    else
        print_error "pip is not installed. Please install pip."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."

    if [ -d "${VENV_NAME}" ]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf "${VENV_NAME}"
    fi

    ${PYTHON_CMD} -m venv "${VENV_NAME}"
    print_success "Virtual environment created: ${VENV_NAME}"
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source "${VENV_NAME}/bin/activate"
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."

    # Upgrade pip first
    pip install --upgrade pip

    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed from requirements.txt"
    else
        print_warning "requirements.txt not found. Installing basic dependencies..."
        pip install openai langchain qdrant-client weaviate-client PyPDF2 pdfplumber click pyyaml requests pandas numpy pytest
        print_success "Basic dependencies installed"
    fi
}

# Create directory structure
create_directories() {
    print_status "Creating directory structure..."

    # Data directories
    mkdir -p data/books
    mkdir -p data/reports
    mkdir -p data/embeddings

    # Log directory
    mkdir -p logs

    # Cache directory
    mkdir -p cache

    # Output directory
    mkdir -p output

    print_success "Directory structure created"
}

# Setup configuration files
setup_config() {
    print_status "Setting up configuration files..."

    # Create config directory if it doesn't exist
    mkdir -p config

    # Create default settings if not exists
    if [ ! -f "config/settings.yaml" ]; then
        print_warning "config/settings.yaml not found. Please create it manually or copy from config/settings.yaml.example"
    else
        print_success "Configuration files found"
    fi

    # Create environment file template
    if [ ! -f ".env" ]; then
        cat >.env <<EOF
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Vector Database Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=

# Weaviate Configuration
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=

# Financial Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FMP_API_KEY=your_fmp_key_here

# Logging Configuration
LOG_LEVEL=INFO
EOF
        print_success "Environment file template created: .env"
        print_warning "Please update .env with your actual API keys"
    else
        print_success "Environment file already exists"
    fi
}

# Check for Docker (for vector databases)
check_docker() {
    print_status "Checking Docker installation..."

    if command -v docker &>/dev/null; then
        print_success "Docker found"

        # Check if Docker is running
        if docker info &>/dev/null; then
            print_success "Docker is running"
        else
            print_warning "Docker is installed but not running"
            print_status "To start Docker, run: sudo systemctl start docker (Linux) or start Docker Desktop (Mac/Windows)"
        fi
    else
        print_warning "Docker not found. Install Docker to run local vector databases"
        print_status "You can still use cloud-hosted vector databases"
    fi
}

# Setup development tools
setup_dev_tools() {
    print_status "Setting up development tools..."

    # Install development dependencies
    pip install pytest pytest-cov black flake8 mypy

    # Setup pre-commit hooks (if .pre-commit-config.yaml exists)
    if [ -f ".pre-commit-config.yaml" ]; then
        pip install pre-commit
        pre-commit install
        print_success "Pre-commit hooks installed"
    fi

    print_success "Development tools installed"
}

# Create startup script
create_startup_script() {
    print_status "Creating startup script..."

    cat >start_niveshak.sh <<'EOF'
#!/bin/bash

# NiveshakAI startup script
echo "🤖 Starting NiveshakAI..."

# Activate virtual environment
source niveshak_env/bin/activate

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Check if vector database is running
echo "Checking vector database connection..."

# Start the application
echo "NiveshakAI environment is ready!"
echo ""
echo "📚 Available commands:"
echo "  python -m src.cli.ingest_books --help"
echo "  python -m src.cli.ingest_reports --help" 
echo "  python -m src.cli.analyze --help"
echo ""
echo "🔍 To run tests:"
echo "  pytest tests/"
echo ""
echo "📖 To start a Python shell with the environment:"
echo "  python"
EOF

    chmod +x start_niveshak.sh
    print_success "Startup script created: start_niveshak.sh"
}

# Main setup function
main() {
    echo "🤖 NiveshakAI Environment Setup"
    echo "================================"
    echo ""

    # Check prerequisites
    check_python
    check_pip
    check_docker

    # Setup environment
    create_venv
    activate_venv
    install_dependencies

    # Setup project structure
    create_directories
    setup_config
    setup_dev_tools
    create_startup_script

    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Update .env file with your API keys"
    echo "2. Review and customize config/settings.yaml"
    echo "3. Start vector database: ./scripts/run_local_vector_db.sh"
    echo "4. Run the startup script: ./start_niveshak.sh"
    echo ""
    echo "To activate the environment manually:"
    echo "  source ${VENV_NAME}/bin/activate"
    echo ""
    echo "Happy investing! 📈"
}

# Run main function
main "$@"
