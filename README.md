# 🚀 Lang-Stack: Energy AI Optimizer Multi-Agent System

A comprehensive AI-powered energy optimization platform combining Langflow multi-agent workflows, Streamlit web interface, and Langfuse observability for intelligent building energy management.

## 📋 Overview

This project implements an **Energy AI Optimizer (EAIO)** system that uses multi-agent AI workflows to analyze, optimize, and manage building energy consumption. The system provides real-time insights, predictive analytics, and automated optimization recommendations for energy efficiency.

### 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    Langflow     │    │    Langfuse     │
│  Web Interface  │◄──►│  Multi-Agent    │◄──►│  Observability  │
│                 │    │     System      │    │   & Analytics   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │  Energy Database│
                    │                 │
                    └─────────────────┘
```

## 🎯 Key Features

### 🤖 Multi-Agent AI System
- **Intelligent Energy Analysis**: AI agents analyze building energy consumption patterns
- **Predictive Optimization**: Machine learning models predict energy usage and suggest optimizations
- **Automated Reporting**: Generated insights and recommendations
- **Vietnamese Language Support**: Native Vietnamese language processing

### 🌐 Web Interface
- **Interactive Chat Interface**: Real-time conversation with AI energy advisors
- **Data Visualization**: Energy consumption charts and analytics
- **Multi-language Support**: Vietnamese and English interfaces
- **Responsive Design**: Works on desktop and mobile devices

### 📊 Observability & Monitoring
- **Real-time Monitoring**: Track AI agent performance and decisions
- **Usage Analytics**: Monitor system usage and optimization impact
- **Error Tracking**: Comprehensive logging and debugging capabilities

### 🐳 Docker Deployment
- **Containerized Architecture**: Easy deployment with Docker Compose
- **Scalable Infrastructure**: Microservices-ready architecture
- **Environment Configuration**: Flexible configuration management

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- 8GB+ RAM recommended

### 1. Clone Repository
```bash
git clone https://github.com/fistdat/lang-stack.git
cd lang-stack
```

### 2. Start Langflow (AI Engine)
```bash
cd langflow
docker-compose up -d
```
Access Langflow at: http://localhost:7860

### 3. Start Streamlit Web Interface
```bash
cd streamlit_app
cp .env.example .env
# Edit .env with your configuration
docker-compose up -d
```
Access Web Interface at: http://localhost:8501

### 4. Start Langfuse (Optional - for observability)
```bash
cd langfuse
docker-compose up -d
```
Access Langfuse at: http://localhost:3000

## 📁 Project Structure

```
lang-stack/
├── 🌐 streamlit_app/           # Web Interface
│   ├── app.py                  # Main Streamlit application
│   ├── Dockerfile              # Container configuration
│   ├── docker-compose.yml      # Service orchestration
│   └── requirements.txt        # Python dependencies
│
├── 🤖 langflow/                # AI Multi-Agent System
│   ├── docker-compose.yml      # Langflow deployment
│   ├── flow/                   # AI agent workflows
│   └── src/                    # Langflow source code
│
├── 📊 langfuse/                # Observability Platform
│   ├── docker-compose.yml      # Langfuse deployment
│   └── web/                    # Langfuse web interface
│
├── ⚡ Energy-AI-Optimizer/     # Energy Optimization Documentation
│   ├── EAIO_Agent_System_Prompts.md
│   ├── stakeholder_agentic_workflows.md
│   └── BDG2-DB/               # Database documentation
│
├── 📚 thesis/                  # Research Documentation
│   ├── eaio-thesis_V3.0.md
│   ├── eaio-thesis_V3.1.md
│   └── eaio-thesis_V3.2.md
│
└── 📋 README.md               # This file
```

## 🔧 Configuration

### Environment Variables

**Streamlit App (.env)**
```bash
# Langflow API Configuration
LANGFLOW_API_KEY=your_api_key_here
LANGFLOW_API_URL=http://host.docker.internal:7860/api/v1/run/your-flow-id

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
```

**Langflow (docker-compose.yml)**
```yaml
environment:
  - LANGFLOW_DATABASE_URL=postgresql://user:password@postgres:5432/langflow
  - LANGFLOW_SECRET_KEY=your-secret-key
```

**Langfuse (docker-compose.yml)**
```yaml
environment:
  - DATABASE_URL=postgresql://user:password@postgres:5432/langfuse
  - NEXTAUTH_SECRET=your-nextauth-secret
```

## 🎨 Usage Examples

### 1. Energy Consumption Analysis
```python
# Ask the AI system in Vietnamese
"Phân tích mức tiêu thụ điện của 5 tòa nhà cao nhất"

# Expected response with formatted table:
# | Tòa Nhà | Tổng Tiêu Thụ (kWh) |
# |---------|---------------------|
# | Building A | 59,870,067.4 |
# | Building B | 42,638,202.18 |
```

### 2. Optimization Recommendations
```python
# Query for optimization suggestions
"Đề xuất biện pháp tiết kiệm năng lượng cho tòa nhà văn phòng"

# Get AI-powered recommendations with specific actions
```

### 3. Real-time Monitoring
Access the Langfuse dashboard to monitor:
- AI agent decision processes
- Energy optimization results
- System performance metrics

## 🧪 Testing

### Run Integration Tests
```bash
cd streamlit_app
python3 test_integration.py
```

### Test Langflow Connection
```bash
cd streamlit_app
./test_langflow_connection.sh
```

### Test Response Parsing
```bash
cd streamlit_app
python3 test_response_parsing.py
```

## 🏢 Use Cases

### 🏭 Smart Building Management
- **Real-time Energy Monitoring**: Track consumption across multiple buildings
- **Predictive Maintenance**: AI-powered equipment optimization recommendations
- **Cost Optimization**: Identify energy-saving opportunities

### 🌱 Sustainability Reporting
- **Carbon Footprint Analysis**: Calculate and track environmental impact
- **Compliance Monitoring**: Ensure adherence to energy regulations
- **Green Building Certification**: Support for LEED and similar standards

### 📈 Energy Analytics
- **Consumption Patterns**: Identify peak usage times and optimization opportunities
- **Benchmarking**: Compare performance across buildings and industry standards
- **ROI Analysis**: Calculate return on investment for energy efficiency measures

## 🔒 Security Features

- **API Key Management**: Secure handling of external service credentials
- **Database Security**: Encrypted connections and access control
- **Container Security**: Isolated microservices architecture
- **Secrets Management**: Environment-based configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/fistdat/lang-stack.git
cd lang-stack

# Start development services
docker-compose -f docker-compose.dev.yml up -d
```

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 20GB available space
- **Network**: Internet connection for AI model access

### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 50GB+ SSD
- **Network**: High-speed internet connection

## 🐛 Troubleshooting

### Common Issues

#### Streamlit Can't Connect to Langflow
```bash
# Check if Langflow is running
curl http://localhost:7860/health

# Verify network configuration in docker-compose.yml
# Ensure using host.docker.internal for container-to-host communication
```

#### Database Connection Issues
```bash
# Check PostgreSQL container status
docker ps | grep postgres

# Review database logs
docker logs langflow_postgres_1
```

#### API Response Formatting Issues
- Ensure response parsing logic handles nested JSON structure
- Check Langflow flow configuration for proper output format

## 📚 Documentation

- **[Thesis Documentation](./thesis/)**: Research background and methodology
- **[Energy AI Optimizer Guide](./Energy-AI-Optimizer/)**: Detailed system documentation
- **[Streamlit App Guide](./streamlit_app/README.md)**: Web interface documentation
- **[API Documentation](./langflow/README.md)**: Langflow API reference

## 🏷️ Releases

### v2.0 (Latest)
- ✅ Complete Streamlit-Langflow integration
- ✅ Docker containerization with proper networking
- ✅ Clean response parsing for chat interface
- ✅ Vietnamese language support
- ✅ Comprehensive testing suite
- ✅ Security improvements (API key management)

### v1.0
- ✅ Basic Langflow and Langfuse integration
- ✅ Initial energy optimization workflows

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/fistdat/lang-stack/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fistdat/lang-stack/discussions)
- **Email**: hoangdat@example.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Langflow Team**: For the excellent multi-agent workflow platform
- **Streamlit Team**: For the intuitive web framework
- **Langfuse Team**: For comprehensive observability tools
- **OpenAI**: For GPT model integration
- **Research Community**: For energy optimization methodologies

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=fistdat/lang-stack&type=Date)](https://star-history.com/#fistdat/lang-stack&Date)

---

**Built with ❤️ for sustainable energy management**

*Empowering intelligent buildings through AI-driven energy optimization*