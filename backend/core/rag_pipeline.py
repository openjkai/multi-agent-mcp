"""
RAG Pipeline - Document processing, embedding, and retrieval system
Advanced RAG implementation for today's major update
"""

import logging
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Individual document chunk for RAG"""
    id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: Dict[str, Any]
    created_at: datetime

@dataclass
class DocumentInfo:
    """Information about a processed document"""
    id: str
    filename: str
    file_size: int
    content_type: str
    chunk_count: int
    processing_status: str
    uploaded_at: datetime
    processed_at: Optional[datetime]
    metadata: Dict[str, Any]

class DocumentProcessor:
    """Handles document processing and chunking"""
    
    def __init__(self):
        self.supported_formats = ['.txt', '.md', '.pdf', '.docx']
        self.max_chunk_size = 1000
        self.chunk_overlap = 200
    
    def can_process(self, filename: str) -> bool:
        """Check if file format is supported"""
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats)
    
    def process_text(self, content: str, filename: str) -> List[DocumentChunk]:
        """Process text content into chunks"""
        chunks = []
        words = content.split()
        
        for i in range(0, len(words), self.max_chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.max_chunk_size]
            chunk_content = ' '.join(chunk_words)
            
            if chunk_content.strip():
                chunk = DocumentChunk(
                    id=f"{filename}_{i}_{hashlib.md5(chunk_content.encode()).hexdigest()[:8]}",
                    document_id=filename,
                    content=chunk_content,
                    chunk_index=i // (self.max_chunk_size - self.chunk_overlap),
                    metadata={
                        "word_count": len(chunk_words),
                        "char_count": len(chunk_content),
                        "chunk_type": "text"
                    },
                    created_at=datetime.utcnow()
                )
                chunks.append(chunk)
        
        return chunks
    
    def process_markdown(self, content: str, filename: str) -> List[DocumentChunk]:
        """Process markdown content with structure preservation"""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_chunk_size = 0
        
        for line in lines:
            line_size = len(line)
            
            # Start new chunk if current is getting too large
            if current_chunk_size + line_size > self.max_chunk_size and current_chunk:
                chunk_content = '\n'.join(current_chunk)
                chunk = DocumentChunk(
                    id=f"{filename}_{len(chunks)}_{hashlib.md5(chunk_content.encode()).hexdigest()[:8]}",
                    document_id=filename,
                    content=chunk_content,
                    chunk_index=len(chunks),
                    metadata={
                        "word_count": len(chunk_content.split()),
                        "char_count": len(chunk_content),
                        "chunk_type": "markdown",
                        "has_headers": any(line.startswith('#') for line in current_chunk)
                    },
                    created_at=datetime.utcnow()
                )
                chunks.append(chunk)
                current_chunk = [line]
                current_chunk_size = line_size
            else:
                current_chunk.append(line)
                current_chunk_size += line_size
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunk = DocumentChunk(
                id=f"{filename}_{len(chunks)}_{hashlib.md5(chunk_content.encode()).hexdigest()[:8]}",
                document_id=filename,
                content=chunk_content,
                chunk_index=len(chunks),
                metadata={
                    "word_count": len(chunk_content.split()),
                    "char_count": len(chunk_content),
                    "chunk_type": "markdown",
                    "has_headers": any(line.startswith('#') for line in current_chunk)
                },
                created_at=datetime.utcnow()
            )
            chunks.append(chunk)
        
        return chunks

class VectorStore:
    """Simple in-memory vector store for today's implementation"""
    
    def __init__(self):
        self.documents: Dict[str, DocumentInfo] = {}
        self.chunks: Dict[str, DocumentChunk] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self.search_index: Dict[str, List[str]] = {}  # word -> chunk_ids
    
    async def add_document(self, doc_info: DocumentInfo, chunks: List[DocumentChunk]):
        """Add document and chunks to the store"""
        # Store document info
        self.documents[doc_info.id] = doc_info
        
        # Store chunks
        for chunk in chunks:
            self.chunks[chunk.id] = chunk
            
            # Simple word-based indexing (will be replaced with real embeddings tomorrow)
            words = chunk.content.lower().split()
            for word in words:
                if word not in self.search_index:
                    self.search_index[word] = []
                if chunk.id not in self.search_index[word]:
                    self.search_index[word].append(chunk.id)
        
        logger.info(f"Added document {doc_info.id} with {len(chunks)} chunks")
    
    async def search(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Search for relevant chunks"""
        query_words = query.lower().split()
        chunk_scores = {}
        
        # Simple TF-IDF like scoring
        for word in query_words:
            if word in self.search_index:
                for chunk_id in self.search_index[word]:
                    if chunk_id not in chunk_scores:
                        chunk_scores[chunk_id] = 0
                    chunk_scores[chunk_id] += 1
        
        # Sort by score and return top results
        sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for chunk_id, score in sorted_chunks[:top_k]:
            if chunk_id in self.chunks:
                chunk = self.chunks[chunk_id]
                # Normalize score
                normalized_score = min(score / len(query_words), 1.0)
                results.append((chunk, normalized_score))
        
        return results
    
    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a document"""
        return [chunk for chunk in self.chunks.values() if chunk.document_id == document_id]
    
    def get_store_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "total_embeddings": len(self.embeddings),
            "indexed_words": len(self.search_index)
        }

class RAGPipeline:
    """Main RAG pipeline orchestrator"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.processing_queue: List[Dict] = []
        self.processing_stats = {
            "documents_processed": 0,
            "total_chunks_created": 0,
            "processing_errors": 0
        }
    
    async def initialize(self):
        """Initialize the RAG pipeline"""
        logger.info("Initializing RAG Pipeline")
        # Future: Initialize real vector store, embedding models, etc.
        logger.info("RAG Pipeline initialized successfully")
    
    async def process_document(self, filename: str, content: str, content_type: str = "text") -> DocumentInfo:
        """Process a document and add it to the vector store"""
        try:
            # Generate document ID
            doc_id = f"{filename}_{hashlib.md5(content.encode()).hexdigest()[:16]}"
            
            # Create document info
            doc_info = DocumentInfo(
                id=doc_id,
                filename=filename,
                file_size=len(content.encode()),
                content_type=content_type,
                chunk_count=0,
                processing_status="processing",
                uploaded_at=datetime.utcnow(),
                processed_at=None,
                metadata={"original_filename": filename}
            )
            
            # Process content into chunks
            if content_type == "markdown":
                chunks = self.processor.process_markdown(content, filename)
            else:
                chunks = self.processor.process_text(content, filename)
            
            # Update document info
            doc_info.chunk_count = len(chunks)
            doc_info.processing_status = "completed"
            doc_info.processed_at = datetime.utcnow()
            
            # Add to vector store
            await self.vector_store.add_document(doc_info, chunks)
            
            # Update stats
            self.processing_stats["documents_processed"] += 1
            self.processing_stats["total_chunks_created"] += len(chunks)
            
            logger.info(f"Successfully processed document {filename} into {len(chunks)} chunks")
            return doc_info
            
        except Exception as e:
            self.processing_stats["processing_errors"] += 1
            logger.error(f"Error processing document {filename}: {e}")
            raise
    
    async def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query the RAG system"""
        try:
            # Search for relevant chunks
            results = await self.vector_store.search(query, top_k)
            
            # Format results
            formatted_results = []
            for chunk, score in results:
                # Get document info
                doc_info = self.vector_store.documents.get(chunk.document_id)
                
                formatted_results.append({
                    "chunk_id": chunk.id,
                    "content": chunk.content,
                    "similarity_score": score,
                    "document_info": {
                        "id": doc_info.id if doc_info else "unknown",
                        "filename": doc_info.filename if doc_info else "unknown",
                        "chunk_index": chunk.chunk_index
                    },
                    "metadata": chunk.metadata
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get RAG pipeline status"""
        return {
            "status": "running",
            "processing_stats": self.processing_stats,
            "vector_store_stats": self.vector_store.get_store_stats(),
            "supported_formats": self.processor.supported_formats
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("RAG Pipeline cleanup completed") 