'use client'

import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Plus, 
  Play, 
  Pause, 
  Square, 
  Settings, 
  Trash2, 
  Copy,
  ArrowRight,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Zap
} from 'lucide-react'
import toast from 'react-hot-toast'

interface WorkflowTask {
  id: string
  name: string
  agentType: string
  action: string
  parameters: Record<string, any>
  dependencies: string[]
  timeout: number
  maxRetries: number
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  position: { x: number; y: number }
}

interface Workflow {
  id: string
  name: string
  description: string
  tasks: WorkflowTask[]
  status: 'created' | 'running' | 'completed' | 'failed' | 'cancelled'
  metadata: Record<string, any>
}

const agentTypes = [
  { id: 'document', name: 'Document Agent', color: 'bg-blue-500' },
  { id: 'code', name: 'Code Agent', color: 'bg-green-500' },
  { id: 'web', name: 'Web Agent', color: 'bg-purple-500' },
  { id: 'chat', name: 'Chat Agent', color: 'bg-orange-500' }
]

const commonActions = {
  document: ['extract_content', 'create_chunks', 'generate_embeddings', 'analyze_content', 'summarize'],
  code: ['check_syntax', 'check_style', 'security_scan', 'analyze_performance', 'refactor'],
  web: ['search', 'fetch_news', 'fact_check', 'get_weather'],
  chat: ['synthesize', 'generate_report', 'coordinate', 'summarize']
}

export function WorkflowBuilder() {
  const [workflow, setWorkflow] = useState<Workflow>({
    id: '',
    name: 'New Workflow',
    description: '',
    tasks: [],
    status: 'created',
    metadata: {}
  })
  
  const [selectedTask, setSelectedTask] = useState<WorkflowTask | null>(null)
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false)
  const [draggedTask, setDraggedTask] = useState<string | null>(null)
  const [isExecuting, setIsExecuting] = useState(false)

  const addTask = useCallback(() => {
    const newTask: WorkflowTask = {
      id: `task_${Date.now()}`,
      name: 'New Task',
      agentType: 'document',
      action: 'extract_content',
      parameters: {},
      dependencies: [],
      timeout: 300,
      maxRetries: 3,
      status: 'pending',
      position: { x: 100 + workflow.tasks.length * 200, y: 100 }
    }
    
    setWorkflow(prev => ({
      ...prev,
      tasks: [...prev.tasks, newTask]
    }))
    
    setSelectedTask(newTask)
    setIsTaskModalOpen(true)
  }, [workflow.tasks.length])

  const updateTask = useCallback((taskId: string, updates: Partial<WorkflowTask>) => {
    setWorkflow(prev => ({
      ...prev,
      tasks: prev.tasks.map(task => 
        task.id === taskId ? { ...task, ...updates } : task
      )
    }))
  }, [])

  const deleteTask = useCallback((taskId: string) => {
    setWorkflow(prev => ({
      ...prev,
      tasks: prev.tasks.filter(task => task.id !== taskId)
    }))
    
    // Remove dependencies to this task
    setWorkflow(prev => ({
      ...prev,
      tasks: prev.tasks.map(task => ({
        ...task,
        dependencies: task.dependencies.filter(dep => dep !== taskId)
      }))
    }))
  }, [])

  const duplicateTask = useCallback((task: WorkflowTask) => {
    const newTask: WorkflowTask = {
      ...task,
      id: `task_${Date.now()}`,
      name: `${task.name} (Copy)`,
      position: { x: task.position.x + 50, y: task.position.y + 50 },
      dependencies: []
    }
    
    setWorkflow(prev => ({
      ...prev,
      tasks: [...prev.tasks, newTask]
    }))
  }, [])

  const executeWorkflow = async () => {
    if (workflow.tasks.length === 0) {
      toast.error('Add at least one task to execute the workflow')
      return
    }

    setIsExecuting(true)
    
    try {
      // Create workflow
      const response = await fetch('http://localhost:8000/workflows/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          name: workflow.name,
          description: workflow.description,
          tasks: workflow.tasks.map(task => ({
            name: task.name,
            agent_type: task.agentType,
            action: task.action,
            parameters: task.parameters,
            dependencies: task.dependencies,
            timeout: task.timeout,
            max_retries: task.maxRetries
          })),
          metadata: workflow.metadata
        })
      })

      if (!response.ok) {
        throw new Error('Failed to create workflow')
      }

      const createdWorkflow = await response.json()
      
      // Start workflow execution
      const startResponse = await fetch(`http://localhost:8000/workflows/${createdWorkflow.id}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (!startResponse.ok) {
        throw new Error('Failed to start workflow')
      }

      toast.success('Workflow started successfully!')
      
      // Update workflow status
      setWorkflow(prev => ({ ...prev, status: 'running', id: createdWorkflow.id }))
      
    } catch (error) {
      console.error('Workflow execution error:', error)
      toast.error('Failed to execute workflow')
    } finally {
      setIsExecuting(false)
    }
  }

  const getTaskStatusIcon = (status: WorkflowTask['status']) => {
    switch (status) {
      case 'running':
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'cancelled':
        return <Square className="h-4 w-4 text-gray-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getAgentTypeColor = (agentType: string) => {
    return agentTypes.find(type => type.id === agentType)?.color || 'bg-gray-500'
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center space-x-4">
          <input
            type="text"
            value={workflow.name}
            onChange={(e) => setWorkflow(prev => ({ ...prev, name: e.target.value }))}
            className="text-xl font-bold bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-2"
          />
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            workflow.status === 'running' ? 'bg-blue-100 text-blue-800' :
            workflow.status === 'completed' ? 'bg-green-100 text-green-800' :
            workflow.status === 'failed' ? 'bg-red-100 text-red-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {workflow.status}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={addTask}
            className="btn-secondary text-sm"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add Task
          </button>
          
          <button
            onClick={executeWorkflow}
            disabled={isExecuting || workflow.tasks.length === 0}
            className="btn-primary text-sm disabled:opacity-50"
          >
            {isExecuting ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-1" />
            ) : (
              <Play className="h-4 w-4 mr-1" />
            )}
            Execute
          </button>
        </div>
      </div>

      {/* Workflow Canvas */}
      <div className="flex-1 relative bg-gray-50 overflow-auto">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        
        {workflow.tasks.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Zap className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Build Your Workflow</h3>
              <p className="text-gray-600 mb-4">Add tasks to create a multi-agent workflow</p>
              <button
                onClick={addTask}
                className="btn-primary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add First Task
              </button>
            </div>
          </div>
        ) : (
          <div className="relative w-full h-full min-h-[600px]">
            {/* Connection Lines */}
            <svg className="absolute inset-0 pointer-events-none" style={{ zIndex: 1 }}>
              {workflow.tasks.map(task => 
                task.dependencies.map(depId => {
                  const depTask = workflow.tasks.find(t => t.id === depId)
                  if (!depTask) return null
                  
                  return (
                    <line
                      key={`${depId}-${task.id}`}
                      x1={depTask.position.x + 100}
                      y1={depTask.position.y + 40}
                      x2={task.position.x}
                      y2={task.position.y + 40}
                      stroke="#6b7280"
                      strokeWidth="2"
                      markerEnd="url(#arrowhead)"
                    />
                  )
                })
              )}
              
              <defs>
                <marker
                  id="arrowhead"
                  markerWidth="10"
                  markerHeight="7"
                  refX="9"
                  refY="3.5"
                  orient="auto"
                >
                  <polygon
                    points="0 0, 10 3.5, 0 7"
                    fill="#6b7280"
                  />
                </marker>
              </defs>
            </svg>

            {/* Tasks */}
            {workflow.tasks.map(task => (
              <motion.div
                key={task.id}
                drag
                dragMomentum={false}
                onDragEnd={(event, info) => {
                  updateTask(task.id, {
                    position: {
                      x: Math.max(0, task.position.x + info.offset.x),
                      y: Math.max(0, task.position.y + info.offset.y)
                    }
                  })
                }}
                className="absolute cursor-move"
                style={{ 
                  left: task.position.x, 
                  top: task.position.y,
                  zIndex: 2
                }}
                whileHover={{ scale: 1.02 }}
                whileDrag={{ scale: 1.05, zIndex: 10 }}
              >
                <div className="bg-white rounded-lg shadow-md border border-gray-200 w-48 p-3">
                  {/* Task Header */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${getAgentTypeColor(task.agentType)}`} />
                      {getTaskStatusIcon(task.status)}
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => {
                          setSelectedTask(task)
                          setIsTaskModalOpen(true)
                        }}
                        className="p-1 text-gray-400 hover:text-gray-600"
                      >
                        <Settings className="h-3 w-3" />
                      </button>
                      
                      <button
                        onClick={() => duplicateTask(task)}
                        className="p-1 text-gray-400 hover:text-gray-600"
                      >
                        <Copy className="h-3 w-3" />
                      </button>
                      
                      <button
                        onClick={() => deleteTask(task.id)}
                        className="p-1 text-gray-400 hover:text-red-600"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                  
                  {/* Task Content */}
                  <div>
                    <h4 className="font-medium text-sm text-gray-900 mb-1">{task.name}</h4>
                    <p className="text-xs text-gray-600 mb-1">{task.agentType} • {task.action}</p>
                    
                    {task.dependencies.length > 0 && (
                      <div className="text-xs text-gray-500">
                        Depends on: {task.dependencies.length} task{task.dependencies.length !== 1 ? 's' : ''}
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Task Configuration Modal */}
      <AnimatePresence>
        {isTaskModalOpen && selectedTask && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setIsTaskModalOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Configure Task</h3>
                
                <div className="space-y-4">
                  {/* Task Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Task Name
                    </label>
                    <input
                      type="text"
                      value={selectedTask.name}
                      onChange={(e) => updateTask(selectedTask.id, { name: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  
                  {/* Agent Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Agent Type
                    </label>
                    <select
                      value={selectedTask.agentType}
                      onChange={(e) => updateTask(selectedTask.id, { 
                        agentType: e.target.value,
                        action: commonActions[e.target.value as keyof typeof commonActions][0]
                      })}
                      className="input-field"
                    >
                      {agentTypes.map(type => (
                        <option key={type.id} value={type.id}>
                          {type.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  {/* Action */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Action
                    </label>
                    <select
                      value={selectedTask.action}
                      onChange={(e) => updateTask(selectedTask.id, { action: e.target.value })}
                      className="input-field"
                    >
                      {commonActions[selectedTask.agentType as keyof typeof commonActions].map(action => (
                        <option key={action} value={action}>
                          {action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  {/* Dependencies */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Dependencies
                    </label>
                    <div className="space-y-2">
                      {workflow.tasks
                        .filter(task => task.id !== selectedTask.id)
                        .map(task => (
                          <label key={task.id} className="flex items-center">
                            <input
                              type="checkbox"
                              checked={selectedTask.dependencies.includes(task.id)}
                              onChange={(e) => {
                                const newDeps = e.target.checked
                                  ? [...selectedTask.dependencies, task.id]
                                  : selectedTask.dependencies.filter(dep => dep !== task.id)
                                updateTask(selectedTask.id, { dependencies: newDeps })
                              }}
                              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                            />
                            <span className="ml-2 text-sm text-gray-700">{task.name}</span>
                          </label>
                        ))}
                    </div>
                  </div>
                  
                  {/* Timeout */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Timeout (seconds)
                    </label>
                    <input
                      type="number"
                      value={selectedTask.timeout}
                      onChange={(e) => updateTask(selectedTask.id, { timeout: parseInt(e.target.value) })}
                      className="input-field"
                      min="1"
                      max="3600"
                    />
                  </div>
                  
                  {/* Max Retries */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Max Retries
                    </label>
                    <input
                      type="number"
                      value={selectedTask.maxRetries}
                      onChange={(e) => updateTask(selectedTask.id, { maxRetries: parseInt(e.target.value) })}
                      className="input-field"
                      min="0"
                      max="10"
                    />
                  </div>
                </div>
                
                <div className="flex justify-end space-x-2 mt-6">
                  <button
                    onClick={() => setIsTaskModalOpen(false)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => setIsTaskModalOpen(false)}
                    className="btn-primary"
                  >
                    Save
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
} 