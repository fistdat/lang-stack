# 🚀 Lang-Stack: Energy AI Optimizer Multi-Agent System (v3.0)

A comprehensive AI-powered energy optimization platform combining Langflow multi-agent workflows, EAIO-DL deep learning backend, and Langfuse observability for intelligent building energy management with Jira/Confluence automation capabilities.

## 📋 Overview

This project implements an **Energy AI Optimizer (EAIO)** system that uses multi-agent AI workflows to analyze, optimize, and manage building energy consumption. The system provides real-time insights, predictive analytics, automated optimization recommendations, and complete project management automation for energy efficiency initiatives.

### 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Langflow     │    │    EAIO-DL      │    │    Langfuse     │
│  Multi-Agent    │◄──►│  Deep Learning  │◄──►│  Observability  │
│    Workflow     │    │    Backend      │    │   & Analytics   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────────────┐
                    │   PostgreSQL + TimesFM      │
                    │   Energy Database + ML      │
                    └─────────────────────────────┘
                                 │
                    ┌─────────────────────────────┐
                    │  Jira + Confluence          │
                    │  Project Automation         │
                    └─────────────────────────────┘
```

## 🎯 Key Features

### 🤖 Multi-Agent AI System (Langflow)
- **5 Specialized Agents**: Weather Intelligence, Forecast Intelligence, Optimization Strategy, System Control, and Validator agents
- **Intelligent Energy Analysis**: AI agents analyze building energy consumption patterns
- **Predictive Optimization**: Machine learning models predict energy usage and suggest optimizations
- **Automated Reporting**: Generated insights and recommendations
- **Vietnamese Language Support**: Native Vietnamese language processing

### 🧠 Deep Learning Backend (EAIO-DL)
- **TimesFM Integration**: Advanced time-series forecasting for energy prediction
- **React + TypeScript Frontend**: Modern chat interface with markdown rendering
- **FastAPI Backend**: High-performance API with PostgreSQL database
- **LLM Multi-Agent Optimization**: 60-70% cost reduction with ChatGPT 4o Mini integration
- **Conversational AI**: Natural language interface for energy management

### 🛠️ Project Automation
- **Jira Integration**: Automated epic, story, and task creation
- **Confluence Documentation**: Auto-generated project documentation pages
- **Sprint Management**: 8-sprint automated planning system
- **Traceability Matrix**: Complete requirement tracking

### 📊 Observability & Monitoring (Langfuse)
- **Real-time Monitoring**: Track AI agent performance and decisions
- **Usage Analytics**: Monitor system usage and optimization impact
- **Trace Collection**: Comprehensive execution tracking
- **Error Tracking**: Comprehensive logging and debugging capabilities

### 🐳 Docker Deployment
- **Containerized Architecture**: Easy deployment with Docker Compose
- **Scalable Infrastructure**: Microservices-ready architecture
- **Environment Configuration**: Flexible configuration management
- **Integrated Stack**: Langflow + Langfuse + EAIO-DL unified deployment

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git (with submodule support)
- Python 3.10+
- Node.js 18+ (for EAIO-DL frontend)
- 16GB+ RAM recommended

### 1. Clone Repository with Submodules
```bash
git clone --recursive https://github.com/fistdat/lang-stack.git
cd lang-stack

# If already cloned, initialize submodules
git submodule update --init --recursive
```

### 2. Start Integrated Stack (Langflow + Langfuse)
```bash
# Copy and configure environment
cp .env.integrated .env
# Edit .env with your secure passwords and API keys

# Start all services
docker-compose -f docker-compose.integrated.yml up -d
```

**Access Points:**
- **Langflow UI**: http://localhost:7860
- **Langfuse Observability**: http://localhost:3000
- **MinIO Console**: http://localhost:9091

### 3. Start EAIO-DL Deep Learning Backend
```bash
cd EAIO-DL

# Backend
cd backend
cp .env.example .env
docker-compose up -d

# Frontend
cd ../frontend
npm install
npm start
```

**Access Points:**
- **EAIO-DL Backend API**: http://localhost:8000
- **EAIO-DL Frontend**: http://localhost:3001

### 4. Run Project Automation (Optional)
```bash
cd automation
pip install -r requirements.txt

# Configure Jira/Confluence credentials
cp .env.example .env

# Run automation
python run_automation.py
```

## 📁 Project Structure

```
lang-stack/
├── 🤖 langflow/                      # AI Multi-Agent Workflow System
│   ├── docker-compose.yml            # Langflow deployment config
│   ├── docker_example/               # Integration examples
│   └── flows/                        # Agent workflow definitions
│
├── 📊 langfuse/                      # Observability Platform
│   ├── docker-compose.yml            # Langfuse deployment
│   └── web/                          # Observability dashboard
│
├── 🧠 EAIO-DL/                      # Deep Learning Backend (Submodule)
│   ├── backend/                      # FastAPI + PostgreSQL
│   │   ├── api/                      # REST API routes
│   │   ├── db/                       # Database models & migrations
│   │   ├── services/                 # Business logic
│   │   └── docker-compose.yml        # Backend deployment
│   ├── frontend/                     # React + TypeScript
│   │   ├── src/components/           # UI components
│   │   └── src/services/             # API clients
│   └── docs/                         # Technical documentation
│
├── 🛠️ automation/                   # Project Management Automation
│   ├── eaio_jira_confluence_automation.py  # Main automation script
│   ├── create_confluence_documentation.py  # Doc generation
│   ├── sprints/                      # Sprint planning files
│   ├── requirements.txt              # Python dependencies
│   └── README.md                     # Automation guide
│
├── 👥 agents/                        # Agent System Documentation
│   ├── EAIO_SYSTEM_OVERVIEW.md       # System architecture
│   ├── Energy_Agent_Instructions_UNIVERSAL.md
│   ├── Weather_Intelligence_Agent_Instructions.md
│   ├── Forecast_Intelligence_Agent_Instructions.md
│   ├── Optimization_Strategy_Agent_Instructions.md
│   ├── System_Control_Agent_Instructions.md
│   ├── Validator_Agent_Instructions.md
│   └── DEPLOYMENT_CHECKLIST.md       # Production deployment guide
│
├── 📚 docs-superclaude/              # SuperClaude Framework Documentation
│   └── SuperClaude-Huong-Dan-Su-Dung.md
│
├── 📄 .env.integrated                # Environment configuration template
├── 🐳 docker-compose.integrated.yml  # Integrated stack deployment
├── 📋 README.md                      # This file
└── 📋 README-Integrated.md           # Langflow+Langfuse integration guide
```

**Submodule:**
- `EAIO-DL`: Separate repository at https://github.com/fistdat/EAIO.git

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

### Main Documentation
- **[Integrated Stack Guide](./README-Integrated.md)**: Complete Langflow + Langfuse integration guide
- **[Agent System Overview](./agents/EAIO_SYSTEM_OVERVIEW.md)**: Multi-agent architecture
- **[Deployment Checklist](./agents/DEPLOYMENT_CHECKLIST.md)**: Production deployment guide

### Agent Instructions
- **[Energy Agent Universal](./agents/Energy_Agent_Instructions_UNIVERSAL.md)**: Core agent behavior
- **[Weather Intelligence](./agents/Weather_Intelligence_Agent_Instructions.md)**: Weather analysis agent
- **[Forecast Intelligence](./agents/Forecast_Intelligence_Agent_Instructions.md)**: Prediction agent
- **[Optimization Strategy](./agents/Optimization_Strategy_Agent_Instructions.md)**: Strategy agent
- **[System Control](./agents/System_Control_Agent_Instructions.md)**: Control agent
- **[Validator](./agents/Validator_Agent_Instructions.md)**: Validation agent

### Automation Documentation
- **[Automation Guide](./automation/README.md)**: Jira/Confluence automation
- **[Multi-Project Setup](./automation/MULTI_PROJECT_SETUP.md)**: Multiple project management

### EAIO-DL Documentation
- **[EAIO Repository](https://github.com/fistdat/EAIO)**: Deep learning backend documentation
- **[System Architecture](./EAIO-DL/Energy%20AI%20Optimizer%20System%20Architecture.md)**: Technical architecture
- **[Phase 1 Summary](./EAIO-DL/PHASE1_COMPLETE_SUMMARY.md)**: Implementation details

### SuperClaude Framework
- **[Usage Guide](./docs-superclaude/SuperClaude-Huong-Dan-Su-Dung.md)**: Vietnamese guide for SuperClaude

## 🏷️ Releases

### v3.0 (Latest - December 2025)
- ✅ Major project restructuring and cleanup
- ✅ EAIO-DL as git submodule with TimesFM integration
- ✅ Complete Jira/Confluence automation system
- ✅ 5 specialized AI agents with comprehensive documentation
- ✅ Integrated Langflow + Langfuse observability stack
- ✅ Multi-project management automation support
- ✅ 8-sprint automated planning system
- ✅ Traceability matrix and requirements tracking
- ✅ SuperClaude framework integration

### v2.3
- ✅ Enhanced EAIO with LLM-as-a-Judge evaluation framework
- ✅ Comprehensive system enhancements

### v2.2
- ✅ Complete lang-stack project with EAIO
- ✅ Streamlit interface with academic thesis styling

### v2.0-2.1
- ✅ Complete Streamlit-Langflow integration
- ✅ Docker containerization with proper networking
- ✅ Vietnamese language support
- ✅ Security improvements

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