"""
Configuration settings for Multi-Agent MCP
Enhanced configuration for today's major update
"""

import os
from typing import Dict, Any, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_title: str = "Multi-Agent MCP"
    api_description: str = "AI Knowledge Hub with MCP Agents"
    api_version: str = "0.2.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # AI Provider Configuration
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_llm_provider: str = "openai"
    default_embedding_provider: str = "openai"
    
    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_chunks_per_query: int = 5
    similarity_threshold: float = 0.7
    
    # Vector Store Configuration
    vector_store_type: str = "memory"  # memory, chroma, faiss
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection_name: str = "multi_agent_docs"
    
    # Agent Configuration
    max_agents: int = 10
    agent_timeout: int = 30
    health_check_interval: int = 30
    
    # File Processing Configuration
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_file_types: List[str] = [".txt", ".md", ".pdf", ".docx"]
    upload_dir: str = "uploads"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # Performance Configuration
    max_concurrent_requests: int = 100
    request_timeout: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_config_dict() -> Dict[str, Any]:
    """Get configuration as dictionary (excluding sensitive data)"""
    config = settings.dict()
    
    # Remove sensitive information
    sensitive_keys = ["openai_api_key", "anthropic_api_key", "secret_key"]
    for key in sensitive_keys:
        if key in config:
            config[key] = "***" if config[key] else ""
    
    return config

def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration"""
    return {
        "default_provider": settings.default_llm_provider,
        "openai_configured": bool(settings.openai_api_key),
        "anthropic_configured": bool(settings.anthropic_api_key)
    }

def get_rag_config() -> Dict[str, Any]:
    """Get RAG configuration"""
    return {
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "max_chunks_per_query": settings.max_chunks_per_query,
        "similarity_threshold": settings.similarity_threshold,
        "vector_store_type": settings.vector_store_type
    }

def get_agent_config() -> Dict[str, Any]:
    """Get agent configuration"""
    return {
        "max_agents": settings.max_agents,
        "agent_timeout": settings.agent_timeout,
        "health_check_interval": settings.health_check_interval
    } 