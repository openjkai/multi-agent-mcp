'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Zap,
  Brain,
  Target,
  TrendingUp,
  Activity,
  BarChart3,
  Settings,
  Play,
  Pause,
  RotateCcw,
  Download,
  Eye,
  Cpu,
  Network,
  Lightbulb,
  CheckCircle,
  AlertTriangle,
  Clock,
  Users
} from 'lucide-react'
import toast from 'react-hot-toast'

interface QuantumParticle {
  id: string
  position: number[]
  velocity: number[]
  fitness: number
  quantum_state: string
  entanglement_connections: string[]
}

interface OptimizationProblem {
  id: string
  problem_type: string
  variables: Record<string, any>
  constraints: any[]
  objective_function: string
  complexity_score: number
}

interface OptimizationResult {
  id: string
  problem_id: string
  variables: Record<string, any>
  fitness_score: number
  confidence: float
  quantum_state: string
  processing_time: number
}

interface QuantumField {
  strength: number
  center: number[]
  particle_count: number
  iteration: number
}

export function QuantumOptimizationDashboard() {
  const [optimizationResults, setOptimizationResults] = useState<OptimizationResult[]>([])
  const [quantumParticles, setQuantumParticles] = useState<QuantumParticle[]>([])
  const [quantumField, setQuantumField] = useState<QuantumField | null>(null)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [selectedProblem, setSelectedProblem] = useState<OptimizationProblem | null>(null)
  const [optimizationStats, setOptimizationStats] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'problems' | 'particles' | 'field' | 'results'>('problems')

  const problemTypes = [
    { id: 'scheduling', name: 'Task Scheduling', icon: Clock, color: 'blue' },
    { id: 'resource_allocation', name: 'Resource Allocation', icon: Target, color: 'green' },
    { id: 'routing', name: 'Routing Optimization', icon: Network, color: 'purple' },
    { id: 'workflow_optimization', name: 'Workflow Optimization', icon: Activity, color: 'orange' },
    { id: 'agent_coordination', name: 'Agent Coordination', icon: Users, color: 'red' },
    { id: 'knowledge_structure', name: 'Knowledge Structure', icon: Brain, color: 'indigo' }
  ]

  const loadOptimizationStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/quantum/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setOptimizationStats(data)
      }
    } catch (error) {
      console.error('Failed to load optimization stats:', error)
    }
  }

  const startOptimization = async (problemType: string) => {
    setIsOptimizing(true)
    try {
      const response = await fetch('http://localhost:8000/quantum/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          problem_type: problemType,
          variables: {
            'param1': { min: 0, max: 100 },
            'param2': { min: 0, max: 1 },
            'param3': { min: 0, max: 10 }
          },
          constraints: [],
          objective_function: 'maximize_fitness'
        })
      })

      if (response.ok) {
        const result = await response.json()
        setOptimizationResults(prev => [result, ...prev])
        toast.success('Optimization completed successfully!')
      }
    } catch (error) {
      console.error('Optimization failed:', error)
      toast.error('Optimization failed')
    } finally {
      setIsOptimizing(false)
    }
  }

  const simulateQuantumParticles = () => {
    const particles: QuantumParticle[] = []
    for (let i = 0; i < 20; i++) {
      particles.push({
        id: `particle_${i}`,
        position: [Math.random() * 100, Math.random() * 100],
        velocity: [Math.random() * 2 - 1, Math.random() * 2 - 1],
        fitness: Math.random(),
        quantum_state: ['superposition', 'entanglement', 'interference'][Math.floor(Math.random() * 3)],
        entanglement_connections: []
      })
    }
    setQuantumParticles(particles)
  }

  const simulateQuantumField = () => {
    setQuantumField({
      strength: Math.random() * 100,
      center: [Math.random() * 100, Math.random() * 100],
      particle_count: quantumParticles.length,
      iteration: Math.floor(Math.random() * 1000)
    })
  }

  useEffect(() => {
    loadOptimizationStats()
    simulateQuantumParticles()
    simulateQuantumField()
  }, [])

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100'
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getQuantumStateColor = (state: string) => {
    switch (state) {
      case 'superposition': return 'text-blue-600 bg-blue-100'
      case 'entanglement': return 'text-purple-600 bg-purple-100'
      case 'interference': return 'text-orange-600 bg-orange-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Zap className="h-6 w-6 mr-2 text-primary-600" />
          Quantum Optimization Engine
        </h2>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={loadOptimizationStats}
            className="btn-secondary text-sm"
          >
            <RotateCcw className="h-4 w-4 mr-1" />
            Refresh
          </button>
          
          <button
            onClick={simulateQuantumParticles}
            className="btn-primary text-sm"
          >
            <Play className="h-4 w-4 mr-1" />
            Simulate
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      {optimizationStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card bg-gradient-to-r from-blue-50 to-blue-100"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-900">Total Optimizations</p>
                <p className="text-2xl font-bold text-blue-700">
                  {optimizationStats.total_optimizations}
                </p>
              </div>
              <Target className="h-8 w-8 text-blue-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card bg-gradient-to-r from-green-50 to-green-100"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-900">Success Rate</p>
                <p className="text-2xl font-bold text-green-700">
                  {optimizationStats.success_rate.toFixed(1)}%
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card bg-gradient-to-r from-purple-50 to-purple-100"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-900">Active Particles</p>
                <p className="text-2xl font-bold text-purple-700">
                  {optimizationStats.active_particles}
                </p>
              </div>
              <Cpu className="h-8 w-8 text-purple-600" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card bg-gradient-to-r from-orange-50 to-orange-100"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-orange-900">Field Strength</p>
                <p className="text-2xl font-bold text-orange-700">
                  {optimizationStats.quantum_field_strength}
                </p>
              </div>
              <Activity className="h-8 w-8 text-orange-600" />
            </div>
          </motion.div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
        {[
          { id: 'problems', label: 'Optimization Problems', icon: Target },
          { id: 'particles', label: 'Quantum Particles', icon: Cpu },
          { id: 'field', label: 'Quantum Field', icon: Network },
          { id: 'results', label: 'Results', icon: BarChart3 }
        ].map(tab => {
          const IconComponent = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <IconComponent className="h-4 w-4 mr-2" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'problems' && (
          <motion.div
            key="problems"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Problems</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {problemTypes.map((problem, index) => {
                  const IconComponent = problem.icon
                  return (
                    <motion.div
                      key={problem.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer ${
                        selectedProblem?.id === problem.id ? 'ring-2 ring-primary-500' : ''
                      }`}
                      onClick={() => setSelectedProblem({
                        id: problem.id,
                        problem_type: problem.id,
                        variables: {},
                        constraints: [],
                        objective_function: 'maximize_fitness',
                        complexity_score: Math.random()
                      })}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <IconComponent className={`h-6 w-6 text-${problem.color}-600`} />
                        <span className={`px-2 py-1 text-xs rounded-full bg-${problem.color}-100 text-${problem.color}-600`}>
                          {Math.round(Math.random() * 100)}% complexity
                        </span>
                      </div>
                      <h4 className="font-medium text-gray-900 mb-1">{problem.name}</h4>
                      <p className="text-sm text-gray-600 mb-3">
                        Quantum-optimized solutions for {problem.name.toLowerCase()}
                      </p>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          startOptimization(problem.id)
                        }}
                        disabled={isOptimizing}
                        className={`w-full py-2 px-3 text-sm rounded-md transition-colors ${
                          isOptimizing
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-primary-600 text-white hover:bg-primary-700'
                        }`}
                      >
                        {isOptimizing ? (
                          <div className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                            Optimizing...
                          </div>
                        ) : (
                          'Start Optimization'
                        )}
                      </button>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'particles' && (
          <motion.div
            key="particles"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quantum Particles</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {quantumParticles.map((particle, index) => (
                  <motion.div
                    key={particle.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{particle.id}</h4>
                      <span className={`px-2 py-1 text-xs rounded-full ${getScoreColor(particle.fitness)}`}>
                        {Math.round(particle.fitness * 100)}%
                      </span>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Position:</span>
                        <span className="text-gray-900">
                          ({particle.position[0].toFixed(1)}, {particle.position[1].toFixed(1)})
                        </span>
                      </div>
                      
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Velocity:</span>
                        <span className="text-gray-900">
                          ({particle.velocity[0].toFixed(2)}, {particle.velocity[1].toFixed(2)})
                        </span>
                      </div>
                      
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">State:</span>
                        <span className={`px-2 py-1 text-xs rounded-full ${getQuantumStateColor(particle.quantum_state)}`}>
                          {particle.quantum_state}
                        </span>
                      </div>
                      
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Connections:</span>
                        <span className="text-gray-900">{particle.entanglement_connections.length}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'field' && (
          <motion.div
            key="field"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quantum Field</h3>
              {quantumField ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <Activity className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                      <div className="text-2xl font-bold text-blue-700">{quantumField.strength.toFixed(1)}</div>
                      <div className="text-sm text-blue-600">Field Strength</div>
                    </div>
                    
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <Cpu className="h-8 w-8 text-green-600 mx-auto mb-2" />
                      <div className="text-2xl font-bold text-green-700">{quantumField.particle_count}</div>
                      <div className="text-sm text-green-600">Particles</div>
                    </div>
                    
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <Network className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                      <div className="text-2xl font-bold text-purple-700">{quantumField.iteration}</div>
                      <div className="text-sm text-purple-600">Iteration</div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">Field Center</h4>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">X:</span>
                      <span className="text-gray-900">{quantumField.center[0].toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Y:</span>
                      <span className="text-gray-900">{quantumField.center[1].toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Network className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Quantum Field Data</h3>
                  <p className="text-gray-600 mb-4">Start an optimization to generate quantum field data</p>
                  <button
                    onClick={simulateQuantumField}
                    className="btn-primary"
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Generate Field
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {activeTab === 'results' && (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Results</h3>
              {optimizationResults.length > 0 ? (
                <div className="space-y-4">
                  {optimizationResults.map((result, index) => (
                    <motion.div
                      key={result.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">Result #{index + 1}</h4>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${getScoreColor(result.fitness_score)}`}>
                            {Math.round(result.fitness_score * 100)}%
                          </span>
                          <span className={`px-2 py-1 text-xs rounded-full ${getQuantumStateColor(result.quantum_state)}`}>
                            {result.quantum_state}
                          </span>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Fitness Score:</span>
                          <span className="text-gray-900 ml-2">{result.fitness_score.toFixed(3)}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Confidence:</span>
                          <span className="text-gray-900 ml-2">{Math.round(result.confidence * 100)}%</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Processing Time:</span>
                          <span className="text-gray-900 ml-2">{result.processing_time.toFixed(2)}s</span>
                        </div>
                      </div>
                      
                      {Object.keys(result.variables).length > 0 && (
                        <div className="mt-3">
                          <h5 className="text-sm font-medium text-gray-700 mb-2">Optimized Variables:</h5>
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            {Object.entries(result.variables).map(([key, value]) => (
                              <div key={key} className="flex justify-between">
                                <span className="text-gray-600">{key}:</span>
                                <span className="text-gray-900">{String(value)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BarChart3 className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Yet</h3>
                  <p className="text-gray-600 mb-4">Start an optimization to see results here</p>
                  <button
                    onClick={() => setActiveTab('problems')}
                    className="btn-primary"
                  >
                    <Target className="h-4 w-4 mr-2" />
                    Start Optimization
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

