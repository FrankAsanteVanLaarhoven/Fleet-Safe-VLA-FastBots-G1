# 🚀 IronCloud-AI Platform

## World-Leading Agentic RAG & Military-Grade Web Intelligence Platform

IronCloud-AI represents the next evolution of AI-driven research and intelligence, integrating military-grade web extraction with agentic RAG capabilities to create the world's most advanced AI-driven research and intelligence platform.

## 🎯 Core Capabilities

### **Agentic RAG Pipeline**
- Multi-hop reasoning agents with self-improvement capabilities
- Dynamic source routing and query refinement
- Contextual embeddings with hybrid search
- Reranking and relevance optimization

### **Military-Grade Web Crawler**
- Stealth crawling with anti-detection mechanisms
- Paywall bypass and authentication handling
- Comprehensive metadata extraction
- Security assessment and vulnerability scanning

### **Enterprise Compliance**
- GDPR and SOC 2 compliance frameworks
- Automated SBOM generation
- Immutable audit trails
- Security vulnerability assessment

## 🏗️ Architecture

```
IronCloud-AI Platform
├── Frontend (React + TypeScript)
│   ├── Dashboard & Analytics
│   ├── Project Management
│   ├── Knowledge Base
│   └── MCP Integration
├── Backend (Python + FastAPI)
│   ├── Agentic RAG Engine
│   ├── IronCloud Crawler
│   ├── Security Suite
│   └── Compliance Framework
└── Infrastructure
    ├── Docker Containers
    ├── PostgreSQL Database
    └── Redis Cache
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/ironcloud-ai-platform.git
   cd ironcloud-ai-platform
   ```

2. **Start the backend services**
   ```bash
   docker-compose up -d
   ```

3. **Install frontend dependencies**
   ```bash
   cd ironcloud-ai-frontend
   npm install
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - MCP Server: http://localhost:8051

## 📋 Features

### **Core Functionality**
- ✅ Dashboard with overview metrics
- ✅ Project creation and management
- ✅ Task tracking and status updates
- ✅ Knowledge base with RAG queries
- ✅ Settings and configuration
- ✅ MCP integration and global rules
- ✅ Analytics and performance tracking
- ✅ User onboarding experience

### **Advanced Features**
- ✅ Agentic RAG pipeline integration
- ✅ Military-grade crawler interface
- ✅ Security assessment tools
- ✅ Compliance and audit features
- ✅ Real-time notifications
- ✅ Error handling and recovery
- ✅ Theme switching and customization
- ✅ Mobile responsiveness

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ironcloud_ai

# Redis
REDIS_URL=redis://localhost:6379

# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# MCP Server
MCP_SERVER_PORT=8051
```

### MCP Integration
IronCloud-AI provides MCP (Model Context Protocol) integration for seamless AI assistant connectivity:

```bash
# Cursor IDE
cursor://anysphere.cursor-deeplink/mcp/install?name=ironcloud&config=...

# Claude Desktop
claude mcp add --transport http ironcloud http://localhost:8051/mcp
```

## 📚 Documentation

- [Implementation Guide](./docs/IRONCLOUD_AI_IMPLEMENTATION_GUIDE.md)
- [Platform Architecture](./docs/IRONCLOUD_AI_PLATFORM.md)
- [API Documentation](./docs/API.md)
- [MCP Integration](./docs/MCP_INTEGRATION.md)

## 🧪 Testing

### Frontend Tests
```bash
cd ironcloud-ai-frontend
npm run test
```

### Backend Tests
```bash
cd python
python -m pytest tests/
```

### End-to-End Tests
```bash
npm run test:e2e
```

## 🚀 Deployment

### Production Build
```bash
# Frontend
cd ironcloud-ai-frontend
npm run build

# Backend
docker-compose -f docker-compose.prod.yml up -d
```

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.ironcloud-ai.com](https://docs.ironcloud-ai.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/ironcloud-ai-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/ironcloud-ai-platform/discussions)

## 🏆 Acknowledgments

IronCloud-AI builds upon the foundation of advanced AI research and development practices, incorporating:

- Agentic RAG methodologies
- Military-grade security practices
- Enterprise compliance frameworks
- Modern web development standards

---

**IronCloud-AI** - The future of intelligent research and development.
