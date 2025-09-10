'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Activity, 
  Clock, 
  CheckCircle, 
  XCircle, 
  TrendingUp, 
  Users,
  BarChart3,
  RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'

interface AgentMetric {
  agent_id: string
  name: string
  capabilities: string[]
  is_active: boolean
  metrics: {
    total_queries: number
    successful_queries: number
    failed_queries: number
    average_response_time: number
    last_query_time: string | null
    uptime: string
  }
}

interface SystemMetrics {
  total_agents: number
  active_agents: number
  total_queries_processed: number
  successful_queries: number
  failed_queries: number
  system_uptime: string
  registered_agents: AgentMetric[]
}

export function AgentMetrics() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/system/status')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      if (data.status === 'success') {
        setMetrics(data.agents)
        setLastUpdated(new Date())
      } else {
        throw new Error(data.error || 'Failed to fetch metrics')
      }
    } catch (error) {
      console.error('Failed to fetch agent metrics:', error)
      toast.error('Failed to fetch agent metrics')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchMetrics()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(fetchMetrics, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [autoRefresh])

  const calculateSuccessRate = (successful: number, total: number): number => {
    return total > 0 ? (successful / total) * 100 : 0
  }

  const formatUptime = (uptime: string): string => {
    // Parse uptime string and format it nicely
    if (!uptime) return 'Unknown'
    
    try {
      // Assuming uptime is in format like "1:23:45.123456"
      const parts = uptime.split(':')
      if (parts.length >= 3) {
        const hours = parseInt(parts[0])
        const minutes = parseInt(parts[1])
        
        if (hours > 0) {
          return `${hours}h ${minutes}m`
        } else {
          return `${minutes}m`
        }
      }
      return uptime
    } catch {
      return uptime
    }
  }

  const formatResponseTime = (time: number): string => {
    return `${time.toFixed(3)}s`
  }

  const getAgentStatusColor = (agent: AgentMetric): string => {
    if (!agent.is_active) return 'text-gray-500'
    
    const successRate = calculateSuccessRate(agent.metrics.successful_queries, agent.metrics.total_queries)
    if (successRate >= 95) return 'text-green-600'
    if (successRate >= 80) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getAgentStatusIcon = (agent: AgentMetric) => {
    if (!agent.is_active) {
      return <XCircle className="h-4 w-4 text-gray-500" />
    }
    
    const successRate = calculateSuccessRate(agent.metrics.successful_queries, agent.metrics.total_queries)
    if (successRate >= 95) {
      return <CheckCircle className="h-4 w-4 text-green-600" />
    }
    if (successRate >= 80) {
      return <Activity className="h-4 w-4 text-yellow-600" />
    }
    return <XCircle className="h-4 w-4 text-red-600" />
  }

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="h-8 w-8 animate-spin text-primary-600" />
          <span className="ml-3 text-gray-600">Loading agent metrics...</span>
        </div>
      </div>
    )
  }

  if (!metrics) {
    return (
      <div className="card border-red-200 bg-red-50">
        <div className="flex items-center">
          <XCircle className="h-6 w-6 text-red-500" />
          <div className="ml-3">
            <h3 className="text-lg font-semibold text-red-900">Metrics Unavailable</h3>
            <p className="text-red-700">Unable to load agent performance metrics</p>
          </div>
        </div>
      </div>
    )
  }

  const overallSuccessRate = calculateSuccessRate(metrics.successful_queries, metrics.total_queries_processed)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <BarChart3 className="h-6 w-6 mr-2 text-primary-600" />
          Agent Performance Metrics
        </h2>
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-600">Auto-refresh</span>
          </label>
          <button
            onClick={fetchMetrics}
            className="btn-secondary text-sm"
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-r from-blue-50 to-blue-100"
        >
          <div className="flex items-center">
            <Users className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-blue-900">Active Agents</p>
              <p className="text-2xl font-bold text-blue-700">
                {metrics.active_agents}/{metrics.total_agents}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card bg-gradient-to-r from-green-50 to-green-100"
        >
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-green-900">Success Rate</p>
              <p className="text-2xl font-bold text-green-700">
                {overallSuccessRate.toFixed(1)}%
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card bg-gradient-to-r from-purple-50 to-purple-100"
        >
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-purple-900">Total Queries</p>
              <p className="text-2xl font-bold text-purple-700">
                {metrics.total_queries_processed}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card bg-gradient-to-r from-orange-50 to-orange-100"
        >
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-orange-900">System Uptime</p>
              <p className="text-lg font-bold text-orange-700">
                {formatUptime(metrics.system_uptime)}
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Individual Agent Metrics */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Individual Agent Performance</h3>
        
        <div className="space-y-4">
          {metrics.registered_agents.map((agent, index) => (
            <motion.div
              key={agent.agent_id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  {getAgentStatusIcon(agent)}
                  <div>
                    <h4 className="font-semibold text-gray-900">{agent.name}</h4>
                    <p className="text-sm text-gray-600">{agent.agent_id}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-medium ${getAgentStatusColor(agent)}`}>
                    {agent.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                <div>
                  <p className="text-xs text-gray-500">Queries Processed</p>
                  <p className="font-semibold">{agent.metrics.total_queries}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Success Rate</p>
                  <p className="font-semibold">
                    {calculateSuccessRate(agent.metrics.successful_queries, agent.metrics.total_queries).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Avg Response Time</p>
                  <p className="font-semibold">{formatResponseTime(agent.metrics.average_response_time)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Uptime</p>
                  <p className="font-semibold">{formatUptime(agent.metrics.uptime)}</p>
                </div>
              </div>

              <div className="flex flex-wrap gap-1">
                {agent.capabilities.map((capability) => (
                  <span
                    key={capability}
                    className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full"
                  >
                    {capability}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Last Updated */}
      {lastUpdated && (
        <div className="text-center text-sm text-gray-500">
          Last updated: {lastUpdated.toLocaleTimeString()}
        </div>
      )}
    </div>
  )
} 