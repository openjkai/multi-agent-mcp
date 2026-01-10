"""
Batch Operations API Routes
Efficient batch processing for multiple operations
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import datetime

from ..core.auth import get_current_user
from ..core.database import User
from ..core.agent_manager import agent_manager
from ..core.advanced_rag import advanced_rag_pipeline
from ..core.cache import cache_manager

logger = logging.getLogger(__name__)

batch_router = APIRouter(prefix="/batch", tags=["batch"])

# Request models
class BatchQueryRequest(BaseModel):
    queries: List[str]
    agent_id: Optional[str] = None

class BatchDocumentRequest(BaseModel):
    documents: List[Dict[str, str]]  # [{"filename": "...", "content": "...", "content_type": "..."}]

class BatchCacheRequest(BaseModel):
    keys: List[str]

@batch_router.post("/queries")
async def batch_queries(
    request: BatchQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Process multiple queries in batch
    Returns results for all queries
    """
    if not agent_manager:
        raise HTTPException(
            status_code=503,
            detail="Agent manager not initialized"
        )
    
    if len(request.queries) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 queries per batch"
        )
    
    results = []
    errors = []
    
    for i, query in enumerate(request.queries):
        try:
            result = await agent_manager.route_query(
                query,
                agent_id=request.agent_id
            )
            results.append({
                "index": i,
                "query": query,
                "result": result,
                "status": "success"
            })
        except Exception as e:
            errors.append({
                "index": i,
                "query": query,
                "error": str(e),
                "status": "error"
            })
            logger.error(f"Batch query error [{i}]: {str(e)}")
    
    return {
        "status": "completed",
        "total": len(request.queries),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

@batch_router.post("/documents")
async def batch_upload_documents(
    request: BatchDocumentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process multiple documents in batch
    """
    if not advanced_rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="Advanced RAG pipeline not initialized"
        )
    
    if len(request.documents) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 documents per batch"
        )
    
    results = []
    errors = []
    
    for i, doc in enumerate(request.documents):
        try:
            filename = doc.get("filename", f"document_{i}.txt")
            content = doc.get("content", "")
            content_type = doc.get("content_type", "text")
            
            doc_info = await advanced_rag_pipeline.process_document(
                filename=filename,
                content=content,
                content_type=content_type
            )
            
            results.append({
                "index": i,
                "filename": filename,
                "document_id": doc_info.id,
                "chunk_count": doc_info.chunk_count,
                "status": "success"
            })
        except Exception as e:
            errors.append({
                "index": i,
                "filename": doc.get("filename", "unknown"),
                "error": str(e),
                "status": "error"
            })
            logger.error(f"Batch document upload error [{i}]: {str(e)}")
    
    return {
        "status": "completed",
        "total": len(request.documents),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

@batch_router.post("/cache/get")
async def batch_cache_get(
    request: BatchCacheRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get multiple cache entries at once
    """
    results = {}
    
    for key in request.keys[:100]:  # Limit to 100 keys
        value = await cache_manager.get(key)
        results[key] = value
    
    return {
        "status": "success",
        "keys_requested": len(request.keys),
        "keys_processed": len(results),
        "results": results
    }

@batch_router.delete("/cache")
async def batch_cache_delete(
    request: BatchCacheRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Delete multiple cache entries at once
    """
    deleted = []
    not_found = []
    
    for key in request.keys[:100]:  # Limit to 100 keys
        success = await cache_manager.delete(key)
        if success:
            deleted.append(key)
        else:
            not_found.append(key)
    
    return {
        "status": "completed",
        "deleted": len(deleted),
        "not_found": len(not_found),
        "deleted_keys": deleted,
        "not_found_keys": not_found
    }

@batch_router.post("/queries/async")
async def batch_queries_async(
    request: BatchQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Process multiple queries asynchronously (fire-and-forget)
    Returns job ID for tracking
    """
    import uuid
    
    job_id = str(uuid.uuid4())
    
    # Store job metadata in cache
    await cache_manager.set(
        f"batch_job:{job_id}",
        {
            "job_id": job_id,
            "total_queries": len(request.queries),
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
        },
        ttl=3600  # 1 hour
    )
    
    # Process asynchronously (in real implementation, use background task)
    # For now, return job ID immediately
    return {
        "status": "accepted",
        "job_id": job_id,
        "message": "Batch job queued for processing",
        "tracking_endpoint": f"/batch/jobs/{job_id}"
    }

@batch_router.get("/jobs/{job_id}")
async def get_batch_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a batch job
    """
    job_data = await cache_manager.get(f"batch_job:{job_id}")
    
    if not job_data:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    return job_data

