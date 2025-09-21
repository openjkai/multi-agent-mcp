"""
Workflow Engine - Advanced multi-agent collaboration system
Enterprise workflow orchestration for 3-day development plan
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"

class WorkflowStatus(Enum):
    """Workflow execution status"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

@dataclass
class TaskResult:
    """Result of task execution"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Task:
    """Individual task in a workflow"""
    id: str
    name: str
    agent_type: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300  # 5 minutes default
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class Workflow:
    """Workflow definition and execution state"""
    id: str
    name: str
    description: str
    tasks: List[Task]
    status: WorkflowStatus = WorkflowStatus.CREATED
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

class WorkflowTemplate:
    """Predefined workflow templates"""
    
    @staticmethod
    def document_analysis_workflow(document_id: str, user_id: str) -> Workflow:
        """Create document analysis workflow"""
        workflow_id = str(uuid4())
        
        tasks = [
            Task(
                id=f"{workflow_id}_extract",
                name="Extract Document Content",
                agent_type="document",
                action="extract_content",
                parameters={"document_id": document_id}
            ),
            Task(
                id=f"{workflow_id}_chunk",
                name="Chunk Document",
                agent_type="document",
                action="create_chunks",
                parameters={"document_id": document_id},
                dependencies=[f"{workflow_id}_extract"]
            ),
            Task(
                id=f"{workflow_id}_embed",
                name="Generate Embeddings",
                agent_type="document",
                action="generate_embeddings",
                parameters={"document_id": document_id},
                dependencies=[f"{workflow_id}_chunk"]
            ),
            Task(
                id=f"{workflow_id}_analyze",
                name="Analyze Content",
                agent_type="document",
                action="analyze_content",
                parameters={"document_id": document_id},
                dependencies=[f"{workflow_id}_embed"]
            ),
            Task(
                id=f"{workflow_id}_summarize",
                name="Generate Summary",
                agent_type="document",
                action="summarize",
                parameters={"document_id": document_id},
                dependencies=[f"{workflow_id}_analyze"]
            )
        ]
        
        return Workflow(
            id=workflow_id,
            name="Document Analysis Pipeline",
            description="Complete document processing and analysis",
            tasks=tasks,
            created_by=user_id,
            metadata={"document_id": document_id}
        )
    
    @staticmethod
    def research_workflow(query: str, user_id: str) -> Workflow:
        """Create research workflow combining multiple agents"""
        workflow_id = str(uuid4())
        
        tasks = [
            Task(
                id=f"{workflow_id}_web_search",
                name="Web Search",
                agent_type="web",
                action="search",
                parameters={"query": query, "max_results": 10}
            ),
            Task(
                id=f"{workflow_id}_doc_search",
                name="Document Search",
                agent_type="document",
                action="search",
                parameters={"query": query, "top_k": 5}
            ),
            Task(
                id=f"{workflow_id}_synthesize",
                name="Synthesize Results",
                agent_type="chat",
                action="synthesize",
                parameters={
                    "query": query,
                    "sources": ["web_results", "doc_results"]
                },
                dependencies=[f"{workflow_id}_web_search", f"{workflow_id}_doc_search"]
            ),
            Task(
                id=f"{workflow_id}_fact_check",
                name="Fact Check",
                agent_type="web",
                action="fact_check",
                parameters={"content": "synthesis_result"},
                dependencies=[f"{workflow_id}_synthesize"]
            ),
            Task(
                id=f"{workflow_id}_final_report",
                name="Generate Report",
                agent_type="chat",
                action="generate_report",
                parameters={
                    "query": query,
                    "synthesis": "synthesis_result",
                    "fact_check": "fact_check_result"
                },
                dependencies=[f"{workflow_id}_fact_check"]
            )
        ]
        
        return Workflow(
            id=workflow_id,
            name="Research Pipeline",
            description="Comprehensive research using multiple agents",
            tasks=tasks,
            created_by=user_id,
            metadata={"query": query}
        )
    
    @staticmethod
    def code_review_workflow(code: str, language: str, user_id: str) -> Workflow:
        """Create code review workflow"""
        workflow_id = str(uuid4())
        
        tasks = [
            Task(
                id=f"{workflow_id}_syntax_check",
                name="Syntax Check",
                agent_type="code",
                action="check_syntax",
                parameters={"code": code, "language": language}
            ),
            Task(
                id=f"{workflow_id}_style_check",
                name="Style Check",
                agent_type="code",
                action="check_style",
                parameters={"code": code, "language": language}
            ),
            Task(
                id=f"{workflow_id}_security_scan",
                name="Security Scan",
                agent_type="code",
                action="security_scan",
                parameters={"code": code, "language": language}
            ),
            Task(
                id=f"{workflow_id}_performance_analysis",
                name="Performance Analysis",
                agent_type="code",
                action="analyze_performance",
                parameters={"code": code, "language": language}
            ),
            Task(
                id=f"{workflow_id}_generate_report",
                name="Generate Review Report",
                agent_type="chat",
                action="compile_review",
                parameters={
                    "code": code,
                    "language": language,
                    "checks": ["syntax", "style", "security", "performance"]
                },
                dependencies=[
                    f"{workflow_id}_syntax_check",
                    f"{workflow_id}_style_check", 
                    f"{workflow_id}_security_scan",
                    f"{workflow_id}_performance_analysis"
                ]
            )
        ]
        
        return Workflow(
            id=workflow_id,
            name="Code Review Pipeline",
            description="Comprehensive code review and analysis",
            tasks=tasks,
            created_by=user_id,
            metadata={"language": language}
        )

class WorkflowEngine:
    """Advanced workflow execution engine"""
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.active_workflows: Dict[str, Workflow] = {}
        self.completed_workflows: Dict[str, Workflow] = {}
        self.task_executors: Dict[str, Callable] = {}
        self.workflow_listeners: List[Callable] = []
        self.max_concurrent_workflows = 10
        self.max_concurrent_tasks = 20
        self._running_tasks = 0
        self._execution_lock = asyncio.Lock()
    
    def register_task_executor(self, agent_type: str, action: str, executor: Callable):
        """Register task executor for specific agent type and action"""
        key = f"{agent_type}:{action}"
        self.task_executors[key] = executor
        logger.info(f"Registered task executor: {key}")
    
    def add_workflow_listener(self, listener: Callable):
        """Add workflow event listener"""
        self.workflow_listeners.append(listener)
    
    async def _notify_listeners(self, event: str, workflow: Workflow, task: Optional[Task] = None):
        """Notify workflow listeners of events"""
        for listener in self.workflow_listeners:
            try:
                await listener(event, workflow, task)
            except Exception as e:
                logger.error(f"Workflow listener error: {str(e)}")
    
    async def create_workflow(self, workflow: Workflow) -> str:
        """Create and register a new workflow"""
        if len(self.active_workflows) >= self.max_concurrent_workflows:
            raise RuntimeError("Maximum concurrent workflows reached")
        
        self.active_workflows[workflow.id] = workflow
        await self._notify_listeners("workflow_created", workflow)
        
        logger.info(f"Created workflow: {workflow.name} ({workflow.id})")
        return workflow.id
    
    async def start_workflow(self, workflow_id: str) -> bool:
        """Start workflow execution"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        
        if workflow.status != WorkflowStatus.CREATED:
            raise RuntimeError(f"Workflow {workflow_id} is not in created state")
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        
        await self._notify_listeners("workflow_started", workflow)
        
        # Start execution in background
        asyncio.create_task(self._execute_workflow(workflow))
        
        logger.info(f"Started workflow: {workflow.name} ({workflow.id})")
        return True
    
    async def _execute_workflow(self, workflow: Workflow):
        """Execute workflow tasks"""
        try:
            while True:
                # Find ready tasks (dependencies satisfied)
                ready_tasks = self._get_ready_tasks(workflow)
                
                if not ready_tasks:
                    # Check if workflow is complete
                    if self._is_workflow_complete(workflow):
                        await self._complete_workflow(workflow)
                        break
                    
                    # Check if workflow is stuck
                    if self._is_workflow_stuck(workflow):
                        await self._fail_workflow(workflow, "Workflow is stuck - no tasks can proceed")
                        break
                    
                    # Wait for running tasks
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready tasks
                tasks_to_execute = ready_tasks[:self.max_concurrent_tasks - self._running_tasks]
                
                for task in tasks_to_execute:
                    asyncio.create_task(self._execute_task(workflow, task))
                
                await asyncio.sleep(0.1)  # Small delay to prevent tight loop
                
        except Exception as e:
            logger.error(f"Workflow execution error: {str(e)}")
            await self._fail_workflow(workflow, str(e))
    
    def _get_ready_tasks(self, workflow: Workflow) -> List[Task]:
        """Get tasks that are ready to execute"""
        ready_tasks = []
        
        for task in workflow.tasks:
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            dependencies_met = True
            for dep_id in task.dependencies:
                dep_task = next((t for t in workflow.tasks if t.id == dep_id), None)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                ready_tasks.append(task)
        
        return ready_tasks
    
    def _is_workflow_complete(self, workflow: Workflow) -> bool:
        """Check if workflow is complete"""
        return all(task.status == TaskStatus.COMPLETED for task in workflow.tasks)
    
    def _is_workflow_stuck(self, workflow: Workflow) -> bool:
        """Check if workflow is stuck"""
        # If there are pending tasks but no running tasks, workflow might be stuck
        pending_tasks = [t for t in workflow.tasks if t.status == TaskStatus.PENDING]
        running_tasks = [t for t in workflow.tasks if t.status == TaskStatus.RUNNING]
        
        return len(pending_tasks) > 0 and len(running_tasks) == 0
    
    async def _execute_task(self, workflow: Workflow, task: Task):
        """Execute individual task"""
        async with self._execution_lock:
            self._running_tasks += 1
        
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            await self._notify_listeners("task_started", workflow, task)
            
            # Find task executor
            executor_key = f"{task.agent_type}:{task.action}"
            if executor_key not in self.task_executors:
                # Try generic agent execution
                result = await self._execute_with_agent(task)
            else:
                executor = self.task_executors[executor_key]
                result = await executor(task.parameters, workflow.context)
            
            # Create task result
            task_result = TaskResult(
                task_id=task.id,
                status=TaskStatus.COMPLETED,
                result=result,
                execution_time=(datetime.utcnow() - task.started_at).total_seconds()
            )
            
            task.result = task_result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            # Update workflow context with result
            workflow.context[task.id] = result
            
            await self._notify_listeners("task_completed", workflow, task)
            
            logger.info(f"Task completed: {task.name} ({task.id})")
            
        except Exception as e:
            task_result = TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time=(datetime.utcnow() - task.started_at).total_seconds() if task.started_at else 0
            )
            
            task.result = task_result
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            
            await self._notify_listeners("task_failed", workflow, task)
            
            logger.error(f"Task failed: {task.name} ({task.id}) - {str(e)}")
            
            # Check if task should be retried
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.started_at = None
                task.completed_at = None
                logger.info(f"Retrying task: {task.name} (attempt {task.retry_count + 1})")
        
        finally:
            async with self._execution_lock:
                self._running_tasks -= 1
    
    async def _execute_with_agent(self, task: Task) -> Any:
        """Execute task using agent manager"""
        # Get appropriate agent
        agent = self.agent_manager.registry.get_agents_by_type(task.agent_type)
        if not agent:
            raise RuntimeError(f"No agent available for type: {task.agent_type}")
        
        # Create query based on action and parameters
        query = self._build_agent_query(task.action, task.parameters)
        
        # Execute with agent
        result = await agent[0].process_query(query, task.parameters)
        return result
    
    def _build_agent_query(self, action: str, parameters: Dict[str, Any]) -> str:
        """Build query string for agent based on action and parameters"""
        action_templates = {
            "search": "Search for: {query}",
            "analyze": "Analyze: {content}",
            "summarize": "Summarize: {content}",
            "extract": "Extract information from: {source}",
            "generate": "Generate: {type} for {topic}",
            "check": "Check {type}: {content}",
            "review": "Review {type}: {content}"
        }
        
        template = action_templates.get(action, f"Perform {action} with parameters: {parameters}")
        
        try:
            return template.format(**parameters)
        except KeyError:
            return f"Perform {action}: {json.dumps(parameters)}"
    
    async def _complete_workflow(self, workflow: Workflow):
        """Complete workflow execution"""
        workflow.status = WorkflowStatus.COMPLETED
        workflow.completed_at = datetime.utcnow()
        
        # Move to completed workflows
        self.completed_workflows[workflow.id] = workflow
        del self.active_workflows[workflow.id]
        
        await self._notify_listeners("workflow_completed", workflow)
        
        logger.info(f"Workflow completed: {workflow.name} ({workflow.id})")
    
    async def _fail_workflow(self, workflow: Workflow, error: str):
        """Fail workflow execution"""
        workflow.status = WorkflowStatus.FAILED
        workflow.completed_at = datetime.utcnow()
        workflow.metadata["error"] = error
        
        # Move to completed workflows
        self.completed_workflows[workflow.id] = workflow
        del self.active_workflows[workflow.id]
        
        await self._notify_listeners("workflow_failed", workflow)
        
        logger.error(f"Workflow failed: {workflow.name} ({workflow.id}) - {error}")
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel workflow execution"""
        if workflow_id not in self.active_workflows:
            return False
        
        workflow = self.active_workflows[workflow_id]
        workflow.status = WorkflowStatus.CANCELLED
        workflow.completed_at = datetime.utcnow()
        
        # Cancel running tasks
        for task in workflow.tasks:
            if task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.utcnow()
        
        # Move to completed workflows
        self.completed_workflows[workflow.id] = workflow
        del self.active_workflows[workflow.id]
        
        await self._notify_listeners("workflow_cancelled", workflow)
        
        logger.info(f"Workflow cancelled: {workflow.name} ({workflow.id})")
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status and progress"""
        workflow = self.active_workflows.get(workflow_id) or self.completed_workflows.get(workflow_id)
        
        if not workflow:
            return None
        
        completed_tasks = len([t for t in workflow.tasks if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in workflow.tasks if t.status == TaskStatus.FAILED])
        running_tasks = len([t for t in workflow.tasks if t.status == TaskStatus.RUNNING])
        
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "progress": {
                "total_tasks": len(workflow.tasks),
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "running_tasks": running_tasks,
                "progress_percentage": (completed_tasks / len(workflow.tasks)) * 100
            },
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "metadata": workflow.metadata
        }
    
    def list_workflows(self, status: Optional[WorkflowStatus] = None) -> List[Dict[str, Any]]:
        """List workflows with optional status filter"""
        all_workflows = {**self.active_workflows, **self.completed_workflows}
        
        workflows = []
        for workflow in all_workflows.values():
            if status is None or workflow.status == status:
                workflows.append(self.get_workflow_status(workflow.id))
        
        return workflows
    
    async def cleanup(self):
        """Cleanup workflow engine"""
        # Cancel all active workflows
        for workflow_id in list(self.active_workflows.keys()):
            await self.cancel_workflow(workflow_id)
        
        logger.info("Workflow Engine cleanup completed")

# Global workflow engine instance
workflow_engine = None

def get_workflow_engine():
    """Get global workflow engine instance"""
    global workflow_engine
    if workflow_engine is None:
        from .agent_manager import AgentManager
        workflow_engine = WorkflowEngine(AgentManager())
    return workflow_engine 