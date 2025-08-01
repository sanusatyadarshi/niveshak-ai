#!/bin/bash

# NiveshakAI Docker Startup Script

echo "🐳 Starting NiveshakAI with Docker..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating a template..."
    cat >.env <<EOF
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Ollama Configuration (for fallback)
OLLAMA_BASE_URL=http://localhost:11434

# Vector Database Configuration
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=

# Application Configuration
FLASK_ENV=production
PYTHONPATH=/app
EOF
    echo "📝 Please edit .env file with your OpenAI API key before continuing"
    echo "   Example: sed -i 's/your_openai_api_key_here/sk-your-actual-key/' .env"
    exit 1
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  Please set your OpenAI API key in .env file"
    echo "   Edit: OPENAI_API_KEY=sk-your-actual-key"
    exit 1
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/annual_reports data/books data/uploads reports logs data/embeddings data/qdrant_storage

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start containers
echo "🏗️  Building Docker image..."
docker-compose build

echo "🚀 Starting NiveshakAI services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Display access information
echo ""
echo "✅ NiveshakAI is now running!"
echo ""
echo "🌐 Web Interface: http://localhost:5000"
echo "   🏠 Home: http://localhost:5000"
echo "   🔍 Analysis: http://localhost:5000/analyze"
echo "   📁 Upload: http://localhost:5000/upload"
echo "   📊 Reports: http://localhost:5000/reports"
echo ""
echo "🗄️  Vector Database (Qdrant): http://localhost:6333"
echo ""
echo "📋 Useful Commands:"
echo "   docker-compose logs -f niveshak-ai    # View application logs"
echo "   docker-compose logs -f qdrant         # View Qdrant logs"
echo "   docker-compose down                   # Stop all services"
echo "   docker-compose restart                # Restart services"
echo ""
echo "🔄 To update the application:"
echo "   git pull && docker-compose build && docker-compose up -d"
