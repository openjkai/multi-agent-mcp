'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Brain,
  Activity,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Users,
  Clock,
  Target,
  Zap,
  Eye,
  Heart,
  Battery,
  Shield,
  Lightbulb,
  Settings,
  BarChart3,
  RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'

interface CognitiveState {
  workload_level: string
  attention_level: number
  stress_level: number
  fatigue_level: number
  confidence_level: number
  load_components: Record<string, number>
  session_metrics: {
    duration: number
    task_switches: number
    error_rate: number
  }
  recommendations: string[]
}

interface WorkloadProfile {
  baseline_capacity: number
  peak_capacity: number
  recovery_rate: number
  stress_sensitivity: number
  optimal_workload_range: [number, number]
  adaptation_preferences: string[]
}

interface AdaptationRecommendation {
  id: string
  strategy: string
  confidence: number
  expected_benefit: number
  implementation_effort: number
  parameters: Record<string, any>
}

export function CognitiveWorkloadMonitor() {
  const [cognitiveState, setCognitiveState] = useState<CognitiveState | null>(null)
  const [workloadProfile, setWorkloadProfile] = useState<WorkloadProfile | null>(null)
  const [adaptationRecommendations, setAdaptationRecommendations] = useState<AdaptationRecommendation[]>([])
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'components' | 'adaptations' | 'insights'>('overview')

  const loadCognitiveState = async () => {
    try {
      const response = await fetch('http://localhost:8000/cognitive/state', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          context: {
            session_duration: Math.random() * 7200, // 0-2 hours
            task_switches: Math.floor(Math.random() * 10),
            error_rate: Math.random() * 0.2,
            task_complexity: Math.random(),
            interface_complexity: Math.random(),
            learning_effort: Math.random(),
            emotional_stress: Math.random() * 0.5,
            physical_fatigue: Math.random() * 0.3,
            time_pressure: Math.random(),
            success_rate: 0.7 + Math.random() * 0.3,
            experience_level: 0.5 + Math.random() * 0.5
          }
        })
      })

      if (response.ok) {
        const data = await response.json()
        setCognitiveState(data.insights)
      }
    } catch (error) {
      console.error('Failed to load cognitive state:', error)
    }
  }

  const loadWorkloadProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/cognitive/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setWorkloadProfile(data.profile)
      }
    } catch (error) {
      console.error('Failed to load workload profile:', error)
    }
  }

  const startMonitoring = () => {
    setIsMonitoring(true)
    toast.success('Cognitive monitoring started')
    
    // Simulate real-time monitoring
    const interval = setInterval(() => {
      loadCognitiveState()
    }, 5000)

    return () => clearInterval(interval)
  }

  const stopMonitoring = () => {
    setIsMonitoring(false)
    toast.info('Cognitive monitoring stopped')
  }

  const getWorkloadColor = (level: string) => {
    switch (level) {
      case 'very_low': return 'text-green-600 bg-green-100'
      case 'low': return 'text-blue-600 bg-blue-100'
      case 'moderate': return 'text-yellow-600 bg-yellow-100'
      case 'high': return 'text-orange-600 bg-orange-100'
      case 'very_high': return 'text-red-600 bg-red-100'
      case 'overload': return 'text-red-800 bg-red-200'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'very_low': return CheckCircle
      case 'low': return CheckCircle
      case 'moderate': return Activity
      case 'high': return AlertTriangle
      case 'very_high': return AlertTriangle
      case 'overload': return AlertTriangle
      default: return Activity
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-yellow-600'
    if (score >= 0.4) return 'text-orange-600'
    return 'text-red-600'
  }

  useEffect(() => {
    loadCognitiveState()
    loadWorkloadProfile()
  }, [])

  if (!cognitiveState) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Brain className="h-6 w-6 mr-2 text-primary-600" />
          Cognitive Workload Monitor
        </h2>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={loadCognitiveState}
            className="btn-secondary text-sm"
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Refresh
          </button>
          
          {isMonitoring ? (
            <button
              onClick={stopMonitoring}
              className="btn-secondary text-sm bg-red-600 hover:bg-red-700 text-white"
            >
              <Activity className="h-4 w-4 mr-1" />
              Stop Monitoring
            </button>
          ) : (
            <button
              onClick={startMonitoring}
              className="btn-primary text-sm"
            >
              <Activity className="h-4 w-4 mr-1" />
              Start Monitoring
            </button>
          )}
        </div>
      </div>

      {/* Current State Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-r from-blue-50 to-blue-100"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-900">Workload Level</p>
              <p className="text-2xl font-bold text-blue-700 capitalize">
                {cognitiveState.workload_level.replace('_', ' ')}
              </p>
            </div>
            {React.createElement(getLevelIcon(cognitiveState.workload_level), {
              className: "h-8 w-8 text-blue-600"
            })}
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
              <p className="text-sm font-medium text-green-900">Attention</p>
              <p className="text-2xl font-bold text-green-700">
                {Math.round(cognitiveState.attention_level * 100)}%
              </p>
            </div>
            <Eye className="h-8 w-8 text-green-600" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card bg-gradient-to-r from-orange-50 to-orange-100"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-orange-900">Stress Level</p>
              <p className="text-2xl font-bold text-orange-700">
                {Math.round(cognitiveState.stress_level * 100)}%
              </p>
            </div>
            <Heart className="h-8 w-8 text-orange-600" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card bg-gradient-to-r from-purple-50 to-purple-100"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-900">Confidence</p>
              <p className="text-2xl font-bold text-purple-700">
                {Math.round(cognitiveState.confidence_level * 100)}%
              </p>
            </div>
            <Shield className="h-8 w-8 text-purple-600" />
          </div>
        </motion.div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
        {[
          { id: 'overview', label: 'Overview', icon: BarChart3 },
          { id: 'components', label: 'Load Components', icon: Target },
          { id: 'adaptations', label: 'Adaptations', icon: Settings },
          { id: 'insights', label: 'Insights', icon: Lightbulb }
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
        {activeTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Workload Level Indicator */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Workload Status</h3>
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-gray-600">Overall Workload</span>
                <span className={`px-3 py-1 text-sm rounded-full ${getWorkloadColor(cognitiveState.workload_level)}`}>
                  {cognitiveState.workload_level.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className={`h-3 rounded-full transition-all duration-500 ${
                    cognitiveState.workload_level === 'overload' ? 'bg-red-600' :
                    cognitiveState.workload_level === 'very_high' ? 'bg-red-500' :
                    cognitiveState.workload_level === 'high' ? 'bg-orange-500' :
                    cognitiveState.workload_level === 'moderate' ? 'bg-yellow-500' :
                    cognitiveState.workload_level === 'low' ? 'bg-blue-500' :
                    'bg-green-500'
                  }`}
                  style={{ 
                    width: `${Math.min(100, Math.max(10, 
                      cognitiveState.workload_level === 'very_low' ? 20 :
                      cognitiveState.workload_level === 'low' ? 40 :
                      cognitiveState.workload_level === 'moderate' ? 60 :
                      cognitiveState.workload_level === 'high' ? 80 :
                      cognitiveState.workload_level === 'very_high' ? 90 :
                      100
                    ))}%` 
                  }}
                />
              </div>
            </div>

            {/* Session Metrics */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <Clock className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-blue-700">
                    {Math.round(cognitiveState.session_metrics.duration / 60)}m
                  </div>
                  <div className="text-sm text-blue-600">Session Duration</div>
                </div>
                
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <Activity className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-green-700">
                    {cognitiveState.session_metrics.task_switches}
                  </div>
                  <div className="text-sm text-green-600">Task Switches</div>
                </div>
                
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <AlertTriangle className="h-8 w-8 text-red-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-red-700">
                    {Math.round(cognitiveState.session_metrics.error_rate * 100)}%
                  </div>
                  <div className="text-sm text-red-600">Error Rate</div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {cognitiveState.recommendations.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
                <div className="space-y-2">
                  {cognitiveState.recommendations.map((recommendation, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg"
                    >
                      <Lightbulb className="h-5 w-5 text-blue-600 mt-0.5" />
                      <span className="text-sm text-blue-800">{recommendation}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'components' && (
          <motion.div
            key="components"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Cognitive Load Components</h3>
              <div className="space-y-4">
                {Object.entries(cognitiveState.load_components).map(([component, value]) => (
                  <div key={component} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {component.replace('_', ' ')}
                      </span>
                      <span className={`text-sm font-bold ${getScoreColor(value)}`}>
                        {Math.round(value * 100)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-500 ${
                          value >= 0.8 ? 'bg-red-500' :
                          value >= 0.6 ? 'bg-orange-500' :
                          value >= 0.4 ? 'bg-yellow-500' :
                          'bg-green-500'
                        }`}
                        style={{ width: `${value * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Individual Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="card">
                <h4 className="font-medium text-gray-900 mb-3">Attention Level</h4>
                <div className="flex items-center space-x-3">
                  <div className="flex-1 bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-blue-500 h-3 rounded-full"
                      style={{ width: `${cognitiveState.attention_level * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {Math.round(cognitiveState.attention_level * 100)}%
                  </span>
                </div>
              </div>

              <div className="card">
                <h4 className="font-medium text-gray-900 mb-3">Fatigue Level</h4>
                <div className="flex items-center space-x-3">
                  <div className="flex-1 bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-orange-500 h-3 rounded-full"
                      style={{ width: `${cognitiveState.fatigue_level * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {Math.round(cognitiveState.fatigue_level * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'adaptations' && (
          <motion.div
            key="adaptations"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Adaptation Strategies</h3>
              <div className="space-y-4">
                {[
                  {
                    strategy: 'Task Decomposition',
                    description: 'Break complex tasks into smaller, manageable subtasks',
                    confidence: 0.8,
                    benefit: 0.3,
                    effort: 0.4
                  },
                  {
                    strategy: 'Interface Simplification',
                    description: 'Reduce visual complexity and cognitive load',
                    confidence: 0.7,
                    benefit: 0.2,
                    effort: 0.3
                  },
                  {
                    strategy: 'Automation Increase',
                    description: 'Enable more automated assistance and suggestions',
                    confidence: 0.9,
                    benefit: 0.4,
                    effort: 0.6
                  },
                  {
                    strategy: 'Break Suggestion',
                    description: 'Recommend cognitive rest periods',
                    confidence: 0.8,
                    benefit: 0.5,
                    effort: 0.1
                  }
                ].map((adaptation, index) => (
                  <motion.div
                    key={adaptation.strategy}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{adaptation.strategy}</h4>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${getScoreColor(adaptation.confidence)}`}>
                          {Math.round(adaptation.confidence * 100)}% confidence
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${getScoreColor(adaptation.benefit)}`}>
                          {Math.round(adaptation.benefit * 100)}% benefit
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{adaptation.description}</p>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Implementation Effort:</span>
                      <span className={`font-medium ${getScoreColor(1 - adaptation.effort)}`}>
                        {Math.round(adaptation.effort * 100)}%
                      </span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'insights' && (
          <motion.div
            key="insights"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Cognitive Insights</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Optimal Performance Window</h4>
                    <p className="text-sm text-blue-700">
                      Your cognitive performance is best when workload is between 30-70% of capacity.
                      Current level: {cognitiveState.workload_level.replace('_', ' ')}
                    </p>
                  </div>
                  
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h4 className="font-medium text-green-900 mb-2">Attention Management</h4>
                    <p className="text-sm text-green-700">
                      Attention level: {Math.round(cognitiveState.attention_level * 100)}%.
                      {cognitiveState.attention_level < 0.5 ? ' Consider reducing distractions.' : ' Good focus level.'}
                    </p>
                  </div>
                  
                  <div className="p-4 bg-orange-50 rounded-lg">
                    <h4 className="font-medium text-orange-900 mb-2">Stress Management</h4>
                    <p className="text-sm text-orange-700">
                      Stress level: {Math.round(cognitiveState.stress_level * 100)}%.
                      {cognitiveState.stress_level > 0.7 ? ' High stress detected - consider breaks.' : ' Stress level manageable.'}
                    </p>
                  </div>
                  
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h4 className="font-medium text-purple-900 mb-2">Confidence Assessment</h4>
                    <p className="text-sm text-purple-700">
                      Confidence level: {Math.round(cognitiveState.confidence_level * 100)}%.
                      {cognitiveState.confidence_level < 0.4 ? ' Consider additional guidance.' : ' Good confidence level.'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {workloadProfile && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Workload Profile</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Capacity Range</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Baseline:</span>
                        <span className="text-gray-900">{Math.round(workloadProfile.baseline_capacity * 100)}%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Peak:</span>
                        <span className="text-gray-900">{Math.round(workloadProfile.peak_capacity * 100)}%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Recovery Rate:</span>
                        <span className="text-gray-900">{Math.round(workloadProfile.recovery_rate * 100)}%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Optimal Range</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Min:</span>
                        <span className="text-gray-900">{Math.round(workloadProfile.optimal_workload_range[0] * 100)}%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Max:</span>
                        <span className="text-gray-900">{Math.round(workloadProfile.optimal_workload_range[1] * 100)}%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Stress Sensitivity:</span>
                        <span className="text-gray-900">{Math.round(workloadProfile.stress_sensitivity * 100)}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

