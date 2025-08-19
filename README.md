# 🤖 Multi-Agent MCP - AI Knowledge Hub

A showcase repository demonstrating how to build **multi-agent AI tools** using Model Context Protocol (MCP), RAG, and LangChain. This project serves as both a playground and reference implementation for building intelligent, pluggable AI assistants.

## 🎯 Project Vision

Build a **pluggable AI knowledge assistant** where each "agent" is a microservice powered by MCP. Agents can be specialized for different tasks and collaborate through the MCP protocol, orchestrated by LangChain.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI       │    │   LangChain     │    │   MCP Agents    │
│   (Next.js)    │◄──►│   Orchestrator  │◄──►│   (Microservices)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   RAG Pipeline  │
                       │   (Chroma/FAISS)│
                       └─────────────────┘
```

## 🚀 Core Features

- **Pluggable Agent System**: Add new agents without changing core code
- **MCP Integration**: Standardized communication between agents
- **RAG Pipeline**: Document processing and intelligent retrieval
- **Multi-Agent Collaboration**: Agents can hand off tasks to each other
- **Extensible Connectors**: Easy integration with external services

## 🎭 Agent Types

- **📚 Docs Agent**: Answer questions from PDFs, Markdown, Confluence
- **💻 Code Agent**: Explain, refactor, and generate code
- **🌐 Web Agent**: Fetch real-time information via web search
- **💬 Chat Agent**: General LLM conversation and task coordination

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, LangChain
- **Frontend**: Next.js, React, Tailwind CSS
- **Database**: ChromaDB (vector store), SQLite (metadata)
- **Protocol**: MCP (Model Context Protocol)
- **AI**: OpenAI, Anthropic (configurable)
- **Deployment**: Docker, Docker Compose

## 📦 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker (optional)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Configuration

Create a `.env` file in the backend directory:
```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

## 🤝 Contributing

This is a showcase project - feel free to fork and adapt for your own use cases!

## 📄 License

MIT License - see LICENSE file for details

---

**Built with ❤️ using MCP, LangChain, and modern AI technologies** 