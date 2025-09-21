"""
Workflow API Routes - Multi-agent workflow orchestration endpoints
Enterprise workflow management API for 3-day development plan
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel, validator

from ..core.auth import get_current_user, get_current_admin_user
from ..core.database import db_manager, User
from ..core.workflow_engine import (
    get_workflow_engine, 
    WorkflowTemplate, 
    Workflow, 
    Task, 
    WorkflowStatus,
    TaskStatus
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Request/Response Models
class TaskRequest(BaseModel):
    name: str
    agent_type: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str] = []
    timeout: int = 300
    max_retries: int = 3

class WorkflowRequest(BaseModel):
    name: str
    description: str
    tasks: List[TaskRequest]
    metadata: Dict[str, Any] = {}

class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    created_by: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress: Dict[str, Any]
    metadata: Dict[str, Any]

class TaskResponse(BaseModel):
    id: str
    name: str
    agent_type: str
    action: str
    status: str
    dependencies: List[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time: Optional[float]
    result: Optional[Any]
    error: Optional[str]

class WorkflowTemplateRequest(BaseModel):
    template_type: str
    parameters: Dict[str, Any]
    
    @validator('template_type')
    def validate_template_type(cls, v):
        valid_types = ['document_analysis', 'research', 'code_review']
        if v not in valid_types:
            raise ValueError(f'Template type must be one of: {valid_types}')
        return v

# Workflow Management Routes
@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new workflow"""
    try:
        workflow_engine = get_workflow_engine()
        
        # Convert request to workflow object
        tasks = []
        for i, task_req in enumerate(workflow_data.tasks):
            task = Task(
                id=f"task_{i}_{task_req.name.lower().replace(' ', '_')}",
                name=task_req.name,
                agent_type=task_req.agent_type,
                action=task_req.action,
                parameters=task_req.parameters,
                dependencies=task_req.dependencies,
                timeout=task_req.timeout,
                max_retries=task_req.max_retries
            )
            tasks.append(task)
        
        workflow = Workflow(
            id=f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{current_user.username}",
            name=workflow_data.name,
            description=workflow_data.description,
            tasks=tasks,
            created_by=current_user.id,
            metadata=workflow_data.metadata
        )
        
        # Create workflow
        workflow_id = await workflow_engine.create_workflow(workflow)
        
        # Get workflow status
        status_data = workflow_engine.get_workflow_status(workflow_id)
        
        logger.info(f"Workflow created: {workflow.name} by {current_user.username}")
        
        return WorkflowResponse(
            id=status_data["id"],
            name=status_data["name"],
            description=workflow.description,
            status=status_data["status"],
            created_by=current_user.id,
            created_at=datetime.fromisoformat(status_data["created_at"]),
            started_at=datetime.fromisoformat(status_data["started_at"]) if status_data["started_at"] else None,
            completed_at=datetime.fromisoformat(status_data["completed_at"]) if status_data["completed_at"] else None,
            progress=status_data["progress"],
            metadata=status_data["metadata"]
        )
        
    except Exception as e:
        logger.error(f"Workflow creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )

@router.post("/templates", response_model=WorkflowResponse)
async def create_workflow_from_template(
    template_data: WorkflowTemplateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create workflow from predefined template"""
    try:
        workflow_engine = get_workflow_engine()
        
        # Create workflow from template
        if template_data.template_type == "document_analysis":
            workflow = WorkflowTemplate.document_analysis_workflow(
                document_id=template_data.parameters.get("document_id"),
                user_id=current_user.id
            )
        elif template_data.template_type == "research":
            workflow = WorkflowTemplate.research_workflow(
                query=template_data.parameters.get("query"),
                user_id=current_user.id
            )
        elif template_data.template_type == "code_review":
            workflow = WorkflowTemplate.code_review_workflow(
                code=template_data.parameters.get("code"),
                language=template_data.parameters.get("language"),
                user_id=current_user.id
            )
        else:
            raise ValueError(f"Unknown template type: {template_data.template_type}")
        
        # Create workflow
        workflow_id = await workflow_engine.create_workflow(workflow)
        
        # Get workflow status
        status_data = workflow_engine.get_workflow_status(workflow_id)
        
        logger.info(f"Workflow created from template: {template_data.template_type} by {current_user.username}")
        
        return WorkflowResponse(
            id=status_data["id"],
            name=status_data["name"],
            description=workflow.description,
            status=status_data["status"],
            created_by=current_user.id,
            created_at=datetime.fromisoformat(status_data["created_at"]),
            started_at=datetime.fromisoformat(status_data["started_at"]) if status_data["started_at"] else None,
            completed_at=datetime.fromisoformat(status_data["completed_at"]) if status_data["completed_at"] else None,
            progress=status_data["progress"],
            metadata=status_data["metadata"]
        )
        
    except Exception as e:
        logger.error(f"Template workflow creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow from template: {str(e)}"
        )

@router.post("/{workflow_id}/start")
async def start_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Start workflow execution"""
    try:
        workflow_engine = get_workflow_engine()
        
        # Check if workflow exists and user has access
        status_data = workflow_engine.get_workflow_status(workflow_id)
        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Start workflow
        success = await workflow_engine.start_workflow(workflow_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to start workflow"
            )
        
        logger.info(f"Workflow started: {workflow_id} by {current_user.username}")
        
        return {"message": "Workflow started successfully", "workflow_id": workflow_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow start failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}"
        )

@router.post("/{workflow_id}/cancel")
async def cancel_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel workflow execution"""
    try:
        workflow_engine = get_workflow_engine()
        
        # Check if workflow exists
        status_data = workflow_engine.get_workflow_status(workflow_id)
        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Cancel workflow
        success = await workflow_engine.cancel_workflow(workflow_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel workflow"
            )
        
        logger.info(f"Workflow cancelled: {workflow_id} by {current_user.username}")
        
        return {"message": "Workflow cancelled successfully", "workflow_id": workflow_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow cancellation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel workflow: {str(e)}"
        )

# Workflow Query Routes
@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    status_filter: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """List user's workflows"""
    try:
        workflow_engine = get_workflow_engine()
        
        # Parse status filter
        status_enum = None
        if status_filter:
            try:
                status_enum = WorkflowStatus(status_filter)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status filter: {status_filter}"
                )
        
        # Get workflows
        workflows_data = workflow_engine.list_workflows(status_enum)
        
        # Filter by user (non-admin users only see their own workflows)
        if not current_user.is_admin:
            # In a real implementation, you'd filter by created_by
            # For now, we'll return all workflows
            pass
        
        # Limit results
        workflows_data = workflows_data[:limit]
        
        # Convert to response format
        workflows = []
        for workflow_data in workflows_data:
            workflows.append(WorkflowResponse(
                id=workflow_data["id"],
                name=workflow_data["name"],
                description="",  # Would need to get from workflow object
                status=workflow_data["status"],
                created_by=workflow_data.get("created_by"),
                created_at=datetime.fromisoformat(workflow_data["created_at"]),
                started_at=datetime.fromisoformat(workflow_data["started_at"]) if workflow_data["started_at"] else None,
                completed_at=datetime.fromisoformat(workflow_data["completed_at"]) if workflow_data["completed_at"] else None,
                progress=workflow_data["progress"],
                metadata=workflow_data["metadata"]
            ))
        
        return workflows
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow listing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get workflow details"""
    try:
        workflow_engine = get_workflow_engine()
        
        # Get workflow status
        status_data = workflow_engine.get_workflow_status(workflow_id)
        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        return WorkflowResponse(
            id=status_data["id"],
            name=status_data["name"],
            description="",  # Would need to get from workflow object
            status=status_data["status"],
            created_by=status_data.get("created_by"),
            created_at=datetime.fromisoformat(status_data["created_at"]),
            started_at=datetime.fromisoformat(status_data["started_at"]) if status_data["started_at"] else None,
            completed_at=datetime.fromisoformat(status_data["completed_at"]) if status_data["completed_at"] else None,
            progress=status_data["progress"],
            metadata=status_data["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow: {str(e)}"
        )

@router.get("/{workflow_id}/tasks", response_model=List[TaskResponse])
async def get_workflow_tasks(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get workflow tasks"""
    try:
        workflow_engine = get_workflow_engine()
        
        # Get workflow
        workflow = workflow_engine.active_workflows.get(workflow_id) or workflow_engine.completed_workflows.get(workflow_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Convert tasks to response format
        tasks = []
        for task in workflow.tasks:
            tasks.append(TaskResponse(
                id=task.id,
                name=task.name,
                agent_type=task.agent_type,
                action=task.action,
                status=task.status.value,
                dependencies=task.dependencies,
                created_at=task.created_at,
                started_at=task.started_at,
                completed_at=task.completed_at,
                execution_time=task.result.execution_time if task.result else None,
                result=task.result.result if task.result else None,
                error=task.result.error if task.result else None
            ))
        
        return tasks
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow tasks retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow tasks: {str(e)}"
        )

# Analytics Routes
@router.get("/analytics/summary")
async def get_workflow_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get workflow analytics summary"""
    try:
        workflow_engine = get_workflow_engine()
        
        # Get all workflows
        all_workflows = workflow_engine.list_workflows()
        
        # Calculate analytics
        total_workflows = len(all_workflows)
        completed_workflows = len([w for w in all_workflows if w["status"] == "completed"])
        failed_workflows = len([w for w in all_workflows if w["status"] == "failed"])
        running_workflows = len([w for w in all_workflows if w["status"] == "running"])
        
        # Calculate success rate
        success_rate = (completed_workflows / total_workflows * 100) if total_workflows > 0 else 0
        
        # Calculate average execution time for completed workflows
        completed_times = []
        for workflow in all_workflows:
            if workflow["status"] == "completed" and workflow["completed_at"] and workflow["started_at"]:
                start_time = datetime.fromisoformat(workflow["started_at"])
                end_time = datetime.fromisoformat(workflow["completed_at"])
                execution_time = (end_time - start_time).total_seconds()
                completed_times.append(execution_time)
        
        avg_execution_time = sum(completed_times) / len(completed_times) if completed_times else 0
        
        return {
            "total_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "failed_workflows": failed_workflows,
            "running_workflows": running_workflows,
            "success_rate": round(success_rate, 2),
            "average_execution_time": round(avg_execution_time, 2),
            "workflows_by_status": {
                "created": len([w for w in all_workflows if w["status"] == "created"]),
                "running": running_workflows,
                "completed": completed_workflows,
                "failed": failed_workflows,
                "cancelled": len([w for w in all_workflows if w["status"] == "cancelled"])
            }
        }
        
    except Exception as e:
        logger.error(f"Workflow analytics failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow analytics: {str(e)}"
        )

# Template Information Routes
@router.get("/templates/list")
async def list_workflow_templates():
    """List available workflow templates"""
    return {
        "templates": [
            {
                "type": "document_analysis",
                "name": "Document Analysis Pipeline",
                "description": "Complete document processing and analysis workflow",
                "required_parameters": ["document_id"],
                "estimated_duration": "5-10 minutes"
            },
            {
                "type": "research",
                "name": "Research Pipeline",
                "description": "Comprehensive research using multiple agents",
                "required_parameters": ["query"],
                "estimated_duration": "10-15 minutes"
            },
            {
                "type": "code_review",
                "name": "Code Review Pipeline",
                "description": "Comprehensive code review and analysis",
                "required_parameters": ["code", "language"],
                "estimated_duration": "3-7 minutes"
            }
        ]
    }

# Health Check
@router.get("/health")
async def workflow_health_check():
    """Workflow system health check"""
    try:
        workflow_engine = get_workflow_engine()
        
        active_count = len(workflow_engine.active_workflows)
        completed_count = len(workflow_engine.completed_workflows)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "active_workflows": active_count,
            "completed_workflows": completed_count,
            "max_concurrent_workflows": workflow_engine.max_concurrent_workflows,
            "max_concurrent_tasks": workflow_engine.max_concurrent_tasks
        }
        
    except Exception as e:
        logger.error(f"Workflow health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Workflow system unhealthy"
        ) 