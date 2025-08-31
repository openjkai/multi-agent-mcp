"""
Multi-Agent MCP - Main FastAPI Application
Core orchestrator for managing MCP agents and RAG pipeline
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Multi-Agent MCP",
    description="AI Knowledge Hub with MCP Agents",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Multi-Agent MCP API",
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "message": "Backend is running successfully"
    }

@app.get("/config")
async def get_config():
    """Get application configuration"""
    from config import get_config_dict
    
    return {
        "status": "success",
        "configuration": get_config_dict()
    }

@app.get("/test-mcp")
async def test_mcp():
    """Test MCP client functionality"""
    from core.mcp_client import MCPClient
    
    client = MCPClient()
    await client.connect("http://localhost:8001", "test-agent")
    
    try:
        # Test query
        response = await client.send_query("Hello, test query!")
        status = await client.get_status()
        
        await client.cleanup()
        
        return {
            "test": "MCP Client",
            "status": "success",
            "response": response,
            "client_status": status
        }
    except Exception as e:
        await client.cleanup()
        return {
            "test": "MCP Client",
            "status": "error",
            "error": str(e)
        }

@app.get("/test-agent")
async def test_agent():
    """Test agent interface functionality"""
    from core.agent_interface import MockAgent
    
    # Create a mock agent
    agent = MockAgent(
        agent_id="test-agent-001",
        name="Test Agent",
        capabilities=["testing", "mock_responses", "health_check"]
    )
    
    # Activate and test
    await agent.activate()
    
    try:
        # Test query processing
        response = await agent.process_query("Hello from test endpoint!")
        status = agent.get_status()
        health = await agent.health_check()
        
        await agent.deactivate()
        
        return {
            "test": "Agent Interface",
            "status": "success",
            "agent_response": response,
            "agent_status": status,
            "health_check": health
        }
    except Exception as e:
        await agent.deactivate()
        return {
            "test": "Agent Interface",
            "status": "error",
            "error": str(e)
        }

@app.get("/test-registry")
async def test_registry():
    """Test agent registry functionality"""
    from core.agent_registry import AgentRegistry
    from core.agent_interface import MockAgent
    
    # Create registry
    registry = AgentRegistry()
    
    try:
        # Create and register multiple agents
        agent1 = MockAgent("docs-agent", "Document Agent", ["document_processing", "qa"])
        agent2 = MockAgent("code-agent", "Code Agent", ["code_analysis", "refactoring"])
        
        # Register agents
        await registry.register_agent(agent1)
        await registry.register_agent(agent2)
        
        # Test registry functions
        all_agents = registry.list_agents()
        registry_status = registry.get_registry_status()
        health_status = await registry.health_check_all()
        
        # Cleanup
        await registry.unregister_agent("docs-agent")
        await registry.unregister_agent("code-agent")
        
        return {
            "test": "Agent Registry",
            "status": "success",
            "registered_agents": len(all_agents),
            "registry_status": registry_status,
            "health_status": health_status
        }
    except Exception as e:
        return {
            "test": "Agent Registry",
            "status": "error",
            "error": str(e)
        }

@app.get("/test-manager")
async def test_manager():
    """Test agent manager functionality"""
    from core.agent_manager import AgentManager
    
    # Create and initialize manager
    manager = AgentManager()
    
    try:
        await manager.initialize()
        
        # Test query routing
        test_queries = [
            "Can you analyze this PDF document?",
            "Help me refactor this Python code",
            "Search for latest AI news",
            "Just have a general chat"
        ]
        
        results = []
        for query in test_queries:
            try:
                result = await manager.route_query(query)
                results.append({
                    "query": query,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "query": query,
                    "error": str(e)
                })
        
        # Get system status
        system_status = await manager.get_system_status()
        
        # Cleanup
        await manager.cleanup()
        
        return {
            "test": "Agent Manager",
            "status": "success",
            "query_results": results,
            "system_status": system_status
        }
    except Exception as e:
        try:
            await manager.cleanup()
        except:
            pass
        
        return {
            "test": "Agent Manager",
            "status": "error",
            "error": str(e)
        }

@app.post("/query")
async def process_query(query: str):
    """Process a query through the agent system"""
    from core.agent_manager import AgentManager
    
    # For now, create a new manager instance
    # In production, this would be a singleton
    manager = AgentManager()
    
    try:
        await manager.initialize()
        result = await manager.route_query(query)
        await manager.cleanup()
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        try:
            await manager.cleanup()
        except:
            pass
        
        return {
            "status": "error",
            "error": str(e)
        }

# RAG Pipeline Endpoints
@app.post("/rag/upload")
async def upload_document(filename: str, content: str, content_type: str = "text"):
    """Upload and process a document for RAG"""
    from core.rag_pipeline import RAGPipeline
    
    rag = RAGPipeline()
    
    try:
        await rag.initialize()
        doc_info = await rag.process_document(filename, content, content_type)
        await rag.cleanup()
        
        return {
            "status": "success",
            "message": "Document processed successfully",
            "document": {
                "id": doc_info.id,
                "filename": doc_info.filename,
                "chunk_count": doc_info.chunk_count,
                "processing_status": doc_info.processing_status
            }
        }
    except Exception as e:
        try:
            await rag.cleanup()
        except:
            pass
        
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/rag/query")
async def rag_query(query: str, top_k: int = 5):
    """Query the RAG system"""
    from core.rag_pipeline import RAGPipeline
    
    rag = RAGPipeline()
    
    try:
        await rag.initialize()
        results = await rag.query(query, top_k)
        await rag.cleanup()
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "total_results": len(results)
        }
    except Exception as e:
        try:
            await rag.cleanup()
        except:
            pass
        
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/rag/status")
async def rag_status():
    """Get RAG pipeline status"""
    from core.rag_pipeline import RAGPipeline
    
    rag = RAGPipeline()
    
    try:
        await rag.initialize()
        status = await rag.get_status()
        await rag.cleanup()
        
        return {
            "status": "success",
            "rag_status": status
        }
    except Exception as e:
        try:
            await rag.cleanup()
        except:
            pass
        
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/rag/test")
async def test_rag():
    """Test RAG pipeline with sample documents"""
    from core.rag_pipeline import RAGPipeline
    
    rag = RAGPipeline()
    
    try:
        await rag.initialize()
        
        # Upload sample documents
        sample_docs = [
            {
                "filename": "sample_ai_article.txt",
                "content": "Artificial Intelligence is transforming the world. Machine learning algorithms can now process vast amounts of data and make predictions with high accuracy. Deep learning has revolutionized computer vision and natural language processing.",
                "content_type": "text"
            },
            {
                "filename": "sample_code_guide.md",
                "content": "# Python Programming Guide\n\n## Variables\nVariables store data in Python.\n\n## Functions\nFunctions are reusable blocks of code.\n\n## Classes\nClasses define object-oriented structures.",
                "content_type": "markdown"
            }
        ]
        
        uploaded_docs = []
        for doc in sample_docs:
            doc_info = await rag.process_document(doc["filename"], doc["content"], doc["content_type"])
            uploaded_docs.append(doc_info)
        
        # Test queries
        test_queries = [
            "What is artificial intelligence?",
            "How do functions work in Python?",
            "What are the benefits of machine learning?"
        ]
        
        query_results = []
        for query in test_queries:
            results = await rag.query(query, top_k=3)
            query_results.append({
                "query": query,
                "results": results
            })
        
        # Get final status
        status = await rag.get_status()
        
        await rag.cleanup()
        
        return {
            "test": "RAG Pipeline",
            "status": "success",
            "uploaded_documents": len(uploaded_docs),
            "test_queries": query_results,
            "pipeline_status": status
        }
        
    except Exception as e:
        try:
            await rag.cleanup()
        except:
            pass
        
        return {
            "test": "RAG Pipeline",
            "status": "error",
            "error": str(e)
        }

@app.get("/embeddings/providers")
async def get_embedding_providers():
    """Get available embedding providers"""
    from core.embeddings import EmbeddingManager
    
    manager = EmbeddingManager()
    
    try:
        await manager.initialize()
        providers = manager.get_available_providers()
        
        provider_info = {}
        for provider in providers:
            provider_info[provider] = manager.get_provider_info(provider)
        
        await manager.cleanup()
        
        return {
            "status": "success",
            "available_providers": providers,
            "provider_details": provider_info,
            "default_provider": manager.default_provider
        }
    except Exception as e:
        try:
            await manager.cleanup()
        except:
            pass
        
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/embeddings/generate")
async def generate_embeddings(texts: List[str], provider: str = None):
    """Generate embeddings for texts"""
    from core.embeddings import EmbeddingManager
    
    manager = EmbeddingManager()
    
    try:
        await manager.initialize()
        result = await manager.generate_embeddings(texts, provider)
        await manager.cleanup()
        
        return {
            "status": "success",
            "embeddings_count": len(result.embeddings),
            "model": result.model,
            "dimensions": result.dimensions,
            "tokens_used": result.tokens_used,
            "cost": result.cost
        }
    except Exception as e:
        try:
            await manager.cleanup()
        except:
            pass
        
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/pdf/process")
async def process_pdf(filename: str, file_content: bytes):
    """Process PDF file and extract content"""
    from core.pdf_processor import PDFProcessor
    
    processor = PDFProcessor()
    
    try:
        if not processor.can_process(filename):
            return {
                "status": "error",
                "error": f"File format not supported: {filename}"
            }
        
        pdf_doc = await processor.process_pdf(file_content, filename)
        
        # Analyze document structure
        analysis = processor.analyze_document_structure(pdf_doc)
        
        return {
            "status": "success",
            "filename": filename,
            "total_pages": pdf_doc.total_pages,
            "total_characters": len(pdf_doc.text_content),
            "total_words": len(pdf_doc.text_content.split()),
            "tables_found": len(pdf_doc.extracted_tables),
            "images_found": len(pdf_doc.extracted_images),
            "document_analysis": analysis,
            "metadata": pdf_doc.metadata
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/system/status")
async def get_system_status():
    """Get comprehensive system status"""
    from core.agent_manager import AgentManager
    from core.rag_pipeline import RAGPipeline
    from core.embeddings import EmbeddingManager
    
    try:
        # Get agent manager status
        agent_manager = AgentManager()
        await agent_manager.initialize()
        agent_status = await agent_manager.get_system_status()
        await agent_manager.cleanup()
        
        # Get RAG pipeline status
        rag = RAGPipeline()
        await rag.initialize()
        rag_status = await rag.get_status()
        await rag.cleanup()
        
        # Get embedding manager status
        embedding_manager = EmbeddingManager()
        await embedding_manager.initialize()
        embedding_providers = embedding_manager.get_available_providers()
        await embedding_manager.cleanup()
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "name": "Multi-Agent MCP",
                "version": "0.1.0",
                "status": "running"
            },
            "agents": agent_status,
            "rag_pipeline": rag_status,
            "embeddings": {
                "available_providers": embedding_providers,
                "status": "initialized"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 