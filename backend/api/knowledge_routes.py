"""
Knowledge Graph and Adaptive Learning API Routes
Advanced intelligence features for today's update
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import datetime

from ..core.auth import get_current_user, get_current_admin_user
from ..core.database import User
from ..core.knowledge_graph import knowledge_graph, EntityType, RelationType
from ..core.adaptive_learning import adaptive_learning, LearningSignal, LearningEvent

logger = logging.getLogger(__name__)

# Create routers
knowledge_router = APIRouter(prefix="/knowledge", tags=["knowledge"])
learning_router = APIRouter(prefix="/learning", tags=["learning"])

# Request/Response models
class ProcessTextRequest(BaseModel):
    text: str
    source_id: str
    source_type: str = "document"

class KnowledgeQueryRequest(BaseModel):
    query: str
    limit: int = 10

class FeedbackRequest(BaseModel):
    feedback_type: str  # positive or negative
    context: Dict[str, Any]

class RecommendationRequest(BaseModel):
    context: Dict[str, Any]

# Knowledge Graph Routes
@knowledge_router.post("/process")
async def process_text_for_knowledge(
    request: ProcessTextRequest,
    current_user: User = Depends(get_current_user)
):
    """Process text and extract knowledge for the graph"""
    try:
        result = await knowledge_graph.process_text(
            text=request.text,
            source_id=request.source_id,
            source_type=request.source_type
        )
        
        return {
            "status": "success",
            "message": "Text processed successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Knowledge processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process text: {str(e)}"
        )

@knowledge_router.get("/graph")
async def get_knowledge_graph(current_user: User = Depends(get_current_user)):
    """Get the complete knowledge graph"""
    try:
        graph_data = await knowledge_graph.export_graph("json")
        
        return {
            "status": "success",
            "graph": graph_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get knowledge graph: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve knowledge graph"
        )

@knowledge_router.post("/search")
async def search_knowledge(
    request: KnowledgeQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Search the knowledge graph"""
    try:
        results = await knowledge_graph.query_knowledge(
            query=request.query,
            limit=request.limit
        )
        
        return {
            "status": "success",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Knowledge search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search knowledge"
        )

@knowledge_router.get("/entity/{entity_id}/neighbors")
async def get_entity_neighbors(
    entity_id: str,
    max_depth: int = 2,
    current_user: User = Depends(get_current_user)
):
    """Get neighboring entities for a specific entity"""
    try:
        neighbors = await knowledge_graph.get_entity_neighbors(
            entity_id=entity_id,
            max_depth=max_depth
        )
        
        return {
            "status": "success",
            "entity_id": entity_id,
            "neighbors": neighbors
        }
        
    except Exception as e:
        logger.error(f"Failed to get entity neighbors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get entity neighbors"
        )

@knowledge_router.get("/patterns")
async def discover_knowledge_patterns(current_user: User = Depends(get_current_user)):
    """Discover patterns and insights in the knowledge graph"""
    try:
        patterns = await knowledge_graph.discover_patterns()
        
        return {
            "status": "success",
            "patterns": patterns
        }
        
    except Exception as e:
        logger.error(f"Pattern discovery failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to discover patterns"
        )

@knowledge_router.get("/export")
async def export_knowledge_graph(
    format_type: str = "json",
    current_user: User = Depends(get_current_user)
):
    """Export knowledge graph in various formats"""
    try:
        exported_data = await knowledge_graph.export_graph(format_type)
        
        return {
            "status": "success",
            "format": format_type,
            "data": exported_data
        }
        
    except Exception as e:
        logger.error(f"Knowledge export failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export knowledge graph"
        )

@knowledge_router.get("/stats")
async def get_knowledge_stats(current_user: User = Depends(get_current_user)):
    """Get knowledge graph statistics"""
    try:
        stats = await knowledge_graph.get_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get knowledge stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get knowledge statistics"
        )

# Adaptive Learning Routes
@learning_router.post("/feedback")
async def provide_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user)
):
    """Provide learning feedback to the system"""
    try:
        await adaptive_learning.learn_from_feedback(
            user_id=current_user.id,
            feedback_type=request.feedback_type,
            context=request.context
        )
        
        return {
            "status": "success",
            "message": "Feedback recorded successfully"
        }
        
    except Exception as e:
        logger.error(f"Feedback recording failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record feedback"
        )

@learning_router.post("/recommendations")
async def get_user_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """Get personalized recommendations for the user"""
    try:
        recommendations = await adaptive_learning.get_user_recommendations(
            user_id=current_user.id,
            context=request.context
        )
        
        return {
            "status": "success",
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Recommendation generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )

@learning_router.get("/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get user learning profile"""
    try:
        profile = await adaptive_learning.export_user_profile(current_user.id)
        
        if not profile:
            # Return empty profile for new users
            return {
                "status": "success",
                "profile": {
                    "user_id": current_user.id,
                    "preferences": {},
                    "behavior_patterns": {},
                    "skill_level": {},
                    "total_interactions": 0,
                    "created_at": current_user.created_at.isoformat(),
                    "updated_at": current_user.created_at.isoformat(),
                    "recent_events": []
                }
            }
        
        return {
            "status": "success",
            "profile": profile
        }
        
    except Exception as e:
        logger.error(f"Failed to get user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@learning_router.get("/stats")
async def get_learning_stats(current_user: User = Depends(get_current_user)):
    """Get adaptive learning system statistics"""
    try:
        stats = await adaptive_learning.get_learning_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get learning stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get learning statistics"
        )

@learning_router.post("/event")
async def record_learning_event(
    signal_type: str,
    context: Dict[str, Any],
    outcome: Dict[str, Any] = {},
    confidence: float = 1.0,
    current_user: User = Depends(get_current_user)
):
    """Record a learning event"""
    try:
        # Validate signal type
        try:
            signal_enum = LearningSignal(signal_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid signal type: {signal_type}"
            )
        
        # Create learning event
        event = LearningEvent(
            id=f"event_{current_user.id}_{signal_type}_{int(datetime.utcnow().timestamp())}",
            user_id=current_user.id,
            signal_type=signal_enum,
            context=context,
            outcome=outcome,
            confidence=confidence
        )
        
        await adaptive_learning.record_learning_event(event)
        
        return {
            "status": "success",
            "message": "Learning event recorded successfully",
            "event_id": event.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record learning event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record learning event"
        )

@learning_router.get("/agent_selection/{task_type}")
async def get_adaptive_agent_selection(
    task_type: str,
    current_user: User = Depends(get_current_user)
):
    """Get adaptive agent selection for a task"""
    try:
        task_context = {
            "type": task_type,
            "user_id": current_user.id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        selected_agent = await adaptive_learning.adapt_agent_selection(
            user_id=current_user.id,
            task_context=task_context
        )
        
        return {
            "status": "success",
            "selected_agent": selected_agent,
            "task_type": task_type
        }
        
    except Exception as e:
        logger.error(f"Adaptive agent selection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to select agent adaptively"
        )

# Admin routes
@knowledge_router.get("/admin/entities")
async def list_all_entities(
    limit: int = 100,
    entity_type: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """List all entities in the knowledge graph (admin only)"""
    try:
        entities = list(knowledge_graph.entities.values())
        
        # Filter by type if specified
        if entity_type:
            entities = [e for e in entities if e.entity_type.value == entity_type]
        
        # Sort by confidence and limit
        entities.sort(key=lambda e: e.confidence, reverse=True)
        entities = entities[:limit]
        
        return {
            "status": "success",
            "total_entities": len(entities),
            "entities": [
                {
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.entity_type.value,
                    "confidence": entity.confidence,
                    "created_at": entity.created_at.isoformat(),
                    "source_references": list(entity.source_references)
                }
                for entity in entities
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to list entities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list entities"
        )

@learning_router.get("/admin/users")
async def list_learning_users(
    current_user: User = Depends(get_current_admin_user)
):
    """List all users in the adaptive learning system (admin only)"""
    try:
        user_profiles = list(adaptive_learning.user_profiles.values())
        
        return {
            "status": "success",
            "total_users": len(user_profiles),
            "users": [
                {
                    "user_id": profile.user_id,
                    "total_interactions": len(adaptive_learning.learning_events.get(profile.user_id, [])),
                    "preferences_count": len(profile.preferences),
                    "skill_areas": list(profile.skill_level.keys()),
                    "created_at": profile.created_at.isoformat(),
                    "updated_at": profile.updated_at.isoformat()
                }
                for profile in user_profiles
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to list learning users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list learning users"
        )

# Health checks
@knowledge_router.get("/health")
async def knowledge_health_check():
    """Knowledge graph system health check"""
    try:
        stats = await knowledge_graph.get_statistics()
        
        return {
            "status": "healthy",
            "knowledge_graph": {
                "status": "running",
                "entities": stats["total_entities"],
                "relationships": stats["total_relationships"],
                "last_update": stats["last_update"]
            }
        }
        
    except Exception as e:
        logger.error(f"Knowledge health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Knowledge graph system unhealthy"
        )

@learning_router.get("/health")
async def learning_health_check():
    """Adaptive learning system health check"""
    try:
        stats = await adaptive_learning.get_learning_statistics()
        
        return {
            "status": "healthy",
            "adaptive_learning": {
                "status": "running",
                "total_users": stats["total_users"],
                "total_events": stats["total_learning_events"],
                "success_rate": stats["adaptation_success_rate"],
                "last_update": stats["last_learning_update"]
            }
        }
        
    except Exception as e:
        logger.error(f"Learning health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Adaptive learning system unhealthy"
        ) 