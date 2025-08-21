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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 