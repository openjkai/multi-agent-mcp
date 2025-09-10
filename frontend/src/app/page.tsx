'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, 
  FileText, 
  Code, 
  Globe, 
  MessageCircle, 
  Upload,
  Search,
  Activity,
  Zap,
  BarChart3,
  Eye,
  Settings
} from 'lucide-react'
import toast from 'react-hot-toast'
import { AgentCard } from '@/components/AgentCard'
import { QueryInterface } from '@/components/QueryInterface'
import { SystemStatus } from '@/components/SystemStatus'
import { DocumentUpload } from '@/components/DocumentUpload'
import { AgentMetrics } from '@/components/AgentMetrics'
import { DocumentViewer } from '@/components/DocumentViewer'

const agents = [
  {
    id: 'docs-agent-001',
    name: 'Document Analysis Agent',
    type: 'docs',
    description: 'Specialized in document processing and Q&A',
    capabilities: ['PDF Processing', 'Text Analysis', 'Document Q&A'],
    icon: FileText,
    color: 'bg-blue-500'
  },
  {
    id: 'code-agent-001',
    name: 'Code Assistant Agent',
    type: 'code',
    description: 'Code explanation, refactoring, and generation',
    capabilities: ['Code Analysis', 'Refactoring', 'Code Generation'],
    icon: Code,
    color: 'bg-green-500'
  },
  {
    id: 'web-agent-001',
    name: 'Web Search Agent',
    type: 'web',
    description: 'Real-time web information retrieval',
    capabilities: ['Web Search', 'News Fetching', 'Fact Checking'],
    icon: Globe,
    color: 'bg-purple-500'
  },
  {
    id: 'chat-agent-001',
    name: 'General Chat Agent',
    type: 'chat',
    description: 'General conversation and task coordination',
    capabilities: ['Conversation', 'Task Coordination', 'Agent Orchestration'],
    icon: MessageCircle,
    color: 'bg-orange-500'
  }
]

const tabs = [
  { id: 'chat', name: 'Chat', icon: MessageCircle, description: 'Interact with AI agents' },
  { id: 'documents', name: 'Documents', icon: FileText, description: 'Manage your document library' },
  { id: 'metrics', name: 'Metrics', icon: BarChart3, description: 'Monitor agent performance' },
  { id: 'agents', name: 'Agents', icon: Zap, description: 'View available agents' }
]

export default function Home() {
  const [systemStatus, setSystemStatus] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('chat')

  useEffect(() => {
    fetchSystemStatus()
  }, [])

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/system/status')
      const data = await response.json()
      setSystemStatus(data)
    } catch (error) {
      console.error('Failed to fetch system status:', error)
      toast.error('Failed to connect to backend')
    } finally {
      setIsLoading(false)
    }
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'chat':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Query Interface */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              className="lg:col-span-2"
            >
              <QueryInterface />
            </motion.div>

            {/* Document Upload */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <DocumentUpload />
            </motion.div>
          </div>
        )
      
      case 'documents':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <DocumentViewer />
          </motion.div>
        )
      
      case 'metrics':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <AgentMetrics />
          </motion.div>
        )
      
      case 'agents':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <Zap className="h-6 w-6 mr-2 text-primary-600" />
                Available Agents
              </h3>
              <p className="text-gray-600">
                Specialized AI agents ready to assist with your tasks
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {agents.map((agent, index) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                >
                  <AgentCard agent={agent} />
                </motion.div>
              ))}
            </div>

            {/* Agent Status Summary */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="mt-8"
            >
              <div className="card">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Agent Status Summary</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{agents.length}</div>
                    <div className="text-sm text-gray-600">Total Agents</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{agents.length}</div>
                    <div className="text-sm text-gray-600">Active Agents</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {agents.reduce((acc, agent) => acc + agent.capabilities.length, 0)}
                    </div>
                    <div className="text-sm text-gray-600">Total Capabilities</div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )
      
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-600 rounded-lg">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Multi-Agent MCP</h1>
                <p className="text-sm text-gray-600">AI Knowledge Hub v0.2.0</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Activity className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-600">
                {systemStatus?.status === 'success' ? 'System Online' : 'System Offline'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Intelligent Multi-Agent System
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Harness the power of AI agents working together through MCP protocol, 
            enhanced with RAG capabilities and real-time collaboration.
          </p>
        </motion.div>

        {/* System Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mb-8"
        >
          <SystemStatus status={systemStatus} isLoading={isLoading} />
        </motion.div>

        {/* Navigation Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-8"
        >
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === tab.id
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className={`mr-2 h-5 w-5 ${
                      activeTab === tab.id ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'
                    }`} />
                    {tab.name}
                  </button>
                )
              })}
            </nav>
          </div>
          
          {/* Tab Description */}
          <div className="mt-4">
            <p className="text-gray-600">
              {tabs.find(tab => tab.id === activeTab)?.description}
            </p>
          </div>
        </motion.div>

        {/* Tab Content */}
        <div className="min-h-[600px]">
          {renderTabContent()}
        </div>
      </main>
    </div>
  )
}
