'use client'

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Activity, 
  Wifi, 
  WifiOff,
  Users, 
  MessageSquare,
  TrendingUp,
  Server,
  AlertCircle,
  CheckCircle,
  Clock,
  BarChart3,
  Zap,
  RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'

interface RealTimeEvent {
  id: string
  type: string
  data: any
  timestamp: string
  room?: string
}

interface ConnectionStats {
  total: number
  users: number
  rooms: Record<string, number>
}

interface SystemMetrics {
  connections: ConnectionStats
  events: {
    sent: number
    failed: number
    success_rate: number
  }
  performance: {
    uptime_seconds: number
    events_per_second: number
    history_size: number
  }
}

interface AgentStatus {
  agent_id: string
  name: string
  status: string
  last_activity: string
  performance: {
    queries: number
    success_rate: number
    avg_response_time: number
  }
}

export function RealTimeMonitor() {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const [events, setEvents] = useState<RealTimeEvent[]>([])
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>([])
  const [activeRoom, setActiveRoom] = useState<string>('general')
  const [eventFilter, setEventFilter] = useState<string>('all')
  
  const websocketRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const eventTypes = [
    { value: 'all', label: 'All Events', color: 'text-gray-600' },
    { value: 'agent_status_update', label: 'Agent Status', color: 'text-blue-600' },
    { value: 'workflow_progress', label: 'Workflows', color: 'text-green-600' },
    { value: 'document_processed', label: 'Documents', color: 'text-purple-600' },
    { value: 'chat_message', label: 'Chat', color: 'text-orange-600' },
    { value: 'system_alert', label: 'System', color: 'text-red-600' },
    { value: 'performance_metrics', label: 'Metrics', color: 'text-indigo-600' }
  ]

  const rooms = [
    { value: 'general', label: 'General' },
    { value: 'agents', label: 'Agents' },
    { value: 'workflows', label: 'Workflows' },
    { value: 'documents', label: 'Documents' }
  ]

  const connectWebSocket = useCallback(() => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    setConnectionStatus('connecting')
    
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.hostname}:8000/ws`
      
      websocketRef.current = new WebSocket(wsUrl)
      
      websocketRef.current.onopen = () => {
        setIsConnected(true)
        setConnectionStatus('connected')
        reconnectAttempts.current = 0
        toast.success('Connected to real-time monitoring')
        
        // Join the active room
        if (activeRoom) {
          sendMessage({ type: 'join_room', room: activeRoom })
        }
        
        // Request initial stats
        sendMessage({ type: 'get_stats' })
      }
      
      websocketRef.current.onmessage = (event) => {
        try {
          const data: RealTimeEvent = JSON.parse(event.data)
          handleIncomingEvent(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
      
      websocketRef.current.onclose = () => {
        setIsConnected(false)
        setConnectionStatus('disconnected')
        
        // Attempt to reconnect
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Reconnection attempt ${reconnectAttempts.current}`)
            connectWebSocket()
          }, delay)
        } else {
          setConnectionStatus('error')
          toast.error('Lost connection to real-time monitoring')
        }
      }
      
      websocketRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionStatus('error')
      }
      
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      setConnectionStatus('error')
    }
  }, [activeRoom])

  const sendMessage = useCallback((message: any) => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify(message))
    }
  }, [])

  const handleIncomingEvent = useCallback((event: RealTimeEvent) => {
    // Add to events list
    setEvents(prev => {
      const newEvents = [event, ...prev].slice(0, 100) // Keep last 100 events
      return newEvents
    })
    
    // Handle specific event types
    switch (event.type) {
      case 'agent_status_update':
        setAgentStatuses(prev => {
          const updated = [...prev]
          const index = updated.findIndex(agent => agent.agent_id === event.data.agent_id)
          if (index >= 0) {
            updated[index] = { ...updated[index], ...event.data.status }
          } else {
            updated.push({
              agent_id: event.data.agent_id,
              name: event.data.status.name || event.data.agent_id,
              status: event.data.status.status || 'active',
              last_activity: event.data.status.last_activity || new Date().toISOString(),
              performance: event.data.status.performance || {
                queries: 0,
                success_rate: 0,
                avg_response_time: 0
              }
            })
          }
          return updated
        })
        break
        
      case 'performance_metrics':
        setSystemMetrics(event.data)
        break
        
      case 'system_alert':
        const level = event.data.level || 'info'
        if (level === 'error') {
          toast.error(event.data.message)
        } else if (level === 'warning') {
          toast((t) => (
            <div className="flex items-center">
              <AlertCircle className="h-4 w-4 text-yellow-500 mr-2" />
              {event.data.message}
            </div>
          ))
        }
        break
    }
  }, [])

  const changeRoom = useCallback((newRoom: string) => {
    if (activeRoom && websocketRef.current?.readyState === WebSocket.OPEN) {
      sendMessage({ type: 'leave_room', room: activeRoom })
    }
    
    setActiveRoom(newRoom)
    
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      sendMessage({ type: 'join_room', room: newRoom })
    }
  }, [activeRoom, sendMessage])

  const filteredEvents = events.filter(event => 
    eventFilter === 'all' || event.type === eventFilter
  )

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'agent_status_update':
        return <Activity className="h-4 w-4 text-blue-500" />
      case 'workflow_progress':
        return <TrendingUp className="h-4 w-4 text-green-500" />
      case 'document_processed':
        return <CheckCircle className="h-4 w-4 text-purple-500" />
      case 'chat_message':
        return <MessageSquare className="h-4 w-4 text-orange-500" />
      case 'system_alert':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'performance_metrics':
        return <BarChart3 className="h-4 w-4 text-indigo-500" />
      default:
        return <Zap className="h-4 w-4 text-gray-500" />
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  useEffect(() => {
    connectWebSocket()
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (websocketRef.current) {
        websocketRef.current.close()
      }
    }
  }, [connectWebSocket])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Activity className="h-6 w-6 mr-2 text-primary-600" />
          Real-Time Monitor
        </h2>
        
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <Wifi className="h-5 w-5 text-green-500" />
            ) : (
              <WifiOff className="h-5 w-5 text-red-500" />
            )}
            <span className={`text-sm font-medium ${
              isConnected ? 'text-green-700' : 'text-red-700'
            }`}>
              {connectionStatus.charAt(0).toUpperCase() + connectionStatus.slice(1)}
            </span>
          </div>
          
          <button
            onClick={connectWebSocket}
            disabled={connectionStatus === 'connecting'}
            className="btn-secondary text-sm"
          >
            {connectionStatus === 'connecting' ? (
              <RefreshCw className="h-4 w-4 animate-spin mr-1" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-1" />
            )}
            Reconnect
          </button>
        </div>
      </div>

      {/* System Metrics */}
      {systemMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card bg-gradient-to-r from-blue-50 to-blue-100"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-900">Active Connections</p>
                <p className="text-2xl font-bold text-blue-700">
                  {systemMetrics.connections.total}
                </p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
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
                <p className="text-sm font-medium text-green-900">Events/sec</p>
                <p className="text-2xl font-bold text-green-700">
                  {systemMetrics.performance.events_per_second.toFixed(1)}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
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
                  {systemMetrics.events.success_rate.toFixed(1)}%
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-purple-600" />
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
                <p className="text-sm font-medium text-orange-900">Uptime</p>
                <p className="text-lg font-bold text-orange-700">
                  {formatUptime(systemMetrics.performance.uptime_seconds)}
                </p>
              </div>
              <Clock className="h-8 w-8 text-orange-600" />
            </div>
          </motion.div>
        </div>
      )}

      {/* Agent Status */}
      {agentStatuses.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agentStatuses.map((agent) => (
              <div key={agent.agent_id} className="border border-gray-200 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{agent.name}</h4>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    agent.status === 'active' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {agent.status}
                  </span>
                </div>
                <div className="space-y-1 text-sm text-gray-600">
                  <div>Queries: {agent.performance.queries}</div>
                  <div>Success: {agent.performance.success_rate.toFixed(1)}%</div>
                  <div>Avg Time: {agent.performance.avg_response_time.toFixed(2)}s</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Event Stream */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Live Event Stream</h3>
              
              <div className="flex items-center space-x-2">
                {/* Event Filter */}
                <select
                  value={eventFilter}
                  onChange={(e) => setEventFilter(e.target.value)}
                  className="text-sm border border-gray-300 rounded px-2 py-1"
                >
                  {eventTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
                
                {/* Room Selector */}
                <select
                  value={activeRoom}
                  onChange={(e) => changeRoom(e.target.value)}
                  className="text-sm border border-gray-300 rounded px-2 py-1"
                >
                  {rooms.map(room => (
                    <option key={room.value} value={room.value}>
                      {room.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="h-96 overflow-y-auto space-y-2 scrollbar-thin">
              <AnimatePresence initial={false}>
                {filteredEvents.map((event) => (
                  <motion.div
                    key={event.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-1">
                        {getEventIcon(event.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">
                            {event.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </p>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(event.timestamp)}
                          </span>
                        </div>
                        <div className="mt-1">
                          <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                            {JSON.stringify(event.data, null, 2)}
                          </pre>
                        </div>
                        {event.room && (
                          <div className="mt-1">
                            <span className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
                              Room: {event.room}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {filteredEvents.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Activity className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>No events to display</p>
                  <p className="text-sm">Events will appear here in real-time</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Connection Info */}
        <div className="space-y-4">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Connection Info</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Status:</span>
                <span className={`text-sm font-medium ${
                  isConnected ? 'text-green-700' : 'text-red-700'
                }`}>
                  {connectionStatus}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Room:</span>
                <span className="text-sm font-medium text-gray-900">{activeRoom}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Events:</span>
                <span className="text-sm font-medium text-gray-900">{events.length}</span>
              </div>
              
              {systemMetrics && (
                <>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Users Online:</span>
                    <span className="text-sm font-medium text-gray-900">
                      {systemMetrics.connections.users}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Total Connections:</span>
                    <span className="text-sm font-medium text-gray-900">
                      {systemMetrics.connections.total}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Room Stats */}
          {systemMetrics?.connections.rooms && Object.keys(systemMetrics.connections.rooms).length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Room Activity</h3>
              <div className="space-y-2">
                {Object.entries(systemMetrics.connections.rooms).map(([room, count]) => (
                  <div key={room} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{room}:</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-900">{count}</span>
                      <div className="w-12 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-primary-600 h-2 rounded-full"
                          style={{ 
                            width: `${Math.min((count / Math.max(systemMetrics.connections.total, 1)) * 100, 100)}%` 
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 