'use client'

import { motion } from 'framer-motion'
import { CheckCircle, XCircle, AlertCircle, Loader2, Server, Database, Zap } from 'lucide-react'

interface SystemStatusProps {
  status: any
  isLoading: boolean
}

export function SystemStatus({ status, isLoading }: SystemStatusProps) {
  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
          <span className="ml-3 text-gray-600">Loading system status...</span>
        </div>
      </div>
    )
  }

  if (!status || status.status !== 'success') {
    return (
      <div className="card border-red-200 bg-red-50">
        <div className="flex items-center">
          <XCircle className="h-6 w-6 text-red-500" />
          <div className="ml-3">
            <h3 className="text-lg font-semibold text-red-900">System Offline</h3>
            <p className="text-red-700">Unable to connect to backend services</p>
          </div>
        </div>
      </div>
    )
  }

  const systemHealth = status.system?.status === 'running'
  const agentHealth = status.agents?.total_agents >= 0
  const ragHealth = status.rag_pipeline?.status === 'initialized'

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Server className="h-5 w-5 mr-2 text-primary-600" />
          System Status
        </h3>
        <div className="flex items-center">
          <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
          <span className="text-sm font-medium text-green-700">All Systems Operational</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Backend Status */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center p-3 bg-gray-50 rounded-lg"
        >
          <div className={`p-2 rounded-full ${systemHealth ? 'bg-green-100' : 'bg-red-100'}`}>
            {systemHealth ? (
              <CheckCircle className="h-4 w-4 text-green-600" />
            ) : (
              <XCircle className="h-4 w-4 text-red-600" />
            )}
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-900">Backend API</p>
            <p className="text-xs text-gray-600">
              {systemHealth ? 'Online' : 'Offline'}
            </p>
          </div>
        </motion.div>

        {/* Agents Status */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex items-center p-3 bg-gray-50 rounded-lg"
        >
          <div className={`p-2 rounded-full ${agentHealth ? 'bg-green-100' : 'bg-yellow-100'}`}>
            {agentHealth ? (
              <CheckCircle className="h-4 w-4 text-green-600" />
            ) : (
              <AlertCircle className="h-4 w-4 text-yellow-600" />
            )}
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-900">AI Agents</p>
            <p className="text-xs text-gray-600">
              {status.agents?.total_agents || 0} Available
            </p>
          </div>
        </motion.div>

        {/* RAG Pipeline Status */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex items-center p-3 bg-gray-50 rounded-lg"
        >
          <div className={`p-2 rounded-full ${ragHealth ? 'bg-green-100' : 'bg-yellow-100'}`}>
            {ragHealth ? (
              <CheckCircle className="h-4 w-4 text-green-600" />
            ) : (
              <AlertCircle className="h-4 w-4 text-yellow-600" />
            )}
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-900">RAG Pipeline</p>
            <p className="text-xs text-gray-600">
              {status.rag_pipeline?.total_documents || 0} Documents
            </p>
          </div>
        </motion.div>
      </div>

      {/* Additional Info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Last Updated: {new Date().toLocaleTimeString()}</span>
          <span>Version: {status.system?.version || '1.3.0'}</span>
        </div>
      </div>
    </div>
  )
}
