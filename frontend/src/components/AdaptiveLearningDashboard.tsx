'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Brain,
  TrendingUp,
  Target,
  Settings,
  User,
  Clock,
  Zap,
  BarChart3,
  Lightbulb,
  ArrowRight,
  CheckCircle,
  AlertCircle,
  Star,
  Activity,
  Calendar,
  RefreshCw,
  Eye,
  ThumbsUp,
  ThumbsDown
} from 'lucide-react'
import toast from 'react-hot-toast'

interface UserRecommendations {
  agents: Array<{
    agent_id: string
    agent_name: string
    recommendation_score: number
    reasoning: string
  }>
  workflows: Array<{
    workflow_name: string
    steps: string[]
    confidence: number
    description: string
    estimated_time: number
  }>
  ui_preferences: {
    default_tab: string
    notification_frequency: string
    auto_save_interval: number
    theme_preference: string
    layout_density: string
  }
  proactive_suggestions: Array<{
    type: string
    title: string
    description: string
    confidence: number
  }>
}

interface LearningStats {
  total_users: number
  total_learning_events: number
  total_adaptations: number
  successful_adaptations: number
  adaptation_success_rate: number
  active_adaptation_rules: number
  last_learning_update: string
  events_by_type: Record<string, number>
}

interface UserProfile {
  user_id: string
  preferences: Record<string, any>
  behavior_patterns: Record<string, any>
  skill_level: Record<string, number>
  total_interactions: number
  created_at: string
  updated_at: string
  recent_events: Array<{
    signal_type: string
    timestamp: string
    context: Record<string, any>
  }>
}

export function AdaptiveLearningDashboard() {
  const [recommendations, setRecommendations] = useState<UserRecommendations | null>(null)
  const [learningStats, setLearningStats] = useState<LearningStats | null>(null)
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'recommendations' | 'patterns' | 'adaptations'>('recommendations')

  const loadRecommendations = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:8000/learning/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          context: {
            current_time: new Date().toISOString(),
            page: 'dashboard'
          }
        })
      })

      if (response.ok) {
        const data = await response.json()
        setRecommendations(data)
      }
    } catch (error) {
      console.error('Failed to load recommendations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadLearningStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/learning/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setLearningStats(data)
      }
    } catch (error) {
      console.error('Failed to load learning stats:', error)
    }
  }

  const loadUserProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/learning/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUserProfile(data)
      }
    } catch (error) {
      console.error('Failed to load user profile:', error)
    }
  }

  const provideFeedback = async (itemType: string, itemId: string, feedback: 'positive' | 'negative') => {
    try {
      const response = await fetch('http://localhost:8000/learning/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          feedback_type: feedback,
          context: {
            item_type: itemType,
            item_id: itemId,
            timestamp: new Date().toISOString()
          }
        })
      })

      if (response.ok) {
        toast.success(`Thank you for your ${feedback} feedback!`)
        loadRecommendations() // Refresh recommendations
      }
    } catch (error) {
      console.error('Failed to provide feedback:', error)
      toast.error('Failed to submit feedback')
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100'
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const formatEventType = (eventType: string) => {
    return eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  useEffect(() => {
    loadRecommendations()
    loadLearningStats()
    loadUserProfile()
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Brain className="h-6 w-6 mr-2 text-primary-600" />
          Adaptive Learning Dashboard
        </h2>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => {
              loadRecommendations()
              loadLearningStats()
              loadUserProfile()
            }}
            disabled={isLoading}
            className="btn-primary text-sm"
          >
            {isLoading ? (
              <RefreshCw className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-1" />
            )}
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      {learningStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card bg-gradient-to-r from-blue-50 to-blue-100"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-900">Learning Events</p>
                <p className="text-2xl font-bold text-blue-700">
                  {learningStats.total_learning_events.toLocaleString()}
                </p>
              </div>
              <Activity className="h-8 w-8 text-blue-600" />
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
                <p className="text-sm font-medium text-green-900">Adaptations</p>
                <p className="text-2xl font-bold text-green-700">
                  {learningStats.total_adaptations}
                </p>
              </div>
              <Settings className="h-8 w-8 text-green-600" />
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
                <p className="text-sm font-medium text-purple-900">Success Rate</p>
                <p className="text-2xl font-bold text-purple-700">
                  {learningStats.adaptation_success_rate.toFixed(1)}%
                </p>
              </div>
              <Target className="h-8 w-8 text-purple-600" />
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
                <p className="text-sm font-medium text-orange-900">Active Rules</p>
                <p className="text-2xl font-bold text-orange-700">
                  {learningStats.active_adaptation_rules}
                </p>
              </div>
              <BarChart3 className="h-8 w-8 text-orange-600" />
            </div>
          </motion.div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
        {[
          { id: 'recommendations', label: 'Recommendations', icon: Lightbulb },
          { id: 'patterns', label: 'Learning Patterns', icon: TrendingUp },
          { id: 'adaptations', label: 'Adaptations', icon: Settings }
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
        {activeTab === 'recommendations' && recommendations && (
          <motion.div
            key="recommendations"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Agent Recommendations */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <User className="h-5 w-5 mr-2 text-primary-600" />
                Recommended Agents
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recommendations.agents.map((agent, index) => (
                  <motion.div
                    key={agent.agent_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{agent.agent_name}</h4>
                      <span className={`px-2 py-1 text-xs rounded-full ${getScoreColor(agent.recommendation_score)}`}>
                        {Math.round(agent.recommendation_score * 100)}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{agent.reasoning}</p>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => provideFeedback('agent', agent.agent_id, 'positive')}
                        className="flex items-center text-sm text-green-600 hover:text-green-700"
                      >
                        <ThumbsUp className="h-3 w-3 mr-1" />
                        Helpful
                      </button>
                      <button
                        onClick={() => provideFeedback('agent', agent.agent_id, 'negative')}
                        className="flex items-center text-sm text-red-600 hover:text-red-700"
                      >
                        <ThumbsDown className="h-3 w-3 mr-1" />
                        Not Helpful
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Workflow Recommendations */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <ArrowRight className="h-5 w-5 mr-2 text-primary-600" />
                Suggested Workflows
              </h3>
              <div className="space-y-4">
                {recommendations.workflows.map((workflow, index) => (
                  <motion.div
                    key={workflow.workflow_name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{workflow.workflow_name}</h4>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${getScoreColor(workflow.confidence)}`}>
                          {Math.round(workflow.confidence * 100)}%
                        </span>
                        <span className="text-xs text-gray-500 flex items-center">
                          <Clock className="h-3 w-3 mr-1" />
                          {workflow.estimated_time}min
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{workflow.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {workflow.steps.map((step, stepIndex) => (
                        <span
                          key={stepIndex}
                          className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                        >
                          {step}
                        </span>
                      ))}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Proactive Suggestions */}
            {recommendations.proactive_suggestions.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Lightbulb className="h-5 w-5 mr-2 text-primary-600" />
                  Proactive Suggestions
                </h3>
                <div className="space-y-3">
                  {recommendations.proactive_suggestions.map((suggestion, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg"
                    >
                      <Zap className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="font-medium text-blue-900">{suggestion.title}</h4>
                        <p className="text-sm text-blue-700">{suggestion.description}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs rounded-full ${getScoreColor(suggestion.confidence)}`}>
                        {Math.round(suggestion.confidence * 100)}%
                      </span>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === 'patterns' && userProfile && (
          <motion.div
            key="patterns"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Usage Patterns */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-primary-600" />
                Your Learning Patterns
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Preferences */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Preferences</h4>
                  <div className="space-y-2">
                    {Object.entries(userProfile.preferences).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-gray-600">{key.replace(/_/g, ' ')}:</span>
                        <span className="text-gray-900">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Skill Levels */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Skill Levels</h4>
                  <div className="space-y-2">
                    {Object.entries(userProfile.skill_level).map(([skill, level]) => (
                      <div key={skill}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-600">{skill.replace(/_/g, ' ')}:</span>
                          <span className="text-gray-900">{Math.round(level * 100)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full"
                            style={{ width: `${level * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Calendar className="h-5 w-5 mr-2 text-primary-600" />
                Recent Learning Events
              </h3>
              <div className="space-y-3">
                {userProfile.recent_events.map((event, index) => (
                  <div
                    key={index}
                    className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg"
                  >
                    <div className="w-2 h-2 bg-primary-600 rounded-full" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900">
                          {formatEventType(event.signal_type)}
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(event.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                      {Object.keys(event.context).length > 0 && (
                        <div className="text-sm text-gray-600 mt-1">
                          {Object.entries(event.context).slice(0, 2).map(([key, value]) => (
                            <span key={key} className="mr-3">
                              {key}: {String(value)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'adaptations' && learningStats && (
          <motion.div
            key="adaptations"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Event Distribution */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <BarChart3 className="h-5 w-5 mr-2 text-primary-600" />
                Learning Event Distribution
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(learningStats.events_by_type).map(([eventType, count]) => (
                  <div key={eventType} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                    <span className="text-sm text-gray-700">{formatEventType(eventType)}</span>
                    <span className="font-medium text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* System Performance */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Target className="h-5 w-5 mr-2 text-primary-600" />
                Adaptation Performance
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-green-700">
                    {learningStats.successful_adaptations}
                  </div>
                  <div className="text-sm text-green-600">Successful</div>
                </div>
                
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <AlertCircle className="h-8 w-8 text-red-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-red-700">
                    {learningStats.total_adaptations - learningStats.successful_adaptations}
                  </div>
                  <div className="text-sm text-red-600">Failed</div>
                </div>
                
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <Star className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-blue-700">
                    {learningStats.adaptation_success_rate.toFixed(1)}%
                  </div>
                  <div className="text-sm text-blue-600">Success Rate</div>
                </div>
              </div>
            </div>

            {/* System Status */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Eye className="h-5 w-5 mr-2 text-primary-600" />
                System Status
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Learning System</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Active Rules:</span>
                      <span className="text-gray-900">{learningStats.active_adaptation_rules}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Total Users:</span>
                      <span className="text-gray-900">{learningStats.total_users}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Last Update:</span>
                      <span className="text-gray-900">
                        {new Date(learningStats.last_learning_update).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Performance Metrics</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Events per User:</span>
                      <span className="text-gray-900">
                        {Math.round(learningStats.total_learning_events / Math.max(learningStats.total_users, 1))}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Adaptation Rate:</span>
                      <span className="text-gray-900">
                        {((learningStats.total_adaptations / Math.max(learningStats.total_learning_events, 1)) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
} 