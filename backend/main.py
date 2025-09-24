"""
Multi-Agent MCP - Enhanced FastAPI Application
Enterprise-level orchestrator with authentication, workflows, and advanced features
3-day development plan implementation
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Import core modules
from core.database import db_manager
from core.auth import auth_manager
from core.workflow_engine import get_workflow_engine
from core.agent_manager import AgentManager
from core.rag_pipeline import RAGPipeline
from core.advanced_rag import AdvancedRAGPipeline
from core.embeddings import EmbeddingManager
from core.real_time_engine import real_time_engine
from core.ai_orchestrator import ai_orchestrator

# Import API routes
from api.auth_routes import router as auth_router
from api.workflow_routes import router as workflow_router
from api.websocket_routes import websocket_router, ai_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
agent_manager = None
rag_pipeline = None
advanced_rag_pipeline = None
embedding_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Multi-Agent MCP System...")
    
    try:
        # Initialize database
        await db_manager.initialize()
        logger.info("Database initialized")
        
        # Initialize global instances
        global agent_manager, rag_pipeline, advanced_rag_pipeline, embedding_manager
        
        agent_manager = AgentManager()
        await agent_manager.initialize()
        logger.info("Agent Manager initialized")
        
        rag_pipeline = RAGPipeline()
        await rag_pipeline.initialize()
        logger.info("RAG Pipeline initialized")
        
        advanced_rag_pipeline = AdvancedRAGPipeline()
        await advanced_rag_pipeline.initialize()
        logger.info("Advanced RAG Pipeline initialized")
        
        embedding_manager = EmbeddingManager()
        await embedding_manager.initialize()
        logger.info("Embedding Manager initialized")
        
        # Initialize workflow engine
        workflow_engine = get_workflow_engine()
        logger.info("Workflow Engine initialized")
        
        # Initialize real-time engine
        await real_time_engine.start()
        logger.info("Real-Time Engine initialized")
        
        # Initialize AI orchestrator
        await ai_orchestrator.initialize()
        logger.info("AI Orchestrator initialized")
        
        logger.info("🚀 Multi-Agent MCP System started successfully!")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {str(e)}")
        raise
    
    finally:
        # Cleanup
        logger.info("Shutting down Multi-Agent MCP System...")
        
        try:
            if agent_manager:
                await agent_manager.cleanup()
            if rag_pipeline:
                await rag_pipeline.cleanup()
            if advanced_rag_pipeline:
                await advanced_rag_pipeline.cleanup()
            if embedding_manager:
                await embedding_manager.cleanup()
            
            workflow_engine = get_workflow_engine()
            await workflow_engine.cleanup()
            
            await real_time_engine.stop()
            await ai_orchestrator.cleanup()
            
            await db_manager.cleanup()
            
            logger.info("System shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")

# Create FastAPI app
app = FastAPI(
    title="Multi-Agent MCP Enterprise",
    description="Advanced AI Knowledge Hub with Multi-Agent Orchestration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth_router)
app.include_router(workflow_router)
app.include_router(websocket_router)
app.include_router(ai_router)

# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Multi-Agent MCP Enterprise API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "Multi-Agent Orchestration",
            "Advanced RAG Pipeline", 
            "Workflow Engine",
            "User Authentication",
            "Real-time Monitoring"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Check database
        db_stats = await db_manager.get_system_stats()
        
        # Check agents
        agent_status = await agent_manager.get_system_status() if agent_manager else {"status": "not_initialized"}
        
        # Check RAG pipeline
        rag_status = await rag_pipeline.get_status() if rag_pipeline else {"status": "not_initialized"}
        
        # Check advanced RAG
        advanced_rag_status = await advanced_rag_pipeline.get_status() if advanced_rag_pipeline else {"status": "not_initialized"}
        
        # Check workflow engine
        workflow_engine = get_workflow_engine()
        workflow_stats = {
            "active_workflows": len(workflow_engine.active_workflows),
            "completed_workflows": len(workflow_engine.completed_workflows)
        }
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": "connected",
                "agents": agent_status.get("total_agents", 0),
                "rag_pipeline": rag_status.get("status", "unknown"),
                "advanced_rag": advanced_rag_status.get("status", "unknown"),
                "workflows": workflow_stats
            },
            "statistics": db_stats
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"System unhealthy: {str(e)}")

@app.get("/config")
async def get_config():
    """Get application configuration"""
    from config import get_config_dict, get_llm_config, get_rag_config, get_agent_config
    
    return {
        "status": "success",
        "configuration": {
            "general": get_config_dict(),
            "llm": get_llm_config(),
            "rag": get_rag_config(),
            "agents": get_agent_config()
        }
    }

# Legacy endpoints for backward compatibility
@app.post("/query")
async def process_query(query: str):
    """Process a query through the agent system (legacy endpoint)"""
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    try:
        result = await agent_manager.route_query(query)
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/rag/upload")
async def upload_document(filename: str, content: str, content_type: str = "text"):
    """Upload and process a document for RAG (legacy endpoint)"""
    if not advanced_rag_pipeline:
        raise HTTPException(status_code=503, detail="Advanced RAG pipeline not initialized")
    
    try:
        doc_info = await advanced_rag_pipeline.process_document(filename, content, content_type)
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
        logger.error(f"Document upload failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/rag/query")
async def rag_query(query: str, top_k: int = 5):
    """Query the RAG system (legacy endpoint)"""
    if not advanced_rag_pipeline:
        raise HTTPException(status_code=503, detail="Advanced RAG pipeline not initialized")
    
    try:
        results = await advanced_rag_pipeline.query(query, top_k=top_k)
        return {
            "status": "success",
            "query": query,
            "results": results,
            "total_results": len(results)
        }
    except Exception as e:
        logger.error(f"RAG query failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/system/status")
async def get_system_status():
    """Get comprehensive system status (legacy endpoint)"""
    try:
        # Get agent manager status
        agent_status = await agent_manager.get_system_status() if agent_manager else {}
        
        # Get RAG pipeline status
        rag_status = await advanced_rag_pipeline.get_status() if advanced_rag_pipeline else {}
        
        # Get embedding manager status
        embedding_providers = embedding_manager.get_available_providers() if embedding_manager else []
        
        # Get database stats
        db_stats = await db_manager.get_system_stats()
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "name": "Multi-Agent MCP Enterprise",
                "version": "1.0.0",
                "status": "running"
            },
            "agents": agent_status,
            "rag_pipeline": rag_status,
            "embeddings": {
                "available_providers": embedding_providers,
                "status": "initialized"
            },
            "database": db_stats
        }
    except Exception as e:
        logger.error(f"System status check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

# Test endpoints
@app.get("/test/agents")
async def test_agents():
    """Test agent functionality"""
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    try:
        test_queries = [
            "Can you analyze this document?",
            "Help me debug this code",
            "Search for AI news",
            "Hello, how are you?"
        ]
        
        results = []
        for query in test_queries:
            try:
                result = await agent_manager.route_query(query)
                results.append({
                    "query": query,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "query": query,
                    "error": str(e)
                })
        
        return {
            "test": "Agent System",
            "status": "success",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Agent test failed: {str(e)}")
        return {
            "test": "Agent System",
            "status": "error",
            "error": str(e)
        }

@app.get("/test/rag")
async def test_rag():
    """Test RAG pipeline functionality"""
    if not advanced_rag_pipeline:
        raise HTTPException(status_code=503, detail="Advanced RAG pipeline not initialized")
    
    try:
        # Upload sample document
        sample_content = """
        Artificial Intelligence (AI) is transforming the world in unprecedented ways. 
        Machine learning algorithms can now process vast amounts of data and make 
        predictions with remarkable accuracy. Deep learning has revolutionized 
        computer vision, natural language processing, and many other fields.
        
        Multi-agent systems represent the next frontier in AI development, where 
        multiple AI agents collaborate to solve complex problems that would be 
        difficult for a single agent to handle alone.
        """
        
        doc_info = await advanced_rag_pipeline.process_document(
            "sample_ai_article.txt", 
            sample_content, 
            "text"
        )
        
        # Test queries
        test_queries = [
            "What is artificial intelligence?",
            "How do multi-agent systems work?",
            "What are the applications of deep learning?"
        ]
        
        query_results = []
        for query in test_queries:
            results = await advanced_rag_pipeline.query(query, top_k=3)
            query_results.append({
                "query": query,
                "results": results
            })
        
        return {
            "test": "Advanced RAG Pipeline",
            "status": "success",
            "document_processed": {
                "id": doc_info.id,
                "filename": doc_info.filename,
                "chunks": doc_info.chunk_count
            },
            "query_results": query_results
        }
        
    except Exception as e:
        logger.error(f"RAG test failed: {str(e)}")
        return {
            "test": "Advanced RAG Pipeline",
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