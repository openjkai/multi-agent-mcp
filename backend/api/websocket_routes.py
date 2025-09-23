"""
WebSocket and AI API Routes - Real-time communication and AI reasoning endpoints
Advanced API routes for today's update
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from pydantic import BaseModel

from ..core.auth import get_current_user, get_optional_user
from ..core.database import User
from ..core.real_time_engine import real_time_engine, RealTimeEvent, EventType
from ..core.ai_orchestrator import ai_orchestrator, ReasoningType

logger = logging.getLogger(__name__)

# Create routers
websocket_router = APIRouter()
ai_router = APIRouter(prefix="/ai", tags=["ai"])

# Request/Response models for AI endpoints
class ReasoningRequest(BaseModel):
    task: str
    reasoning_type: str = "chain_of_thought"
    context: Dict[str, Any] = {}
    requirements: Dict[str, Any] = {}

class TaskDecompositionRequest(BaseModel):
    task: str
    context: Dict[str, Any] = {}

class ReasoningChainResponse(BaseModel):
    chain_id: str
    task: str
    reasoning_type: str
    steps: list
    final_result: Dict[str, Any]
    overall_confidence: float
    total_processing_time: float
    models_used: list
    created_at: str

# WebSocket endpoints
@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication"""
    await real_time_engine.handle_websocket(websocket)

@websocket_router.websocket("/ws/{user_id}")
async def websocket_endpoint_with_user(websocket: WebSocket, user_id: str):
    """WebSocket endpoint with user identification"""
    await real_time_engine.handle_websocket(websocket, user_id)

# AI Reasoning endpoints
@ai_router.post("/reasoning", response_model=ReasoningChainResponse)
async def create_reasoning_chain(
    request: ReasoningRequest,
    current_user: User = Depends(get_current_user)
):
    """Create and execute an AI reasoning chain"""
    try:
        # Validate reasoning type
        try:
            reasoning_type_enum = ReasoningType(request.reasoning_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid reasoning type: {request.reasoning_type}"
            )
        
        # Create reasoning chain
        chain = await ai_orchestrator.process_complex_task(
            task=request.task,
            reasoning_type=reasoning_type_enum,
            context=request.context,
            requirements=request.requirements
        )
        
        # Emit real-time event
        await real_time_engine.emit_event(RealTimeEvent(
            id=f"reasoning_{chain.chain_id}",
            type=EventType.SYSTEM_ALERT,
            data={
                "message": f"Reasoning chain completed: {request.task[:50]}...",
                "chain_id": chain.chain_id,
                "confidence": chain.overall_confidence,
                "processing_time": chain.total_processing_time
            },
            user_id=current_user.id
        ))
        
        # Convert to response format
        return ReasoningChainResponse(
            chain_id=chain.chain_id,
            task=chain.task,
            reasoning_type=chain.reasoning_type.value,
            steps=[
                {
                    "step_id": step.step_id,
                    "description": step.description,
                    "input_data": step.input_data,
                    "output_data": step.output_data,
                    "confidence": step.confidence,
                    "model_used": step.model_used,
                    "processing_time": step.processing_time,
                    "reasoning_type": step.reasoning_type.value,
                    "created_at": step.created_at.isoformat()
                }
                for step in chain.steps
            ],
            final_result=chain.final_result,
            overall_confidence=chain.overall_confidence,
            total_processing_time=chain.total_processing_time,
            models_used=chain.models_used,
            created_at=chain.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Reasoning chain creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reasoning chain: {str(e)}"
        )

@ai_router.get("/reasoning/{chain_id}")
async def get_reasoning_chain(
    chain_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific reasoning chain"""
    try:
        chain = await ai_orchestrator.get_reasoning_chain(chain_id)
        
        if not chain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reasoning chain not found"
            )
        
        return ReasoningChainResponse(
            chain_id=chain.chain_id,
            task=chain.task,
            reasoning_type=chain.reasoning_type.value,
            steps=[
                {
                    "step_id": step.step_id,
                    "description": step.description,
                    "input_data": step.input_data,
                    "output_data": step.output_data,
                    "confidence": step.confidence,
                    "model_used": step.model_used,
                    "processing_time": step.processing_time,
                    "reasoning_type": step.reasoning_type.value,
                    "created_at": step.created_at.isoformat()
                }
                for step in chain.steps
            ],
            final_result=chain.final_result,
            overall_confidence=chain.overall_confidence,
            total_processing_time=chain.total_processing_time,
            models_used=chain.models_used,
            created_at=chain.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get reasoning chain: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reasoning chain"
        )

@ai_router.get("/reasoning")
async def list_reasoning_chains(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """List user's reasoning chains"""
    try:
        # In a full implementation, this would filter by user
        # For now, return all chains
        chains = list(ai_orchestrator.reasoning_chains.values())[-limit:]
        
        return [
            {
                "chain_id": chain.chain_id,
                "task": chain.task,
                "reasoning_type": chain.reasoning_type.value,
                "overall_confidence": chain.overall_confidence,
                "total_processing_time": chain.total_processing_time,
                "steps_count": len(chain.steps),
                "created_at": chain.created_at.isoformat()
            }
            for chain in reversed(chains)
        ]
        
    except Exception as e:
        logger.error(f"Failed to list reasoning chains: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list reasoning chains"
        )

@ai_router.post("/decompose")
async def decompose_task(
    request: TaskDecompositionRequest,
    current_user: User = Depends(get_current_user)
):
    """Decompose a complex task into subtasks"""
    try:
        # Create task decomposition
        decomposition = await ai_orchestrator._decompose_task(
            task=request.task,
            context=request.context
        )
        
        # Emit real-time event
        await real_time_engine.emit_event(RealTimeEvent(
            id=f"decomposition_{decomposition.task_id}",
            type=EventType.SYSTEM_ALERT,
            data={
                "message": f"Task decomposed: {request.task[:50]}...",
                "task_id": decomposition.task_id,
                "subtasks_count": len(decomposition.subtasks),
                "complexity": decomposition.estimated_complexity
            },
            user_id=current_user.id
        ))
        
        return {
            "task_id": decomposition.task_id,
            "original_task": decomposition.original_task,
            "subtasks": decomposition.subtasks,
            "dependencies": decomposition.dependencies,
            "execution_order": decomposition.execution_order,
            "estimated_complexity": decomposition.estimated_complexity,
            "created_at": decomposition.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Task decomposition failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decompose task: {str(e)}"
        )

@ai_router.get("/decompositions/{task_id}")
async def get_task_decomposition(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific task decomposition"""
    try:
        decomposition = await ai_orchestrator.get_task_decomposition(task_id)
        
        if not decomposition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task decomposition not found"
            )
        
        return {
            "task_id": decomposition.task_id,
            "original_task": decomposition.original_task,
            "subtasks": decomposition.subtasks,
            "dependencies": decomposition.dependencies,
            "execution_order": decomposition.execution_order,
            "estimated_complexity": decomposition.estimated_complexity,
            "created_at": decomposition.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task decomposition: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task decomposition"
        )

@ai_router.get("/models")
async def get_available_models():
    """Get available AI models and their capabilities"""
    try:
        from ..core.ai_orchestrator import ModelProvider
        
        model_info = {}
        for provider in ModelProvider:
            model_info[provider.value] = {
                "name": provider.value,
                "capabilities": ai_orchestrator.model_router.model_capabilities.get(provider, {}),
                "available": True  # In a real implementation, check actual availability
            }
        
        return {
            "models": model_info,
            "reasoning_types": [
                {
                    "value": rt.value,
                    "name": rt.value.replace("_", " ").title(),
                    "description": ai_orchestrator.prompt_builder.templates.get(rt).__doc__ or "Advanced reasoning approach"
                }
                for rt in ReasoningType
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get model information: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve model information"
        )

@ai_router.get("/stats")
async def get_ai_stats(current_user: User = Depends(get_current_user)):
    """Get AI orchestrator performance statistics"""
    try:
        stats = ai_orchestrator.get_performance_stats()
        
        return {
            "ai_orchestrator": stats,
            "real_time_engine": real_time_engine.get_statistics(),
            "timestamp": "2024-12-01T00:00:00Z"  # Current timestamp
        }
        
    except Exception as e:
        logger.error(f"Failed to get AI stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AI statistics"
        )

# Real-time event emission endpoints
@ai_router.post("/events/emit")
async def emit_real_time_event(
    event_type: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    room: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Emit a custom real-time event (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Validate event type
        try:
            event_type_enum = EventType(event_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type: {event_type}"
            )
        
        # Create and emit event
        event = RealTimeEvent(
            id=f"custom_{int(time.time())}",
            type=event_type_enum,
            data=data,
            user_id=user_id,
            room=room
        )
        
        await real_time_engine.emit_event(event)
        
        return {"message": "Event emitted successfully", "event_id": event.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to emit event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to emit event"
        )

@ai_router.get("/events/stats")
async def get_real_time_stats():
    """Get real-time engine statistics"""
    try:
        stats = real_time_engine.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get real-time stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve real-time statistics"
        )

# Health check endpoints
@ai_router.get("/health")
async def ai_health_check():
    """AI system health check"""
    try:
        ai_stats = ai_orchestrator.get_performance_stats()
        rt_stats = real_time_engine.get_statistics()
        
        return {
            "status": "healthy",
            "ai_orchestrator": {
                "status": "running",
                "total_tasks": ai_stats["total_tasks"],
                "success_rate": ai_stats["success_rate"]
            },
            "real_time_engine": {
                "status": "running" if real_time_engine.is_running else "stopped",
                "connections": rt_stats["connections"]["total"],
                "events_sent": rt_stats["events"]["sent"]
            }
        }
        
    except Exception as e:
        logger.error(f"AI health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI system unhealthy"
        ) 