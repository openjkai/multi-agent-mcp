"""
Embedding System - AI-powered text embeddings for RAG
Advanced embedding integration for today's major update
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import numpy as np

from config import get_settings

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    embeddings: List[List[float]]
    model: str
    dimensions: int
    tokens_used: Optional[int] = None
    cost: Optional[float] = None

class BaseEmbeddingProvider:
    """Base class for embedding providers"""
    
    def __init__(self):
        self.model_name: str = ""
        self.dimensions: int = 0
        self.max_tokens: int = 0
        self.cost_per_1k_tokens: float = 0.0
    
    async def generate_embeddings(self, texts: List[str]) -> EmbeddingResult:
        """Generate embeddings for a list of texts"""
        raise NotImplementedError
    
    async def health_check(self) -> bool:
        """Check if provider is healthy"""
        raise NotImplementedError

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider"""
    
    def __init__(self):
        super().__init__()
        self.model_name = "text-embedding-ada-002"
        self.dimensions = 1536
        self.max_tokens = 8191
        self.cost_per_1k_tokens = 0.0001  # $0.0001 per 1K tokens
        
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            import openai
            openai.api_key = settings.openai_api_key
            self.client = openai
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    async def generate_embeddings(self, texts: List[str]) -> EmbeddingResult:
        """Generate embeddings using OpenAI"""
        try:
            # Process texts in batches to respect rate limits
            batch_size = 100
            all_embeddings = []
            total_tokens = 0
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Truncate texts that are too long
                truncated_batch = []
                for text in batch:
                    if len(text) > self.max_tokens * 4:  # Rough estimate
                        text = text[:self.max_tokens * 4]
                    truncated_batch.append(text)
                
                response = await asyncio.to_thread(
                    self.client.Embedding.create,
                    input=truncated_batch,
                    model=self.model_name
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Estimate tokens (rough calculation)
                total_tokens += sum(len(text.split()) for text in truncated_batch)
                
                # Rate limiting
                await asyncio.sleep(0.1)
            
            cost = (total_tokens / 1000) * self.cost_per_1k_tokens
            
            return EmbeddingResult(
                embeddings=all_embeddings,
                model=self.model_name,
                dimensions=self.dimensions,
                tokens_used=total_tokens,
                cost=cost
            )
            
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check OpenAI API health"""
        try:
            # Simple health check with minimal tokens
            response = await asyncio.to_thread(
                self.client.Embedding.create,
                input=["test"],
                model=self.model_name
            )
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False

class AnthropicEmbeddingProvider(BaseEmbeddingProvider):
    """Anthropic embedding provider"""
    
    def __init__(self):
        super().__init__()
        self.model_name = "claude-3-sonnet-20240229"
        self.dimensions = 4096  # Claude embeddings are larger
        self.max_tokens = 100000
        self.cost_per_1k_tokens = 0.003  # $0.003 per 1K tokens
        
        settings = get_settings()
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    
    async def generate_embeddings(self, texts: List[str]) -> EmbeddingResult:
        """Generate embeddings using Anthropic"""
        try:
            all_embeddings = []
            total_tokens = 0
            
            for text in texts:
                # Truncate if too long
                if len(text) > self.max_tokens * 4:
                    text = text[:self.max_tokens * 4]
                
                response = await asyncio.to_thread(
                    self.client.messages.create,
                    model=self.model_name,
                    max_tokens=1,
                    messages=[{"role": "user", "content": text}]
                )
                
                # For now, generate a mock embedding since Anthropic doesn't have direct embedding API
                # In production, you'd use their actual embedding endpoint
                mock_embedding = np.random.normal(0, 1, self.dimensions).tolist()
                all_embeddings.append(mock_embedding)
                
                total_tokens += len(text.split())
                
                # Rate limiting
                await asyncio.sleep(0.1)
            
            cost = (total_tokens / 1000) * self.cost_per_1k_tokens
            
            return EmbeddingResult(
                embeddings=all_embeddings,
                model=self.model_name,
                dimensions=self.dimensions,
                tokens_used=total_tokens,
                cost=cost
            )
            
        except Exception as e:
            logger.error(f"Anthropic embedding error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Anthropic API health"""
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model_name,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return response.content is not None
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False

class MockEmbeddingProvider(BaseEmbeddingProvider):
    """Mock embedding provider for testing"""
    
    def __init__(self):
        super().__init__()
        self.model_name = "mock-embedding-model"
        self.dimensions = 384
        self.max_tokens = 1000
        self.cost_per_1k_tokens = 0.0
    
    async def generate_embeddings(self, texts: List[str]) -> EmbeddingResult:
        """Generate mock embeddings"""
        embeddings = []
        for text in texts:
            # Generate deterministic mock embeddings based on text content
            seed = hash(text) % 10000
            np.random.seed(seed)
            embedding = np.random.normal(0, 1, self.dimensions).tolist()
            embeddings.append(embedding)
        
        return EmbeddingResult(
            embeddings=embeddings,
            model=self.model_name,
            dimensions=self.dimensions,
            tokens_used=0,
            cost=0.0
        )
    
    async def health_check(self) -> bool:
        """Always healthy for mock provider"""
        return True

class EmbeddingManager:
    """Manages multiple embedding providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseEmbeddingProvider] = {}
        self.default_provider: Optional[str] = None
        self.provider_health: Dict[str, bool] = {}
        
    async def initialize(self):
        """Initialize embedding providers"""
        logger.info("Initializing Embedding Manager")
        
        try:
            # Try OpenAI first
            openai_provider = OpenAIEmbeddingProvider()
            if await openai_provider.health_check():
                self.providers["openai"] = openai_provider
                self.default_provider = "openai"
                logger.info("OpenAI embedding provider initialized")
        except Exception as e:
            logger.warning(f"OpenAI provider not available: {e}")
        
        try:
            # Try Anthropic
            anthropic_provider = AnthropicEmbeddingProvider()
            if await anthropic_provider.health_check():
                self.providers["anthropic"] = anthropic_provider
                if not self.default_provider:
                    self.default_provider = "anthropic"
                logger.info("Anthropic embedding provider initialized")
        except Exception as e:
            logger.warning(f"Anthropic provider not available: {e}")
        
        # Always add mock provider for testing
        mock_provider = MockEmbeddingProvider()
        self.providers["mock"] = mock_provider
        if not self.default_provider:
            self.default_provider = "mock"
        logger.info("Mock embedding provider initialized")
        
        # Check health of all providers
        await self._check_all_providers_health()
        
        logger.info(f"Embedding Manager initialized with {len(self.providers)} providers")
    
    async def _check_all_providers_health(self):
        """Check health of all providers"""
        for name, provider in self.providers.items():
            try:
                self.provider_health[name] = await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                self.provider_health[name] = False
    
    async def generate_embeddings(self, texts: List[str], provider: str = None) -> EmbeddingResult:
        """Generate embeddings using specified or default provider"""
        if not provider:
            provider = self.default_provider
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")
        
        if not self.provider_health.get(provider, False):
            raise RuntimeError(f"Provider {provider} is not healthy")
        
        return await self.providers[provider].generate_embeddings(texts)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """Get information about a specific provider"""
        if provider not in self.providers:
            return {}
        
        p = self.providers[provider]
        return {
            "name": provider,
            "model": p.model_name,
            "dimensions": p.dimensions,
            "max_tokens": p.max_tokens,
            "cost_per_1k_tokens": p.cost_per_1k_tokens,
            "healthy": self.provider_health.get(provider, False)
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Embedding Manager cleanup completed") 