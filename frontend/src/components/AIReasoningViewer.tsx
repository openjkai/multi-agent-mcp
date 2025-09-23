'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Brain, 
  GitBranch, 
  Target, 
  Lightbulb,
  ArrowRight,
  Clock,
  TrendingUp,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Eye,
  Layers,
  Zap,
  RefreshCw
} from 'lucide-react'

interface ReasoningStep {
  step_id: string
  description: string
  input_data: any
  output_data: any
  confidence: number
  model_used: string
  processing_time: number
  reasoning_type: string
  created_at: string
}

interface ReasoningChain {
  chain_id: string
  task: string
  reasoning_type: string
  steps: ReasoningStep[]
  final_result: any
  overall_confidence: number
  total_processing_time: number
  models_used: string[]
  created_at: string
}

interface TaskDecomposition {
  task_id: string
  original_task: string
  subtasks: Array<{
    id: string
    description: string
    inputs: string[]
    outputs: string[]
    dependencies: string[]
    difficulty: number
  }>
  dependencies: Record<string, string[]>
  execution_order: string[]
  estimated_complexity: number
  created_at: string
}

export function AIReasoningViewer() {
  const [activeTab, setActiveTab] = useState<'chains' | 'decompositions' | 'create'>('chains')
  const [reasoningChains, setReasoningChains] = useState<ReasoningChain[]>([])
  const [decompositions, setDecompositions] = useState<TaskDecomposition[]>([])
  const [selectedChain, setSelectedChain] = useState<ReasoningChain | null>(null)
  const [selectedDecomposition, setSelectedDecomposition] = useState<TaskDecomposition | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [newTask, setNewTask] = useState('')
  const [reasoningType, setReasoningType] = useState('chain_of_thought')

  const reasoningTypes = [
    { value: 'chain_of_thought', label: 'Chain of Thought', icon: ArrowRight, description: 'Step-by-step logical reasoning' },
    { value: 'tree_of_thought', label: 'Tree of Thought', icon: GitBranch, description: 'Multiple reasoning paths' },
    { value: 'decomposition', label: 'Task Decomposition', icon: Layers, description: 'Break complex tasks into subtasks' },
    { value: 'synthesis', label: 'Synthesis', icon: Target, description: 'Combine multiple sources' },
    { value: 'reflection', label: 'Reflection', icon: Eye, description: 'Self-evaluation and improvement' },
    { value: 'debate', label: 'Internal Debate', icon: Brain, description: 'Multiple perspectives analysis' }
  ]

  const createReasoningChain = async () => {
    if (!newTask.trim()) return

    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:8000/ai/reasoning', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          task: newTask,
          reasoning_type: reasoningType,
          context: {},
          requirements: {}
        })
      })

      if (response.ok) {
        const chain = await response.json()
        setReasoningChains(prev => [chain, ...prev])
        setSelectedChain(chain)
        setNewTask('')
        setActiveTab('chains')
      }
    } catch (error) {
      console.error('Failed to create reasoning chain:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getReasoningTypeInfo = (type: string) => {
    return reasoningTypes.find(rt => rt.value === type) || reasoningTypes[0]
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100'
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const formatProcessingTime = (seconds: number) => {
    if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`
    return `${seconds.toFixed(2)}s`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Brain className="h-6 w-6 mr-2 text-primary-600" />
          AI Reasoning Engine
        </h2>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab('chains')}
            className={`px-4 py-2 rounded-lg font-medium ${
              activeTab === 'chains' 
                ? 'bg-primary-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Reasoning Chains
          </button>
          <button
            onClick={() => setActiveTab('decompositions')}
            className={`px-4 py-2 rounded-lg font-medium ${
              activeTab === 'decompositions' 
                ? 'bg-primary-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Task Decompositions
          </button>
          <button
            onClick={() => setActiveTab('create')}
            className={`px-4 py-2 rounded-lg font-medium ${
              activeTab === 'create' 
                ? 'bg-primary-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Create New
          </button>
        </div>
      </div>

      {/* Create New Reasoning Chain */}
      {activeTab === 'create' && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Create AI Reasoning Chain</h3>
          
          <div className="space-y-4">
            {/* Task Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Complex Task or Question
              </label>
              <textarea
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                placeholder="Enter a complex task that requires advanced reasoning..."
                className="w-full h-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            
            {/* Reasoning Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reasoning Approach
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {reasoningTypes.map((type) => {
                  const IconComponent = type.icon
                  return (
                    <motion.div
                      key={type.value}
                      whileHover={{ scale: 1.02 }}
                      className={`p-3 border rounded-lg cursor-pointer ${
                        reasoningType === type.value
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setReasoningType(type.value)}
                    >
                      <div className="flex items-center mb-2">
                        <IconComponent className="h-5 w-5 mr-2 text-primary-600" />
                        <span className="font-medium text-gray-900">{type.label}</span>
                      </div>
                      <p className="text-sm text-gray-600">{type.description}</p>
                    </motion.div>
                  )
                })}
              </div>
            </div>
            
            <button
              onClick={createReasoningChain}
              disabled={isLoading || !newTask.trim()}
              className="btn-primary w-full disabled:opacity-50"
            >
              {isLoading ? (
                <RefreshCw className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Zap className="h-4 w-4 mr-2" />
              )}
              Generate Reasoning Chain
            </button>
          </div>
        </div>
      )}

      {/* Reasoning Chains */}
      {activeTab === 'chains' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chain List */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900">Reasoning Chains</h3>
            {reasoningChains.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Brain className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p>No reasoning chains yet</p>
                <p className="text-sm">Create your first reasoning chain</p>
              </div>
            ) : (
              reasoningChains.map((chain) => {
                const typeInfo = getReasoningTypeInfo(chain.reasoning_type)
                const IconComponent = typeInfo.icon
                
                return (
                  <motion.div
                    key={chain.chain_id}
                    whileHover={{ scale: 1.02 }}
                    className={`card cursor-pointer ${
                      selectedChain?.chain_id === chain.chain_id 
                        ? 'ring-2 ring-primary-500 border-primary-200' 
                        : 'hover:shadow-md'
                    }`}
                    onClick={() => setSelectedChain(chain)}
                  >
                    <div className="flex items-start space-x-3">
                      <IconComponent className="h-5 w-5 mt-1 text-primary-600" />
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 truncate">
                          {chain.task.substring(0, 60)}...
                        </h4>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="text-xs text-gray-500">{typeInfo.label}</span>
                          <span className={`text-xs px-2 py-1 rounded-full ${getConfidenceColor(chain.overall_confidence)}`}>
                            {(chain.overall_confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="flex items-center space-x-2 mt-1 text-xs text-gray-500">
                          <Clock className="h-3 w-3" />
                          <span>{formatProcessingTime(chain.total_processing_time)}</span>
                          <span>•</span>
                          <span>{chain.steps.length} steps</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )
              })
            )}
          </div>

          {/* Chain Details */}
          <div className="lg:col-span-2">
            {selectedChain ? (
              <div className="space-y-4">
                {/* Chain Header */}
                <div className="card">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {selectedChain.task}
                      </h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span>Type: {getReasoningTypeInfo(selectedChain.reasoning_type).label}</span>
                        <span>Steps: {selectedChain.steps.length}</span>
                        <span>Time: {formatProcessingTime(selectedChain.total_processing_time)}</span>
                      </div>
                    </div>
                    <div className={`px-3 py-1 rounded-full ${getConfidenceColor(selectedChain.overall_confidence)}`}>
                      Confidence: {(selectedChain.overall_confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                  
                  {/* Models Used */}
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-700">Models:</span>
                    {selectedChain.models_used.map((model, index) => (
                      <span key={index} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {model}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Reasoning Steps */}
                <div className="space-y-3">
                  {selectedChain.steps.map((step, index) => (
                    <motion.div
                      key={step.step_id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="card relative"
                    >
                      {/* Step Number */}
                      <div className="absolute -left-3 -top-3 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                        {index + 1}
                      </div>
                      
                      <div className="ml-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{step.description}</h4>
                          <div className="flex items-center space-x-2">
                            <span className={`text-xs px-2 py-1 rounded-full ${getConfidenceColor(step.confidence)}`}>
                              {(step.confidence * 100).toFixed(0)}%
                            </span>
                            <span className="text-xs text-gray-500">
                              {formatProcessingTime(step.processing_time)}
                            </span>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {/* Input */}
                          <div>
                            <h5 className="text-sm font-medium text-gray-700 mb-1">Input</h5>
                            <div className="bg-gray-50 rounded p-2 text-xs">
                              <pre className="whitespace-pre-wrap">
                                {JSON.stringify(step.input_data, null, 2)}
                              </pre>
                            </div>
                          </div>
                          
                          {/* Output */}
                          <div>
                            <h5 className="text-sm font-medium text-gray-700 mb-1">Output</h5>
                            <div className="bg-green-50 rounded p-2 text-xs">
                              <pre className="whitespace-pre-wrap">
                                {JSON.stringify(step.output_data, null, 2)}
                              </pre>
                            </div>
                          </div>
                        </div>
                        
                        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                          <span>Model: {step.model_used}</span>
                          <span>Type: {step.reasoning_type}</span>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* Final Result */}
                <div className="card bg-gradient-to-r from-green-50 to-blue-50">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Target className="h-5 w-5 mr-2 text-green-600" />
                    Final Result
                  </h3>
                  <div className="bg-white rounded-lg p-4">
                    <pre className="whitespace-pre-wrap text-sm">
                      {JSON.stringify(selectedChain.final_result, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            ) : (
              <div className="card text-center py-12">
                <Brain className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Reasoning Chain</h3>
                <p className="text-gray-600">Choose a reasoning chain from the list to view its details</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Task Decompositions */}
      {activeTab === 'decompositions' && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Decompositions</h3>
          <div className="text-center py-12 text-gray-500">
            <Layers className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Task Decompositions</h3>
            <p className="text-gray-600">View how complex tasks are broken down into manageable subtasks</p>
          </div>
        </div>
      )}
    </div>
  )
} 