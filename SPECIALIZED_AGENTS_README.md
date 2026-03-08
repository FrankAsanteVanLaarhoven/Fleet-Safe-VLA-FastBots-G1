# Specialized AI Agents System

## Overview

The Specialized AI Agents System is a comprehensive platform that provides intelligent crawling and content extraction capabilities for various web platforms and technologies. The system features specialized agents for WordPress, Framer, Webflow, Square Commerce, WooCommerce, Figma, and dynamic content sites.

## 🚀 Features

### Specialized Agents
- **WordPress Crawler**: Extract themes, plugins, custom post types, and WordPress-specific functionality
- **Framer Extractor**: Extract components, animations, design tokens, and interactive elements
- **Webflow Scraper**: Extract CMS content, dynamic interactions, and e-commerce features
- **Square Commerce**: Extract product catalogs, payment systems, and inventory data
- **WooCommerce**: Extract product data, order systems, and e-commerce functionality
- **Figma Assets**: Extract design components, style guides, and design tokens
- **Dynamic Content**: Handle SPAs, JavaScript-heavy sites, and real-time data
- **Mobile Apps**: Extract mobile app data, APIs, and native features

### AI Prompt Generation
- **Cursor AI**: Generate code generation prompts
- **Lovo AI**: Generate voice synthesis prompts
- **Winsurf**: Generate web development prompts
- **Bolt AI**: Generate rapid development prompts
- **Midjourney**: Generate image generation prompts
- **DALL-E**: Generate image creation prompts

### Advanced Capabilities
- Real-time site analysis and technology detection
- Intelligent content extraction and processing
- Specialized prompt generation for different AI platforms
- Comprehensive API integration
- Microservices orchestration
- Performance monitoring and metrics

## 🏗️ Architecture

### Frontend (Next.js 14 + TypeScript)
```
src/
├── app/
│   ├── page.tsx              # Main application interface
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── lib/
│   └── api.ts               # API integration service
└── components/
    ├── navigation/
    │   └── sidebar.tsx      # Navigation components
    └── ui/
        ├── button.tsx       # UI components
        └── card.tsx
```

### Backend (FastAPI + Python)
```
backend/
├── main.py                  # FastAPI application entry point
├── microservices_orchestrator.py  # Agent orchestration
├── advanced_crawler_orchestrator.py  # Advanced crawling system
├── api/
│   └── routes/
│       ├── agents.py        # Microservices agents API
│       └── specialized_agents.py  # Specialized agents API
├── core/
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connections
│   └── security.py         # Authentication and security
└── agents/
    ├── testing_agent.py    # Testing agent implementation
    └── frontend_clean_code_agent.py  # Clean code agent
```

## 🛠️ Installation

### Prerequisites
- Node.js 18+ and npm 9+
- Python 3.8+
- FastAPI and uvicorn

### Frontend Setup
```bash
# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

### Specialized Agents API

#### Get Available Agents
```http
GET /api/specialized-agents/agents
```

Response:
```json
{
  "agents": [
    {
      "id": "wordpress",
      "name": "WordPress Crawler",
      "description": "Specialized in WordPress sites, themes, plugins, and dynamic content",
      "capabilities": ["Theme extraction", "Plugin detection", "Database structure", "Dynamic content"]
    }
  ],
  "total_count": 8,
  "timestamp": "2024-01-01T00:00:00"
}
```

#### Get Prompt Types
```http
GET /api/specialized-agents/prompt-types
```

Response:
```json
{
  "prompt_types": [
    {
      "id": "cursor",
      "name": "Cursor",
      "description": "Generate Cursor AI prompts for code generation"
    }
  ],
  "total_count": 6,
  "timestamp": "2024-01-01T00:00:00"
}
```

#### Analyze Site
```http
POST /api/specialized-agents/analyze
Content-Type: application/json

{
  "url": "https://example.com",
  "agent_type": "wordpress"
}
```

Response:
```json
{
  "success": true,
  "analysis": {
    "platform": "WordPress",
    "capabilities": ["Theme extraction", "Plugin detection", "Database structure"],
    "analysis": {
      "theme_detected": true,
      "plugins_count": 15,
      "custom_post_types": 3
    }
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

#### Generate Specialized Prompt
```http
POST /api/specialized-agents/generate-prompt
Content-Type: application/json

{
  "url": "https://example.com",
  "agent_type": "wordpress",
  "prompt_type": "cursor"
}
```

Response:
```json
{
  "success": true,
  "prompt": "Create an exact clone of this WordPress site: https://example.com\n\nWordPress-Specific Requirements:\n- Extract and recreate WordPress theme structure\n...",
  "agent_type": "wordpress",
  "prompt_type": "cursor",
  "timestamp": "2024-01-01T00:00:00"
}
```

### Microservices Agents API

#### Get System Status
```http
GET /api/agents/status
```

#### Get All Agents
```http
GET /api/agents/agents
```

#### Submit Task
```http
POST /api/agents/tasks
Content-Type: application/json

{
  "type": "crawling",
  "payload": {
    "url": "https://example.com",
    "agent_type": "wordpress"
  }
}
```

#### Get Task Status
```http
GET /api/agents/tasks/{task_id}
```

## 🎯 Usage Examples

### Frontend Integration

```typescript
import { apiService } from '../lib/api';

// Analyze a WordPress site
const analysis = await apiService.analyzeSite('https://wordpress-site.com', 'wordpress');

// Generate a Cursor AI prompt
const prompt = await apiService.generatePrompt({
  url: 'https://wordpress-site.com',
  agent_type: 'wordpress',
  prompt_type: 'cursor'
});

// Get all specialized agents
const agents = await apiService.getSpecializedAgents();
```

### Backend Integration

```python
from backend.api.routes.specialized_agents import agent_manager

# Analyze site with WordPress agent
analysis = await agent_manager.analyze_site('https://wordpress-site.com', 'wordpress')

# Generate specialized prompt
prompt = await agent_manager.generate_prompt(
    'https://wordpress-site.com', 
    'wordpress', 
    'cursor'
)
```

## 🔧 Configuration

### Environment Variables

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Backend (config.py)
```python
# Database configuration
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Security settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS settings
CORS_ORIGINS = ["http://localhost:3000", "https://yourdomain.com"]

# Allowed hosts
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "yourdomain.com"]
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=dbname
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 📊 Performance Monitoring

The system includes comprehensive performance monitoring:

- Agent response times and success rates
- Task processing metrics
- System health monitoring
- Error tracking and logging
- Performance optimization recommendations

## 🔒 Security

- JWT-based authentication
- CORS protection
- Input validation and sanitization
- Rate limiting
- Secure API endpoints
- Environment variable protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation
- Review the troubleshooting guide

## 🔄 Changelog

### v2.0.0 (Current)
- Added specialized agents for 8 different platforms
- Implemented AI prompt generation for 6 AI platforms
- Added comprehensive API integration
- Enhanced frontend with real-time processing
- Added microservices orchestration
- Improved performance monitoring

### v1.0.0
- Initial release with basic crawling capabilities
- WordPress and dynamic content support
- Basic prompt generation

## 🎯 Roadmap

- [ ] Add more specialized agents (Shopify, Magento, etc.)
- [ ] Implement real-time collaboration features
- [ ] Add advanced analytics and reporting
- [ ] Enhance AI prompt customization
- [ ] Add mobile app support
- [ ] Implement cloud deployment options 