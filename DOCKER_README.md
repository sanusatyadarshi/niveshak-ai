# NiveshakAI Docker Setup

This guide shows how to run NiveshakAI using Docker, which eliminates all dependency and environment issues.

## 🐳 Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- OpenAI API key

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd niveshak-ai
```

### 2. Configure Environment

```bash
# Create .env file with your OpenAI API key
echo 'OPENAI_API_KEY=sk-your-actual-openai-key-here' > .env
```

### 3. Start with Docker

```bash
# Option 1: Use the startup script (recommended)
./docker-start.sh

# Option 2: Manual Docker Compose
docker-compose up -d
```

### 4. Access the Application

- **Web Interface**: http://localhost:5000
- **Vector Database**: http://localhost:6333 (Qdrant dashboard)

## 📊 Services

The Docker setup includes:

1. **NiveshakAI Web App** (Port 5000)

   - Complete web interface
   - All CLI functionality via API
   - File upload handling
   - Report generation

2. **Qdrant Vector Database** (Port 6333)
   - Vector storage for AI embeddings
   - Knowledge base for investment books
   - Persistent storage

## 🔧 Docker Commands

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f niveshak-ai
docker-compose logs -f qdrant

# Check status
docker-compose ps
```

### Development

```bash
# Build image
docker-compose build

# Build without cache
docker-compose build --no-cache

# Update application
git pull && docker-compose build && docker-compose up -d
```

### Data Management

```bash
# Backup data
tar -czf niveshak-backup.tar.gz data/ reports/

# Restore data
tar -xzf niveshak-backup.tar.gz

# Reset vector database
docker-compose down
rm -rf data/qdrant_storage
docker-compose up -d
```

## 📁 Volume Mappings

Docker automatically maps these directories:

```
Host Directory          → Container Directory
./data/                → /app/data/
./reports/             → /app/reports/
./logs/                → /app/logs/
./.env                 → /app/.env
```

This means:

- Your data persists even if containers are recreated
- You can access reports and logs from your host system
- Configuration changes in `.env` are immediately available

## 🛠️ Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs niveshak-ai

# Common issues:
# 1. Missing .env file
# 2. Invalid OpenAI API key
# 3. Port 5000 already in use
```

### Fix Port Conflicts

If port 5000 is in use, edit `docker-compose.yml`:

```yaml
services:
  niveshak-ai:
    ports:
      - "8080:5000" # Use port 8080 instead
```

### Reset Everything

```bash
# Stop and remove all containers and volumes
docker-compose down -v
docker system prune -f

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

## 🔐 Security Notes

- The `.env` file is mounted read-only into the container
- API keys are never built into the Docker image
- All data is stored in mapped volumes, not in containers
- Qdrant runs in the internal Docker network

## 📈 Production Deployment

For production use:

1. **Use Docker Swarm or Kubernetes**
2. **Add HTTPS/SSL termination**
3. **Use external database for persistence**
4. **Implement proper logging and monitoring**
5. **Set up backup strategies**

### Example Production docker-compose.yml

```yaml
version: "3.8"
services:
  niveshak-ai:
    image: niveshak-ai:latest
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
    environment:
      - FLASK_ENV=production
    # ... other production settings
```

## 💡 Benefits of Docker Setup

1. **No Dependency Issues**: All dependencies are containerized
2. **Consistent Environment**: Same environment across all systems
3. **Easy Deployment**: Single command to start everything
4. **Isolation**: No conflicts with host system
5. **Scalability**: Easy to scale with Docker Swarm/Kubernetes
6. **Backup/Restore**: Simple data management
7. **Version Control**: Easy to roll back to previous versions

---

This Docker setup provides a production-ready environment for NiveshakAI with minimal configuration required.
