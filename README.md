# 🤖 Multi-Agent MCP - AI Knowledge Hub

A showcase repository demonstrating how to build **multi-agent AI tools** using Model Context Protocol (MCP), RAG, and LangChain. This project serves as both a playground and reference implementation for building intelligent, pluggable AI assistants.

## 🎯 Project Vision

Build a **pluggable AI knowledge assistant** where each "agent" is a microservice powered by MCP. Agents can be specialized for different tasks and collaborate through the MCP protocol, orchestrated by LangChain.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI       │    │   Agent Manager │    │   Specialized   │
│   (Next.js)    │◄──►│   Orchestrator  │◄──►│   AI Agents     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   RAG Pipeline  │
                       │   (Vector Store)│
                       └─────────────────┘
```

## 🚀 Core Features

- **Pluggable Agent System**: Add new agents without changing core code
- **MCP Integration**: Standardized communication between agents
- **RAG Pipeline**: Document processing and intelligent retrieval
- **Multi-Agent Collaboration**: Agents can hand off tasks to each other
- **Real-time Chat Interface**: Interactive web UI for agent communication
- **Document Upload**: Drag-and-drop file processing with progress tracking
- **System Monitoring**: Real-time status and health monitoring

## 🎭 Agent Types

- **📚 Document Agent**: PDF analysis, text extraction, document Q&A
- **💻 Code Agent**: Code analysis, debugging, refactoring, generation
- **🌐 Web Agent**: Real-time web search, news fetching, fact checking
- **💬 Chat Agent**: General conversation, task coordination, agent orchestration

## 🛠️ Tech Stack

### Backend
- **Python 3.9+** with FastAPI
- **Agent System**: Custom multi-agent orchestrator
- **RAG Pipeline**: Document chunking, vector search
- **Vector Store**: In-memory (extensible to ChromaDB, FAISS)
- **AI Providers**: OpenAI, Anthropic (configurable)

### Frontend
- **Next.js 14** with TypeScript
- **React 18** with modern hooks
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Lucide React** for icons

## 📦 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: Create .env file for API keys
echo "OPENAI_API_KEY=your_key_here" > .env
echo "ANTHROPIC_API_KEY=your_key_here" >> .env

# Start the backend server
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

Create a `.env` file in the backend directory:
```env
# AI Provider Configuration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CHUNKS_PER_QUERY=5

# Vector Store Configuration
VECTOR_STORE_TYPE=memory
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Agent Configuration
MAX_AGENTS=10
AGENT_TIMEOUT=30
HEALTH_CHECK_INTERVAL=30
```

## 🎮 Usage Examples

### Document Processing
1. Upload documents via the web interface
2. Ask questions about your documents
3. Get AI-powered summaries and insights

### Code Assistance
```
User: "Can you help me refactor this Python function?"
Code Agent: "I can help refactor code for better performance, readability, and maintainability..."
```

### Web Search
```
User: "What's the latest news about AI?"
Web Agent: "I can fetch the latest news and current events..."
```

### General Chat
```
User: "Hello, how can you help me?"
Chat Agent: "Hello! I'm here to help with general questions and coordinate tasks between agents..."
```

## 🧪 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /system/status` - System status and metrics
- `POST /query` - Process user queries through agents

### RAG Pipeline
- `POST /rag/upload` - Upload and process documents
- `POST /rag/query` - Query the RAG system
- `GET /rag/status` - RAG pipeline status

### Agent Management
- `GET /test-agent` - Test individual agents
- `GET /test-manager` - Test agent manager
- `GET /test-registry` - Test agent registry

## 🔍 System Monitoring

The system provides comprehensive monitoring:
- **Agent Health**: Real-time health checks for all agents
- **Performance Metrics**: Query processing times and success rates
- **System Status**: Overall system health and statistics
- **Query History**: Track all interactions and responses

## 🚧 Development Roadmap

### Phase 1 (Current)
- ✅ Basic agent system with 4 specialized agents
- ✅ RAG pipeline with document processing
- ✅ Web interface with real-time chat
- ✅ System monitoring and health checks

### Phase 2 (Next)
- [ ] Real vector embeddings (ChromaDB/FAISS integration)
- [ ] Advanced agent collaboration protocols
- [ ] Plugin system for custom agents
- [ ] Authentication and user management

### Phase 3 (Future)
- [ ] Multi-tenant support
- [ ] Advanced RAG techniques (hybrid search, reranking)
- [ ] Agent marketplace and sharing
- [ ] Production deployment guides

## 🤝 Contributing

This is a showcase project - feel free to fork and adapt for your own use cases!

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Adding New Agents
1. Create a new agent class in `backend/core/specialized_agents.py`
2. Implement the `BaseAgent` interface
3. Register the agent in `AgentManager._register_default_agents()`
4. Update the frontend agent list in `frontend/src/app/page.tsx`

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Model Context Protocol (MCP)** for standardized AI communication
- **LangChain** for AI orchestration patterns
- **FastAPI** for the robust backend framework
- **Next.js** for the modern frontend framework

---

**Built with ❤️ using MCP, LangChain, and modern AI technologies**

*Last updated: December 2024* 