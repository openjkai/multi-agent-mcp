'use client'

import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

interface Agent {
  id: string
  name: string
  type: string
  description: string
  capabilities: string[]
  icon: LucideIcon
  color: string
}

interface AgentCardProps {
  agent: Agent
}

export function AgentCard({ agent }: AgentCardProps) {
  const Icon = agent.icon

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="card hover:shadow-lg transition-shadow duration-200"
    >
      <div className="flex items-start space-x-4">
        <div className={`p-3 rounded-lg ${agent.color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 mb-1">{agent.name}</h4>
          <p className="text-sm text-gray-600 mb-3">{agent.description}</p>
          <div className="space-y-1">
            {agent.capabilities.map((capability, index) => (
              <span
                key={index}
                className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full mr-1 mb-1"
              >
                {capability}
              </span>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
