"""
Configuration management for Multi-Agent MCP
Centralized configuration for today's major update
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Multi-Agent MCP"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # AI Providers
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Vector Store
    vector_store_type: str = Field(default="memory", env="VECTOR_STORE_TYPE")
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8000, env="CHROMA_PORT")
    
    # Agent Configuration
    max_agents: int = Field(default=10, env="MAX_AGENTS")
    agent_health_check_interval: int = Field(default=30, env="AGENT_HEALTH_CHECK_INTERVAL")
    
    # RAG Configuration
    max_chunk_size: int = Field(default=1000, env="MAX_CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    max_documents: int = Field(default=1000, env="MAX_DOCUMENTS")
    
    # MCP Configuration
    mcp_timeout: int = Field(default=30, env="MCP_TIMEOUT")
    mcp_retry_count: int = Field(default=3, env="MCP_RETRY_COUNT")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings

def get_config_dict() -> Dict[str, Any]:
    """Get configuration as dictionary"""
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "host": settings.host,
        "port": settings.port,
        "vector_store_type": settings.vector_store_type,
        "max_agents": settings.max_agents,
        "max_chunk_size": settings.max_chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "mcp_timeout": settings.mcp_timeout,
        "mcp_retry_count": settings.mcp_retry_count,
        "log_level": settings.log_level
    } 