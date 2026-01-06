"""
Enhanced Embedding System - Better providers and error handling
Improved implementation for 2-day development plan
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Result from embedding generation"""
    embeddings: List[List[float]]
    model: str
    dimensions: int
    tokens_used: Optional[int] = None
    cost: Optional[float] = None

class BaseEmbeddingProvider:
    """Base class for embedding providers"""
    
    def __init__(self, model_name: str, dimensions: int):
        self.model_name = model_name
        self.dimensions = dimensions
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the provider"""
        self.is_initialized = True
    
    async def generate_embeddings(self, texts: List[str]) -> EmbeddingResult:
        """Generate embeddings for texts"""
        raise NotImplementedError
    
    async def cleanup(self):
        """Cleanup resources"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            "model": self.model_name,
            "dimensions": self.dimensions,
            "initialized": self.is_initialized
        }

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider with enhanced error handling"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        super().__init__(model, 1536)
        self.api_key = api_key
        self.client = None
        self.rate_limit_delay = 0.1  # Seconds between requests
    
    async def initialize(self):
        """Initialize OpenAI client"""
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            self.is_initialized = True
            logger.info(f"OpenAI embedding provider initialized with model {self.model_name}")
        except ImportError:
            logger.error("OpenAI package not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> EmbeddingResult:
        """Generate embeddings using OpenAI API"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Process in batches to avoid rate limits
            batch_size = 100
            all_embeddings = []
            total_tokens = 0
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Add rate limiting
                if i > 0:
                    await asyncio.sleep(self.rate_limit_delay)
                
                try:
                    response = await self.client.embeddings.create(
                        model=self.model_name,
                        input=batch
                    )
                    
                    batch_embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(batch_embeddings)
                    total_tokens += response.usage.total_tokens
                except Exception as e:
                    error_msg = str(e)
                    if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                        raise RuntimeError(f"OpenAI API authentication failed. Check your API key: {error_msg}")
                    elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                        raise RuntimeError(f"OpenAI API rate limit exceeded. Please wait and try again: {error_msg}")
                    elif "model" in error_msg.lower():
                        raise RuntimeError(f"OpenAI model unavailable: {error_msg}")
                    else:
                        raise RuntimeError(f"OpenAI API error: {error_msg}")
            
            return EmbeddingResult(
                embeddings=all_embeddings,
                model=self.model_name,
                dimensions=self.dimensions,
                tokens_used=total_tokens,
                cost=total_tokens * 0.0001  # Approximate cost
            )
            
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {str(e)}")
            raise

class SentenceTransformerProvider(BaseEmbeddingProvider):
    """Local sentence transformer provider for offline usage"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Dimensions vary by model
        dimensions_map = {
            "all-MiniLM-L6-v2": 384,
            "all-mpnet-base-v2": 768,
            "multi-qa-MiniLM-L6-cos-v1": 384
        }
        dimensions = dimensions_map.get(model_name, 384)
        super().__init__(model_name, dimensions)
        self.model = None
    
    async def initialize(self):
        """Initialize sentence transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.is_initialized = True
            logger.info(f"SentenceTransformer provider initialized with model {self.model_name}")
        except ImportError:
            logger.error("sentence-transformers package not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize SentenceTransformer provider: {str(e)}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> EmbeddingResult:
        """Generate embeddings using sentence transformers"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, 
                self.model.encode, 
                texts
            )
            
            # Convert numpy arrays to lists
            embeddings_list = [emb.tolist() for emb in embeddings]
            
            return EmbeddingResult(
                embeddings=embeddings_list,
                model=self.model_name,
                dimensions=self.dimensions,
                tokens_used=sum(len(text.split()) for text in texts),  # Approximate
                cost=0.0  # Free local model
            )
            
        except Exception as e:
            logger.error(f"SentenceTransformer embedding generation failed: {str(e)}")
            raise

class MockEmbeddingProvider(BaseEmbeddingProvider):
    """Mock provider for testing and development"""
    
    def __init__(self, dimensions: int = 384):
        super().__init__("mock-embedding-model", dimensions)
    
    async def initialize(self):
        """Initialize mock provider"""
        self.is_initialized = True
        logger.info("Mock embedding provider initialized")
    
    async def generate_embeddings(self, texts: List[str]) -> EmbeddingResult:
        """Generate mock embeddings"""
        if not self.is_initialized:
            await self.initialize()
        
        # Generate random embeddings for testing
        embeddings = []
        for text in texts:
            # Create deterministic "embeddings" based on text hash
            text_hash = hash(text)
            np.random.seed(abs(text_hash) % (2**32))
            embedding = np.random.normal(0, 1, self.dimensions).tolist()
            embeddings.append(embedding)
        
        return EmbeddingResult(
            embeddings=embeddings,
            model=self.model_name,
            dimensions=self.dimensions,
            tokens_used=sum(len(text.split()) for text in texts),
            cost=0.0
        )
    
    async def cleanup(self):
        """Cleanup mock provider"""
        return True

class EmbeddingManager:
    """Enhanced embedding manager with multiple providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseEmbeddingProvider] = {}
        self.default_provider = "mock"
        self.initialized_providers = set()
    
    async def initialize(self):
        """Initialize embedding manager with available providers"""
        logger.info("Initializing Embedding Manager")
        
        # Always add mock provider
        self.providers["mock"] = MockEmbeddingProvider()
        
        # Try to add OpenAI provider
        try:
            from config import settings
            if settings.openai_api_key:
                self.providers["openai"] = OpenAIEmbeddingProvider(settings.openai_api_key)
                self.default_provider = "openai"
        except Exception as e:
            logger.warning(f"Could not initialize OpenAI provider: {str(e)}")
        
        # Try to add SentenceTransformer provider
        try:
            self.providers["sentence_transformer"] = SentenceTransformerProvider()
            if self.default_provider == "mock":
                self.default_provider = "sentence_transformer"
        except Exception as e:
            logger.warning(f"Could not initialize SentenceTransformer provider: {str(e)}")
        
        logger.info(f"Embedding Manager initialized with providers: {list(self.providers.keys())}")
        logger.info(f"Default provider: {self.default_provider}")
    
    async def generate_embeddings(self, texts: List[str], provider: Optional[str] = None) -> EmbeddingResult:
        """Generate embeddings using specified or default provider with fallback"""
        provider_name = provider or self.default_provider
        
        # Try primary provider first
        if provider_name in self.providers:
            provider_instance = self.providers[provider_name]
            
            # Initialize provider if needed
            if provider_name not in self.initialized_providers:
                try:
                    await provider_instance.initialize()
                    self.initialized_providers.add(provider_name)
                except Exception as e:
                    logger.warning(f"Failed to initialize provider {provider_name}: {str(e)}")
                    # Fall through to fallback
            
            # Try to generate embeddings
            try:
                return await provider_instance.generate_embeddings(texts)
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {str(e)}. Trying fallback...")
                # Fall through to fallback
        
        # Fallback to mock provider if primary fails
        if "mock" in self.providers and provider_name != "mock":
            logger.info(f"Falling back to mock provider")
            try:
                mock_provider = self.providers["mock"]
                if "mock" not in self.initialized_providers:
                    await mock_provider.initialize()
                    self.initialized_providers.add("mock")
                return await mock_provider.generate_embeddings(texts)
            except Exception as e:
                logger.error(f"Mock provider also failed: {str(e)}")
        
        # If all providers fail, raise error
        raise RuntimeError(
            f"All embedding providers failed. Tried: {provider_name}, fallback: mock. "
            f"Available providers: {list(self.providers.keys())}"
        )
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_provider_info(self, provider_name: str) -> Dict[str, Any]:
        """Get information about a specific provider"""
        if provider_name not in self.providers:
            return {"error": "Provider not found"}
        
        return self.providers[provider_name].get_info()
    
    async def benchmark_providers(self, test_texts: List[str]) -> Dict[str, Dict[str, Any]]:
        """Benchmark all available providers"""
        results = {}
        
        for provider_name in self.providers.keys():
            try:
                start_time = datetime.utcnow()
                result = await self.generate_embeddings(test_texts, provider_name)
                end_time = datetime.utcnow()
                
                processing_time = (end_time - start_time).total_seconds()
                
                results[provider_name] = {
                    "success": True,
                    "processing_time": processing_time,
                    "embeddings_count": len(result.embeddings),
                    "dimensions": result.dimensions,
                    "tokens_used": result.tokens_used,
                    "cost": result.cost
                }
            except Exception as e:
                results[provider_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    async def cleanup(self):
        """Cleanup all providers"""
        for provider in self.providers.values():
            await provider.cleanup()
        
        logger.info("Embedding Manager cleanup completed") 