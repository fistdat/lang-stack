# 🌍 GIS Energy Optimizer - Docker Deployment

Advanced geospatial intelligence platform for sustainable energy management with AI-powered chatbot integration.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Usage](#usage)
- [API Integration](#api-integration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## 🎯 Overview

This Docker deployment provides a complete GIS energy optimization platform with:

- **Interactive Mapping**: Leafmap-powered geospatial visualization
- **AI Assistant**: Langflow integration for intelligent energy analysis  
- **Real-time Analytics**: Energy consumption and efficiency monitoring
- **Scalable Architecture**: Docker Compose with Redis caching and Nginx proxy

## ✨ Features

### 🗺️ Geospatial Intelligence
- Interactive maps with Vietnam energy infrastructure
- Heat maps for consumption analysis
- Spatial clustering and optimization
- Site selection for renewable energy

### 🤖 AI-Powered Insights
- Natural language query processing
- Intelligent recommendations
- Predictive energy modeling
- Automated report generation

### 📊 Advanced Analytics
- Real-time energy consumption tracking
- Efficiency analysis across regions
- Performance benchmarking
- Trend visualization

### 🔧 Enterprise Features
- Load balancing with Nginx
- Redis caching for performance
- Health monitoring
- Auto-scaling capabilities

## 🛠 Prerequisites

- **Docker**: Version 20.0+ 
- **Docker Compose**: Version 2.0+
- **System Requirements**: 
  - RAM: 4GB minimum, 8GB recommended
  - CPU: 2 cores minimum, 4 cores recommended
  - Storage: 10GB available space

### Installation Commands

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# macOS (using Homebrew)
brew install docker docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
cd streamlit-geospatial
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (optional)
nano .env
```

### 3. Deploy Application
```bash
# Make script executable
chmod +x deploy.sh

# Deploy with automatic setup
./deploy.sh deploy
```

### 4. Access Application
- **Main App**: http://localhost:8502
- **Nginx Proxy**: http://localhost:8080  
- **Redis Cache**: http://localhost:6381

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Langflow API Configuration
LANGFLOW_API_URL=http://host.docker.internal:7860/api/v1/run/3f229440-4079-4ee6-bcd3-341accdd9761
LANGFLOW_API_KEY=your_api_key_here

# Streamlit Configuration  
STREAMLIT_SERVER_PORT=8501
STREAMLIT_THEME_PRIMARY_COLOR=#28a745

# Performance Settings
MAX_WORKERS=4
TIMEOUT=60
MAX_MEMORY_MB=2048
```

### Docker Compose Services

| Service | Port | Description |
|---------|------|-------------|
| `streamlit-gis` | 8502 | Main Streamlit application |
| `nginx-proxy` | 8080 | Load balancer and reverse proxy |
| `redis-cache` | 6381 | Caching and session storage |

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Users/Browsers │    │  Nginx Proxy    │    │ Streamlit GIS   │
│                 │ => │  (Port 8080)    │ => │ (Port 8502)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲                       │
                                │                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis Cache   │    │  Langflow API   │
                       │  (Port 6381)    │    │  (External)     │
                       │                 │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## 📱 Usage

### Basic Operations

```bash
# View service status
./deploy.sh status

# View real-time logs
./deploy.sh logs

# Restart services
./deploy.sh restart

# Stop services
./deploy.sh stop

# Clean up resources
./deploy.sh clean
```

### Manual Docker Commands

```bash
# Build and start
docker-compose up -d --build

# Scale services
docker-compose up -d --scale streamlit-gis=3

# View logs
docker-compose logs -f streamlit-gis

# Execute commands in container
docker-compose exec streamlit-gis bash
```

## 🔌 API Integration

### Langflow Connection

The application automatically connects to your existing Langflow instance:

```python
# Environment configuration
LANGFLOW_API_URL=http://host.docker.internal:7860/api/v1/run/YOUR_FLOW_ID
LANGFLOW_API_KEY=your_api_key_here
```

### Sample API Usage

```python
import requests

def query_ai_assistant(question):
    response = requests.post(
        "http://localhost:8502/api/chat",
        json={"message": question}
    )
    return response.json()

# Example usage
result = query_ai_assistant("Find optimal solar locations in Vietnam")
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8502

# Change ports in docker-compose.yml
ports:
  - "8503:8501"  # Use different external port
```

#### 2. Memory Issues
```bash
# Increase Docker memory limits
docker-compose.yml:
  deploy:
    resources:
      limits:
        memory: 4G
```

#### 3. Langflow Connection Failed
```bash
# Check Langflow status
curl http://localhost:7860/health

# Update API URL in .env
LANGFLOW_API_URL=http://your-langflow-host:7860/api/v1/run/YOUR_FLOW_ID
```

#### 4. Build Failures
```bash
# Clean build
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
docker-compose --verbose up
```

### Health Checks

```bash
# Application health
curl http://localhost:8502/_stcore/health

# Nginx health  
curl http://localhost:8080/health

# Redis health
docker-compose exec redis-cache redis-cli ping
```

## 🔄 Development

### Local Development Setup

```bash
# Development with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black . && isort .
```

### Custom Configuration

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'
services:
  streamlit-gis:
    volumes:
      - .:/app  # Mount source code
    environment:
      - STREAMLIT_SERVER_RUN_ON_SAVE=true
```

### Performance Tuning

```bash
# Production optimizations
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

# Monitor resource usage
docker stats

# Optimize image size
docker-compose build --build-arg PYTHON_VERSION=3.11-slim
```

## 📊 Monitoring

### Application Metrics

```bash
# View container stats
docker stats streamlit-gis-app

# Memory usage
docker exec streamlit-gis-app cat /proc/meminfo

# CPU usage
docker exec streamlit-gis-app top -bn1 | grep streamlit
```

### Log Analysis

```bash
# Error logs only
docker-compose logs streamlit-gis | grep ERROR

# Performance logs
docker-compose logs nginx-proxy | grep "response_time"

# Application metrics
curl http://localhost:8502/_stcore/metrics
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is part of the Master Thesis at FPT University.

**Author**: Hoang Tuan Dat  
**Advisor**: Assoc. Prof. Phan Duy Hung  
**Institution**: FPT University - Master of Software Engineering  
**Year**: 2025

## 🆘 Support

For issues and questions:

- 📧 Email: datht@fpt.edu.vn
- 🐛 Issues: [GitHub Issues](https://github.com/hoangtuandat/energy-ai-optimizer/issues)
- 📖 Documentation: [Wiki](https://github.com/hoangtuandat/energy-ai-optimizer/wiki)

---

🌟 **Star this project if you find it useful!**