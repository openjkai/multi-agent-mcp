'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Loader2, Bot, User } from 'lucide-react'
import toast from 'react-hot-toast'

interface Message {
  id: string
  type: 'user' | 'agent'
  content: string
  timestamp: Date
  agentName?: string
}

export function QueryInterface() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: query,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setQuery('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      })

      const data = await response.json()

      if (data.status === 'success') {
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'agent',
          content: data.result.response.response,
          timestamp: new Date(),
          agentName: data.result.agent_name
        }
        setMessages(prev => [...prev, agentMessage])
      } else {
        toast.error(data.error || 'Failed to get response')
      }
    } catch (error) {
      console.error('Query error:', error)
      toast.error('Failed to connect to backend')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Chat with AI Agents</h3>
      
      {/* Messages */}
      <div className="h-64 overflow-y-auto mb-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <Bot className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>Start a conversation with our AI agents</p>
          </div>
        ) : (
          messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-2 max-w-xs lg:max-w-md ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`p-2 rounded-full ${message.type === 'user' ? 'bg-primary-600' : 'bg-gray-200'}`}>
                  {message.type === 'user' ? (
                    <User className="h-4 w-4 text-white" />
                  ) : (
                    <Bot className="h-4 w-4 text-gray-600" />
                  )}
                </div>
                <div className={`rounded-lg px-3 py-2 ${message.type === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
                  <p className="text-sm">{message.content}</p>
                  {message.agentName && (
                    <p className="text-xs opacity-75 mt-1">by {message.agentName}</p>
                  )}
                </div>
              </div>
            </motion.div>
          ))
        )}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="flex items-start space-x-2">
              <div className="p-2 rounded-full bg-gray-200">
                <Bot className="h-4 w-4 text-gray-600" />
              </div>
              <div className="rounded-lg px-3 py-2 bg-gray-100">
                <div className="flex items-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask our AI agents anything..."
          className="input-field flex-1"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </button>
      </form>
    </div>
  )
}
