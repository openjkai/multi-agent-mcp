"""
Advanced RAG Pipeline - Enhanced with real embeddings and vector search
Next-level implementation for 2-day development plan
"""

import logging
import asyncio
import hashlib
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import numpy as np

from .embeddings import EmbeddingManager
from .rag_pipeline import DocumentProcessor, DocumentInfo, DocumentChunk

logger = logging.getLogger(__name__)

@dataclass
class VectorSearchResult:
    """Enhanced search result with similarity scores"""
    chunk_id: str
    document_id: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

@dataclass
class SearchQuery:
    """Search query with parameters"""
    text: str
    top_k: int = 5
    similarity_threshold: float = 0.7
    filters: Optional[Dict[str, Any]] = None
    rerank: bool = False

class AdvancedVectorStore:
    """Advanced vector store with real embeddings and similarity search"""
    
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
        self.documents: Dict[str, DocumentInfo] = {}
        self.chunks: Dict[str, DocumentChunk] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self.metadata_index: Dict[str, List[str]] = {}  # metadata_key -> chunk_ids
        self.initialized = False
    
    async def initialize(self):
        """Initialize the vector store"""
        await self.embedding_manager.initialize()
        self.initialized = True
        logger.info("Advanced Vector Store initialized")
    
    async def add_document(self, doc_info: DocumentInfo, chunks: List[DocumentChunk]):
        """Add document with embedding generation"""
        if not self.initialized:
            await self.initialize()
        
        # Store document info
        self.documents[doc_info.id] = doc_info
        
        # Process chunks and generate embeddings
        chunk_texts = []
        chunk_ids = []
        
        for chunk in chunks:
            self.chunks[chunk.id] = chunk
            chunk_texts.append(chunk.content)
            chunk_ids.append(chunk.id)
            
            # Index metadata
            for key, value in chunk.metadata.items():
                if key not in self.metadata_index:
                    self.metadata_index[key] = []
                if chunk.id not in self.metadata_index[key]:
                    self.metadata_index[key].append(chunk.id)
        
        # Generate embeddings for all chunks
        if chunk_texts:
            try:
                embedding_result = await self.embedding_manager.generate_embeddings(chunk_texts)
                
                # Store embeddings
                for chunk_id, embedding in zip(chunk_ids, embedding_result.embeddings):
                    self.embeddings[chunk_id] = embedding
                    # Also store in chunk object
                    if chunk_id in self.chunks:
                        self.chunks[chunk_id].embedding = embedding
                
                logger.info(f"Generated embeddings for {len(chunk_texts)} chunks from document {doc_info.filename}")
                
            except Exception as e:
                logger.error(f"Failed to generate embeddings for document {doc_info.filename}: {str(e)}")
                # Fallback to storing without embeddings
                for chunk_id in chunk_ids:
                    self.embeddings[chunk_id] = None
    
    async def search(self, query: SearchQuery) -> List[VectorSearchResult]:
        """Advanced vector similarity search"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Generate query embedding
            query_result = await self.embedding_manager.generate_embeddings([query.text])
            query_embedding = query_result.embeddings[0]
            
            # Calculate similarities
            similarities = []
            for chunk_id, chunk_embedding in self.embeddings.items():
                if chunk_embedding is None:
                    continue  # Skip chunks without embeddings
                
                # Apply filters if specified
                if query.filters:
                    chunk = self.chunks[chunk_id]
                    if not self._matches_filters(chunk, query.filters):
                        continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                
                if similarity >= query.similarity_threshold:
                    similarities.append((chunk_id, similarity))
            
            # Sort by similarity and take top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_results = similarities[:query.top_k]
            
            # Create search results
            results = []
            for chunk_id, similarity in top_results:
                chunk = self.chunks[chunk_id]
                result = VectorSearchResult(
                    chunk_id=chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    similarity_score=similarity,
                    metadata=chunk.metadata,
                    embedding=self.embeddings[chunk_id] if query.rerank else None
                )
                results.append(result)
            
            logger.info(f"Vector search for '{query.text}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            # Fallback to keyword search
            return await self._fallback_keyword_search(query)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
            
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {str(e)}")
            return 0.0
    
    def _matches_filters(self, chunk: DocumentChunk, filters: Dict[str, Any]) -> bool:
        """Check if chunk matches the specified filters"""
        for key, value in filters.items():
            if key not in chunk.metadata:
                return False
            if chunk.metadata[key] != value:
                return False
        return True
    
    async def _fallback_keyword_search(self, query: SearchQuery) -> List[VectorSearchResult]:
        """Fallback keyword search when embeddings fail"""
        logger.warning("Falling back to keyword search")
        
        query_words = query.text.lower().split()
        chunk_scores = {}
        
        for chunk_id, chunk in self.chunks.items():
            score = 0
            content_lower = chunk.content.lower()
            
            for word in query_words:
                if word in content_lower:
                    score += content_lower.count(word)
            
            if score > 0:
                chunk_scores[chunk_id] = score / len(query_words)
        
        # Sort and take top results
        sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)[:query.top_k]
        
        results = []
        for chunk_id, score in sorted_chunks:
            chunk = self.chunks[chunk_id]
            result = VectorSearchResult(
                chunk_id=chunk_id,
                document_id=chunk.document_id,
                content=chunk.content,
                similarity_score=score,
                metadata=chunk.metadata
            )
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed vector store statistics"""
        embedded_chunks = sum(1 for emb in self.embeddings.values() if emb is not None)
        
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "embedded_chunks": embedded_chunks,
            "embedding_coverage": embedded_chunks / len(self.chunks) if self.chunks else 0,
            "metadata_keys": list(self.metadata_index.keys()),
            "average_chunk_size": np.mean([len(chunk.content) for chunk in self.chunks.values()]) if self.chunks else 0
        }

class AdvancedRAGPipeline:
    """Advanced RAG pipeline with enhanced capabilities"""
    
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.processor = DocumentProcessor()
        self.vector_store = AdvancedVectorStore(self.embedding_manager)
        self.query_history: List[Dict[str, Any]] = []
        self.processing_stats = {
            "documents_processed": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "queries_processed": 0,
            "processing_errors": 0
        }
    
    async def initialize(self):
        """Initialize the advanced RAG pipeline"""
        logger.info("Initializing Advanced RAG Pipeline")
        await self.vector_store.initialize()
        logger.info("Advanced RAG Pipeline initialized successfully")
    
    async def process_document(self, filename: str, content: str, content_type: str = "text") -> DocumentInfo:
        """Process document with advanced features"""
        try:
            # Generate document ID
            doc_id = hashlib.md5(f"{filename}_{content[:100]}".encode()).hexdigest()
            
            # Extract enhanced metadata
            metadata = self._extract_enhanced_metadata(filename, content, content_type)
            metadata['document_id'] = doc_id
            
            # Process content with enhanced chunking
            chunks = await self._enhanced_chunking(content, content_type, metadata)
            
            # Create document info
            doc_info = DocumentInfo(
                id=doc_id,
                filename=filename,
                content_type=content_type,
                chunk_count=len(chunks),
                processing_status="completed",
                created_at=datetime.utcnow(),
                metadata=metadata
            )
            
            # Add to vector store (this will generate embeddings)
            await self.vector_store.add_document(doc_info, chunks)
            
            # Update stats
            self.processing_stats["documents_processed"] += 1
            self.processing_stats["chunks_created"] += len(chunks)
            self.processing_stats["embeddings_generated"] += len(chunks)
            
            logger.info(f"Advanced processing completed for {filename} ({len(chunks)} chunks)")
            return doc_info
            
        except Exception as e:
            self.processing_stats["processing_errors"] += 1
            logger.error(f"Advanced document processing failed for {filename}: {str(e)}")
            raise
    
    async def query(self, query_text: str, **kwargs) -> List[Dict[str, Any]]:
        """Advanced query with enhanced search capabilities"""
        start_time = datetime.utcnow()
        
        try:
            # Create search query
            search_query = SearchQuery(
                text=query_text,
                top_k=kwargs.get('top_k', 5),
                similarity_threshold=kwargs.get('similarity_threshold', 0.7),
                filters=kwargs.get('filters'),
                rerank=kwargs.get('rerank', False)
            )
            
            # Perform vector search
            results = await self.vector_store.search(search_query)
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "chunk_id": result.chunk_id,
                    "document_id": result.document_id,
                    "content": result.content,
                    "similarity_score": result.similarity_score,
                    "metadata": result.metadata,
                    "document_filename": self.vector_store.documents.get(result.document_id, {}).filename if result.document_id in self.vector_store.documents else "unknown"
                })
            
            # Log query
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.query_history.append({
                "query": query_text,
                "results_count": len(results),
                "processing_time": processing_time,
                "timestamp": start_time.isoformat(),
                "parameters": kwargs
            })
            
            self.processing_stats["queries_processed"] += 1
            
            logger.info(f"Advanced query processed: '{query_text}' -> {len(results)} results in {processing_time:.3f}s")
            return formatted_results
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.processing_stats["processing_errors"] += 1
            logger.error(f"Advanced query processing failed: {str(e)}")
            raise
    
    async def _enhanced_chunking(self, content: str, content_type: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Enhanced chunking with better strategies"""
        if content_type == "markdown":
            return await self._chunk_markdown_advanced(content, metadata)
        else:
            return self.processor.process_text(content, metadata)
    
    async def _chunk_markdown_advanced(self, content: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Advanced markdown chunking that preserves structure"""
        chunks = []
        doc_id = metadata.get('document_id', str(uuid.uuid4()))
        
        lines = content.split('\n')
        current_section = []
        current_header = ""
        chunk_index = 0
        
        for line in lines:
            if line.startswith('#'):
                # New header found, process previous section
                if current_section:
                    chunk_content = '\n'.join(current_section)
                    if chunk_content.strip():
                        chunk_metadata = metadata.copy()
                        chunk_metadata.update({
                            "section_header": current_header,
                            "chunk_type": "markdown_section"
                        })
                        
                        chunk = DocumentChunk(
                            id=f"{doc_id}_chunk_{chunk_index}",
                            document_id=doc_id,
                            content=chunk_content,
                            chunk_index=chunk_index,
                            metadata=chunk_metadata
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                
                # Start new section
                current_header = line
                current_section = [line]
            else:
                current_section.append(line)
        
        # Process final section
        if current_section:
            chunk_content = '\n'.join(current_section)
            if chunk_content.strip():
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "section_header": current_header,
                    "chunk_type": "markdown_section"
                })
                
                chunk = DocumentChunk(
                    id=f"{doc_id}_chunk_{chunk_index}",
                    document_id=doc_id,
                    content=chunk_content,
                    chunk_index=chunk_index,
                    metadata=chunk_metadata
                )
                chunks.append(chunk)
        
        return chunks
    
    def _extract_enhanced_metadata(self, filename: str, content: str, content_type: str) -> Dict[str, Any]:
        """Extract enhanced metadata from document"""
        metadata = {
            "filename": filename,
            "content_type": content_type,
            "character_count": len(content),
            "word_count": len(content.split()),
            "processed_at": datetime.utcnow().isoformat(),
            "language": self._detect_language(content),
            "has_code": self._detect_code_blocks(content),
            "estimated_reading_time": len(content.split()) / 200  # words per minute
        }
        
        if content_type == "markdown":
            metadata.update({
                "header_count": content.count('#'),
                "link_count": content.count('['),
                "code_block_count": content.count('```')
            })
        
        return metadata
    
    def _detect_language(self, content: str) -> str:
        """Simple language detection"""
        # Very basic detection - could be enhanced with proper language detection
        if any(word in content.lower() for word in ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to']):
            return "english"
        return "unknown"
    
    def _detect_code_blocks(self, content: str) -> bool:
        """Detect if content contains code blocks"""
        code_indicators = ['```', 'def ', 'class ', 'function', 'import ', 'from ', '<?php', '<script']
        return any(indicator in content for indicator in code_indicators)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive pipeline status"""
        vector_stats = self.vector_store.get_statistics()
        
        return {
            "status": "initialized",
            "processing_stats": self.processing_stats,
            "vector_store": vector_stats,
            "recent_queries": self.query_history[-5:] if self.query_history else [],
            "embedding_providers": self.embedding_manager.get_available_providers(),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.embedding_manager.cleanup()
        logger.info("Advanced RAG Pipeline cleanup completed") 